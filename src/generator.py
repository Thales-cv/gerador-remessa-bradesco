import pandas as pd
from datetime import datetime
from .cnab_definitions import (
    HEADER_ARQUIVO, HEADER_LOTE, SEGMENTO_A, SEGMENTO_B, 
    TRAILER_LOTE, TRAILER_ARQUIVO, PadType
)
from .validators import (
    clean_non_digits, format_value, sanitize_text, 
    determine_inscription_type, validate_date_not_past
)

class CNABGenerator:
    def __init__(self, nsa: int, empresa_data: dict):
        self.nsa = nsa
        # Sanitize empresa data on init
        self.empresa_data = {k: sanitize_text(str(v)) for k, v in empresa_data.items()}
        # Except CNPJ/Convenio which are numbers
        self.empresa_data['cnpj'] = clean_non_digits(empresa_data['cnpj'])
        self.empresa_data['convenio'] = clean_non_digits(empresa_data['convenio'])
        self.empresa_data['agencia'] = clean_non_digits(empresa_data['agencia'])
        self.empresa_data['conta'] = clean_non_digits(empresa_data['conta'])
        self.empresa_data['pix_flag'] = empresa_data.get('pix_flag', '')
        
        self.lines = []
        self.lotes_count = 0
        self.registros_count = 0 # Total lines in file
        self.total_value_file = 0.0
        
    def _format_field(self, value, spec):
        start, end, pad_type, default = spec
        length = end - start + 1
        
        val_str = str(value) if value is not None and value != "" else default
        
        # Enforce ANSI safe chars? already handled by generate_line input hopefully
        
        if len(val_str) > length:
            val_str = val_str[:length]
            
        if pad_type == PadType.ZERO_LEFT:
            return val_str.zfill(length)
        else:
            return val_str.ljust(length)

    def _generate_line(self, layout: dict, data: dict):
        # Sort by start position
        sorted_fields = sorted(layout.items(), key=lambda item: item[1][0])
        
        line = ""
        current_pos = 1
        
        for field_name, spec in sorted_fields:
            start, end, _, _ = spec
            if start != current_pos:
                line += " " * (start - current_pos)
            
            value = data.get(field_name, None)
            formatted = self._format_field(value, spec)
            line += formatted
            current_pos = end + 1
            
        # STRICT 240 Enforcement
        if len(line) < 240:
            line = line.ljust(240)
        elif len(line) > 240:
            line = line[:240]
            
        return line

    def generate(self, df: pd.DataFrame) -> bytes:
        # Returns BYTES encoded in cp1252
        self.lines = []
        self.registros_count = 0 # File header is 0? No, File header is first line.
        self.lotes_count = 0
        self.total_value_file = 0.0
        
        # 1. Header Arquivo
        header_arq_data = {
            "numero_inscricao": self.empresa_data['cnpj'],
            "tipo_inscricao": "2", # Assume PJ
            "convenio": self.empresa_data['convenio'],
            "agencia": self.empresa_data['agencia'],
            "conta": self.empresa_data['conta'],
            "nome_empresa": self.empresa_data['nome'],
            "data_geracao": datetime.now().strftime("%d%m%Y"),
            "hora_geracao": datetime.now().strftime("%H%M%S"),
            "nsa": str(self.nsa),
            "reservado_banco": "PIX" if "PIX" in self.empresa_data['pix_flag'] else ""
        }
        self.lines.append(self._generate_line(HEADER_ARQUIVO, header_arq_data))
        self.registros_count += 1
        
        # Group Determine Payment Type
        # Logic: 
        # If Key Type != Empty -> Likely Pix (unless it's DOC/TED)
        # We need a robust Classifier.
        
        # Let's use the explicit "TIPO_CHAVE_PIX" or "CHAVE_PIX" presence.
        def classify_payment(row):
            pix_k = str(row.get('CHAVE_PIX', '')).strip()
            # If there is a Pix Key, it's Pix.
            if pix_k and pix_k.lower() != 'nan':
                 return 'PIX'
            else:
                 return 'TED' # Default to TED/DOC/CC

        df['payment_type'] = df.apply(classify_payment, axis=1)
        
        # Group by Payment Type (Pix vs Others) because they need different Lotes (45 vs 01/41)
        # Actually, separate batches for Pix (45) and others.
        
        for p_type, group in df.groupby('payment_type'):
            self.lotes_count += 1
            lote_seq = self.lotes_count
            
            is_pix = (p_type == 'PIX')
            forma_lancamento = "45" if is_pix else "41" # 41=TED as default for Other
            # If same bank (237) -> 01 (CC).
            # But let's stick to 41 for simplicity unless user requested bank check.
            # User requirement: "Alerta se houver bancos com códigos inválidos" implies we should handle bank codes.
            # If COD_BANCO == 237 -> 01 (CC). Else -> 41 (TED).
            # Let's refine forma_lancamento row by row needed? 
            # No, Batch Header defines Forma Lancamento.
            # We MUST split batches by (Pix/TED) AND (Same Bank vs Other Bank)?
            # Bradesco allows mixed? Usually not. Forma Lancamento is in Header Lote.
            # So we must sub-group by (Pix) vs (Bradesco CC) vs (TED).
            
            # Sub-grouping logic
            sub_groups = {}
            for idx, row in group.iterrows():
                banco = str(row['COD_BANCO']).strip()
                if is_pix:
                    key = 'PIX'
                elif banco == '237':
                    key = 'CC'
                else:
                    key = 'TED'
                
                if key not in sub_groups: sub_groups[key] = []
                sub_groups[key].append(row)
                
            for key_type, rows in sub_groups.items():
                if key_type == 'PIX': forma = '45'
                elif key_type == 'CC': forma = '01'
                else: forma = '41'
                
                layout_lote = "045" if forma == '45' else "040"
                
                header_lote_data = {
                    "lote": str(self.lotes_count), # Wait, lotes_count needs to increment for each sub-group
                    "forma_lancamento": forma,
                    "layout_lote": layout_lote,
                    "numero_inscricao": self.empresa_data['cnpj'],
                    "tipo_inscricao": "2",
                    "convenio": self.empresa_data['convenio'],
                    "agencia": self.empresa_data['agencia'],
                    "conta": self.empresa_data['conta'],
                    "nome_empresa": self.empresa_data['nome']
                }
                
                # Careful with Lote numbering if I loop inside
                # Actually I should increment lotes_count here
                if key_type != list(sub_groups.keys())[0]: # If verified
                     # This logic is messy. Let's just flatten the loop logic.
                     pass 
                     
                # Correct Loop: Group by tuple (is_pix, is_bradesco) -> determine forma.
            
        # Re-doing the loop Structure
        # 1. Annotate Forma Lancamento on DF
        def get_forma(row):
            pix_k = str(row.get('CHAVE_PIX', '')).strip()
            if pix_k and pix_k.lower() != 'nan': return '45' # Pix
            banco = clean_non_digits(str(row.get('COD_BANCO', '')))
            if banco == '237': return '01' # Credit Account
            return '41' # TED
            
        df['forma_lancamento'] = df.apply(get_forma, axis=1)
        
        for forma, group in df.groupby('forma_lancamento'):
            self.lotes_count += 1
            lote_seq = self.lotes_count
            
            layout_lote = "045" if forma == '45' else "040"
            
            header_lote_data = {
                "lote": str(lote_seq),
                "forma_lancamento": forma,
                "layout_lote": layout_lote,
                "numero_inscricao": self.empresa_data['cnpj'],
                "tipo_inscricao": "2",
                "convenio": self.empresa_data['convenio'],
                "agencia": self.empresa_data['agencia'],
                "conta": self.empresa_data['conta'],
                "nome_empresa": self.empresa_data['nome'],
                "logradouro": "", # Optional
                "cidade": "",
                "estado": "  "
            }
            self.lines.append(self._generate_line(HEADER_LOTE, header_lote_data))
            self.registros_count += 1
            
            items_in_lot = 0
            total_val_lot = 0.0
            
            for idx, row in group.iterrows():
                items_in_lot += 1
                
                # Validation of Value/Date happens before or here?
                # Ideally validation was done in App. Here we assume valid or raw.
                
                val_float = float(row['VALOR_PAGAMENTO'])
                total_val_lot += val_float
                val_str = format_value(val_float)
                
                date_str = pd.to_datetime(row['DATA_PAGAMENTO'], dayfirst=True).strftime("%d%m%Y")
                
                fav_insc_type, fav_insc_num = determine_inscription_type(row['CPF_CNPJ'])
                
                # Camara Logic
                if forma == '45': camara = '009' # Pix
                elif forma == '41': camara = '018' # TED
                else: camara = '000' # CC
                
                # Segment A
                seg_a_data = {
                    "lote": str(lote_seq),
                    "n_registro": str(items_in_lot),
                    "camara": camara,
                    "banco_favorecido": clean_non_digits(row['COD_BANCO']),
                    "agencia_favorecido": clean_non_digits(row['AGENCIA']),
                    "conta_favorecido": clean_non_digits(row['CONTA']),
                    "nome_favorecido": sanitize_text(row['NOME_FAVORECIDO']),
                    "data_pagamento": date_str,
                    "valor_pagamento": val_str,
                    "tipo_inscricao_fav": fav_insc_type,
                    "numero_inscricao_fav": fav_insc_num,
                    "n_doc_empresa": str(idx+1).zfill(10), # Seu Numero = ROW ID
                    "cod_finalidade_ted": "00005" if forma == '41' else ""
                }
                self.lines.append(self._generate_line(SEGMENTO_A, seg_a_data))
                self.registros_count += 1
                
                if forma == '45':
                    # Segment B for PIX
                    items_in_lot += 1
                    
                    pix_key = str(row['CHAVE_PIX']).strip()
                    pix_type_raw = str(row.get('TIPO_CHAVE_PIX', '')).upper()
                    
                    forma_iniciacao = "01" # Or error?
                    if "TELEFONE" in pix_type_raw: forma_iniciacao = "02" # Manual said 01=Email? No, wait.
                    # User said: 01=Email, 02=Telefone in the NEW REQUEST!
                    # "Posição 126-127: Forma de Iniciação (01=Email, 02=Telefone, 03=CPF/CNPJ, 04=Chave Aleatória)."
                    # Okay, using USER's Specific Instruction.
                
                    if "EMAIL" in pix_type_raw: forma_iniciacao = "01"
                    elif "TELEFONE" in pix_type_raw: forma_iniciacao = "02"
                    elif "CPF" in pix_type_raw or "CNPJ" in pix_type_raw: forma_iniciacao = "03"
                    elif "ALEATORIA" in pix_type_raw: forma_iniciacao = "04"
                    
                    # Redundancy Check
                    final_key = pix_key
                    if forma_iniciacao == "03": final_key = "" # Suppress if CPF/CNPJ
                    
                    seg_b_data = {
                        "lote": str(lote_seq),
                        "n_registro": str(items_in_lot),
                        "forma_iniciacao": forma_iniciacao,
                        "tipo_inscricao_fav": fav_insc_type,
                        "numero_inscricao_fav": fav_insc_num,
                        "chave_pix_ou_conta": sanitize_text(final_key, allow_email=True)
                    }
                    self.lines.append(self._generate_line(SEGMENTO_B, seg_b_data))
                    self.registros_count += 1
                    
            # Trailer Lote
            trailer_lote_data = {
                "lote": str(lote_seq),
                "qtd_registros": str(items_in_lot + 2), # Header + Details + Trailer
                "valor_total": format_value(total_val_lot)
            }
            self.lines.append(self._generate_line(TRAILER_LOTE, trailer_lote_data))
            self.registros_count += 1
            self.total_value_file += total_val_lot
            
        # Trailer Arquivo
        trailer_arq_data = {
            "qtd_lotes": str(self.lotes_count),
            "qtd_registros": str(self.registros_count + 1) # All previous + Trailer File
        }
        self.lines.append(self._generate_line(TRAILER_ARQUIVO, trailer_arq_data))
        
        # Combine and Encode
        full_text = "\r\n".join(self.lines)
        return full_text.encode('cp1252', errors='replace')
