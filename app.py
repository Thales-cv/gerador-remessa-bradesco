import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from src.generator import CNABGenerator
from src.validators import validate_date_not_past, sanitize_text

# --- Config & Persistence ---
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"nsa": 1}

def save_config(nsa):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"nsa": nsa}, f)

st.set_page_config(page_title="Gerador Remessa Bradesco 089", page_icon="🏦", layout="wide")

# --- UI Header ---
st.title("🏦 Gerador de Remessa CNAB 240 - Bradesco Multipag (Layout 089)")
st.markdown("---")

# --- Sidebar: Company Config ---
st.sidebar.header("⚙️ Configurações da Empresa")
config = load_config()

nome_empresa = st.sidebar.text_input("Razão Social", config.get("nome_empresa", "DCS-CL CONSTRUTORA E PAVIMENTADORA LTDA"))
cnpj_empresa = st.sidebar.text_input("CNPJ (Somente Números)", config.get("cnpj", "95258174000165"))
convenio = st.sidebar.text_input("Código Convênio", config.get("convenio", "458049"))
agencia = st.sidebar.text_input("Agência (Sem dígito)", config.get("agencia", "0268"))
conta = st.sidebar.text_input("Conta (Sem dígito)", config.get("conta", "559461"))
nsa_atual = st.sidebar.number_input("NSA (Nº Sequencial Arquivo)", min_value=1, value=config.get("nsa", 1))
pix_flag = st.sidebar.checkbox("Habilitar Remessa PIX", value=True)

# --- 1. Download Template ---
st.subheader("1. Download do Modelo")
st.markdown("Utilize o modelo atualizado abaixo. Não altere os nomes das colunas.")
try:
    with open("templates/modelo_remessa.xlsx", "rb") as f:
        st.download_button("📥 Baixar Modelo Excel (.xlsx)", f, "modelo_remessa_bradesco_v2.xlsx")
except:
    st.error("Template não encontrado. Verifique se generated_template.py foi executado.")

# --- 2. Upload & Validation ---
st.subheader("2. Upload e Conferência")
uploaded_file = st.file_uploader("Carregar Excel Preenchido", type=["xlsx"])

if uploaded_file:
    # Strictly enforce string types
    try:
        df = pd.read_excel(uploaded_file, dtype=str)
        # Clean NaNs
        df = df.fillna("")
        
        # Filter Empty Rows (where NOME_FAVORECIDO or VALOR_PAGAMENTO is empty)
        df = df[df["NOME_FAVORECIDO"].str.strip() != ""]
        df = df[df["VALOR_PAGAMENTO"].str.strip() != ""]
        
        # Verify Columns
        req_cols = ["NOME_FAVORECIDO", "CPF_CNPJ", "COD_BANCO", "VALOR_PAGAMENTO", "DATA_PAGAMENTO"]
        missing = [c for c in req_cols if c not in df.columns]
        
        if missing:
            st.error(f"❌ Erro: Colunas faltando no Excel: {', '.join(missing)}")
        else:
            # --- Validations ---
            errors = []
            warnings = []
            
            total_val = 0.0
            
            for idx, row in df.iterrows():
                line_no = idx + 2
                
                # Value Validation
                try:
                    val = float(row['VALOR_PAGAMENTO'].replace('R$', '').replace(',', '.')) if row['VALOR_PAGAMENTO'] else 0.0
                    total_val += val
                    if val <= 0:
                        errors.append(f"Linha {line_no}: Valor inválido (R$ {val})")
                except:
                    errors.append(f"Linha {line_no}: Formato de valor inválido")
                
                # Date Validation
                dt_str = str(row['DATA_PAGAMENTO']).split()[0] # Handle "2026-01-01 00:00:00"
                # If excel read as YYYY-MM-DD, try to convert or validate
                # Ideally user puts DD/MM/YYYY text.
                # If panda read it as timestamp:
                if '-' in dt_str:
                     # Attempt to parse YYYY-MM-DD
                     try:
                         # Normalize to DD/MM/YYYY for internal use
                         dt_obj = pd.to_datetime(dt_str)
                         row['DATA_PAGAMENTO'] = dt_obj.strftime("%d/%m/%Y")
                     except:
                         pass
                
                if not validate_date_not_past(row['DATA_PAGAMENTO']):
                    errors.append(f"Linha {line_no}: Data no passado ou inválida ({row['DATA_PAGAMENTO']})")
                
                # Bank Warning
                banco = str(row['COD_BANCO']).strip()
                pix_key = str(row.get('CHAVE_PIX', '')).strip()
                if not pix_key and banco != '237' and banco != '':
                    warnings.append(f"Linha {line_no}: Transferência para Banco {banco} (Será gerado como TED). Verifique se é intencional.")

            # --- Dashboard ---
            st.markdown("### 📊 Dashboard de Conferência")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Registros", len(df))
            c1.metric("Soma Total", f"R$ {total_val:,.2f}")
            c2.info(f"NSA a ser gerado: {nsa_atual}")
            
            st.dataframe(df)

            if warnings:
                with st.expander("⚠️ Alertas não impeditivos"):
                    for w in warnings: st.write(w)
            
            if errors:
                st.error("⛔ Foram encontrados erros impeditivos:")
                for e in errors: st.write(f"- {e}")
            else:
                # --- Generation ---
                if st.button("🚀 Gerar Arquivo Remessa (ANSI)"):
                    empresa_data = {
                        "nome": nome_empresa,
                        "cnpj": cnpj_empresa,
                        "convenio": convenio,
                        "agencia": agencia,
                        "conta": conta,
                        "pix_flag": "PIX" if pix_flag else ""
                    }
                    
                    try:
                        # Progress bar simulation
                        my_bar = st.progress(0)
                        
                        gen = CNABGenerator(nsa=nsa_atual, empresa_data=empresa_data)
                        my_bar.progress(50)
                        
                        file_bytes = gen.generate(df)
                        my_bar.progress(100)
                        
                        fname = f"CB{datetime.now().strftime('%d%m')}{str(nsa_atual).zfill(2)}.REM"
                        
                        st.success(f"Arquivo gerado com sucesso! ({len(file_bytes)} bytes)")
                        st.download_button(
                            "💾 Download .REM (Layout 089)",
                            data=file_bytes,
                            file_name=fname,
                            mime="text/plain"
                        )
                        
                        # Increment NSA
                        save_config(nsa_atual + 1)
                        st.info("NSA incrementado para a próxima geração.")
                        
                    except Exception as e:
                        st.error(f"Erro na geração: {str(e)}")
                        st.exception(e)
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
