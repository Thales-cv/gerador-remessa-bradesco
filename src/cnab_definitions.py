from enum import Enum

class PadType(Enum):
    ZERO_LEFT = "zero_left"
    SPACE_RIGHT = "space_right"

# Layout Constants based on Bradesco Multipag CNAB 240 v089
# IMPORTANT: All layouts must sum to 240 characters exactly.

HEADER_ARQUIVO = {
    "banco": (1, 3, PadType.ZERO_LEFT, "237"),
    "lote": (4, 7, PadType.ZERO_LEFT, "0000"),
    "registro": (8, 8, PadType.ZERO_LEFT, "0"),
    "cnab_vazio": (9, 17, PadType.SPACE_RIGHT, ""),
    "tipo_inscricao": (18, 18, PadType.ZERO_LEFT, ""), # 1=CPF, 2=CNPJ
    "numero_inscricao": (19, 32, PadType.ZERO_LEFT, ""), 
    "convenio": (33, 52, PadType.SPACE_RIGHT, ""),
    "agencia": (53, 57, PadType.ZERO_LEFT, ""),
    "agencia_dv": (58, 58, PadType.SPACE_RIGHT, ""),
    "conta": (59, 70, PadType.ZERO_LEFT, ""),
    "conta_dv": (71, 71, PadType.SPACE_RIGHT, ""),
    "dv_ag_conta": (72, 72, PadType.SPACE_RIGHT, ""),
    "nome_empresa": (73, 102, PadType.SPACE_RIGHT, ""),
    "nome_banco": (103, 132, PadType.SPACE_RIGHT, "BRADESCO"),
    "cnab_vazio_2": (133, 142, PadType.SPACE_RIGHT, ""),
    "codigo_remessa": (143, 143, PadType.ZERO_LEFT, "1"), 
    "data_geracao": (144, 151, PadType.ZERO_LEFT, ""), # DDMMAAAA
    "hora_geracao": (152, 157, PadType.ZERO_LEFT, ""), # HHMMSS
    "nsa": (158, 163, PadType.ZERO_LEFT, ""), 
    "layout_arquivo": (164, 166, PadType.ZERO_LEFT, "089"),
    "densidade": (167, 171, PadType.ZERO_LEFT, "01600"),
    "reservado_banco": (172, 174, PadType.SPACE_RIGHT, ""), # PIX if Pix
    "reservado_banco_2": (175, 240, PadType.SPACE_RIGHT, ""),
}

HEADER_LOTE = {
    "banco": (1, 3, PadType.ZERO_LEFT, "237"),
    "lote": (4, 7, PadType.ZERO_LEFT, ""), 
    "registro": (8, 8, PadType.ZERO_LEFT, "1"),
    "operacao": (9, 9, PadType.SPACE_RIGHT, "C"),
    "tipo_pagamento": (10, 11, PadType.ZERO_LEFT, "20"),
    "forma_lancamento": (12, 13, PadType.ZERO_LEFT, ""), # 45=Pix, 41=TED, 01=CC, 03=DOC
    "layout_lote": (14, 16, PadType.ZERO_LEFT, "045"),
    "cnab_vazio": (17, 17, PadType.SPACE_RIGHT, ""),
    "tipo_inscricao": (18, 18, PadType.ZERO_LEFT, ""),
    "numero_inscricao": (19, 32, PadType.ZERO_LEFT, ""),
    "convenio": (33, 52, PadType.SPACE_RIGHT, ""),
    "agencia": (53, 57, PadType.ZERO_LEFT, ""),
    "agencia_dv": (58, 58, PadType.SPACE_RIGHT, ""),
    "conta": (59, 70, PadType.ZERO_LEFT, ""),
    "conta_dv": (71, 71, PadType.SPACE_RIGHT, ""),
    "dv_ag_conta": (72, 72, PadType.SPACE_RIGHT, ""),
    "nome_empresa": (73, 102, PadType.SPACE_RIGHT, ""),
    "mensagem_1": (103, 142, PadType.SPACE_RIGHT, ""),
    "logradouro": (143, 172, PadType.SPACE_RIGHT, ""),
    "numero_local": (173, 177, PadType.ZERO_LEFT, ""),
    "complemento": (178, 192, PadType.SPACE_RIGHT, ""),
    "cidade": (193, 212, PadType.SPACE_RIGHT, ""),
    "cep": (213, 217, PadType.ZERO_LEFT, ""),
    "complemento_cep": (218, 220, PadType.SPACE_RIGHT, ""),
    "estado": (221, 222, PadType.SPACE_RIGHT, ""),
    "forma_pagamento_servico": (223, 224, PadType.ZERO_LEFT, "01"), # NEW: Force 01
    "cnab_vazio_2": (225, 230, PadType.SPACE_RIGHT, ""), 
    "ocorrencias": (231, 240, PadType.SPACE_RIGHT, "")
}

SEGMENTO_A = {
    "banco": (1, 3, PadType.ZERO_LEFT, "237"),
    "lote": (4, 7, PadType.ZERO_LEFT, ""),
    "registro": (8, 8, PadType.ZERO_LEFT, "3"),
    "n_registro": (9, 13, PadType.ZERO_LEFT, ""), 
    "segmento": (14, 14, PadType.SPACE_RIGHT, "A"),
    "tipo_movimento": (15, 15, PadType.ZERO_LEFT, "0"), 
    "codigo_instrucao": (16, 17, PadType.ZERO_LEFT, "00"),
    "camara": (18, 20, PadType.ZERO_LEFT, ""), 
    "banco_favorecido": (21, 23, PadType.ZERO_LEFT, ""),
    "agencia_favorecido": (24, 28, PadType.ZERO_LEFT, ""),
    "agencia_dv_favorecido": (29, 29, PadType.SPACE_RIGHT, ""),
    "conta_favorecido": (30, 41, PadType.ZERO_LEFT, ""),
    "conta_dv_favorecido": (42, 42, PadType.SPACE_RIGHT, ""),
    "dv_ag_conta_favorecido": (43, 43, PadType.SPACE_RIGHT, ""),
    "nome_favorecido": (44, 73, PadType.SPACE_RIGHT, ""),
    "n_doc_empresa": (74, 93, PadType.SPACE_RIGHT, ""), 
    "data_pagamento": (94, 101, PadType.ZERO_LEFT, ""),
    "tipo_moeda": (102, 104, PadType.SPACE_RIGHT, "BRL"),
    "quantidade_moeda": (105, 119, PadType.ZERO_LEFT, "0"),
    "valor_pagamento": (120, 134, PadType.ZERO_LEFT, ""), 
    "n_doc_banco": (135, 154, PadType.SPACE_RIGHT, ""),
    "data_real": (155, 162, PadType.ZERO_LEFT, "0"), 
    "valor_real": (163, 177, PadType.ZERO_LEFT, "0"), 
    "info_compl": (178, 217, PadType.SPACE_RIGHT, ""),
    "tipo_inscricao_fav": (218, 218, PadType.ZERO_LEFT, ""), 
    "numero_inscricao_fav": (219, 233, PadType.ZERO_LEFT, ""),
    "cod_finalidade_doc": (234, 235, PadType.SPACE_RIGHT, ""),
    "cod_finalidade_ted": (236, 240, PadType.SPACE_RIGHT, "") 
}

# Special Layout for Pix in Segment A:
# Cols 227-229 (Reservado Febraban) must be blank.
# Cols 231-240 (Reservado Banco) must be blank.
SEGMENTO_A_PIX = {
    "banco": (1, 3, PadType.ZERO_LEFT, "237"),
    "lote": (4, 7, PadType.ZERO_LEFT, ""),
    "registro": (8, 8, PadType.ZERO_LEFT, "3"),
    "n_registro": (9, 13, PadType.ZERO_LEFT, ""), 
    "segmento": (14, 14, PadType.SPACE_RIGHT, "A"),
    "tipo_movimento": (15, 15, PadType.ZERO_LEFT, "0"), 
    "codigo_instrucao": (16, 17, PadType.ZERO_LEFT, "00"),
    "camara": (18, 20, PadType.ZERO_LEFT, ""), 
    "banco_favorecido": (21, 23, PadType.ZERO_LEFT, ""),
    "agencia_favorecido": (24, 28, PadType.ZERO_LEFT, ""),
    "agencia_dv_favorecido": (29, 29, PadType.SPACE_RIGHT, ""),
    "conta_favorecido": (30, 41, PadType.ZERO_LEFT, ""),
    "conta_dv_favorecido": (42, 42, PadType.SPACE_RIGHT, ""),
    "dv_ag_conta_favorecido": (43, 43, PadType.SPACE_RIGHT, ""),
    "nome_favorecido": (44, 73, PadType.SPACE_RIGHT, ""),
    "n_doc_empresa": (74, 93, PadType.SPACE_RIGHT, ""), 
    "data_pagamento": (94, 101, PadType.ZERO_LEFT, ""),
    "tipo_moeda": (102, 104, PadType.SPACE_RIGHT, "BRL"),
    "quantidade_moeda": (105, 119, PadType.ZERO_LEFT, "0"),
    "valor_pagamento": (120, 134, PadType.ZERO_LEFT, ""), 
    "n_doc_banco": (135, 154, PadType.SPACE_RIGHT, ""),
    "data_real": (155, 162, PadType.ZERO_LEFT, "0"), 
    "valor_real": (163, 177, PadType.ZERO_LEFT, "0"), 
    "info_compl": (178, 217, PadType.SPACE_RIGHT, ""),
    "tipo_inscricao_fav": (218, 218, PadType.ZERO_LEFT, ""), 
    "numero_inscricao_fav_part1": (219, 226, PadType.ZERO_LEFT, "0"), 
    "reservado_febraban_fix": (227, 229, PadType.SPACE_RIGHT, ""), 
    "reservado_banco_fix": (230, 240, PadType.SPACE_RIGHT, "") 
} 

SEGMENTO_B = {
    "banco": (1, 3, PadType.ZERO_LEFT, "237"),
    "lote": (4, 7, PadType.ZERO_LEFT, ""),
    "registro": (8, 8, PadType.ZERO_LEFT, "3"),
    "n_registro": (9, 13, PadType.ZERO_LEFT, ""),
    "segmento": (14, 14, PadType.SPACE_RIGHT, "B"),
    "forma_iniciacao": (15, 17, PadType.SPACE_RIGHT, ""), # 01=Email, 02=Phone...
    "tipo_inscricao_fav": (18, 18, PadType.ZERO_LEFT, ""), 
    "numero_inscricao_fav": (19, 32, PadType.ZERO_LEFT, ""), # CPF/CNPJ Favorecido
    "info_10": (33, 67, PadType.SPACE_RIGHT, ""),
    "info_11": (68, 127, PadType.SPACE_RIGHT, ""),
    "chave_pix_ou_conta": (128, 226, PadType.SPACE_RIGHT, ""), # PIX Key or Account Type (05)
    "cnab_vazio": (227, 240, PadType.SPACE_RIGHT, "")
}

TRAILER_LOTE = {
    "banco": (1, 3, PadType.ZERO_LEFT, "237"),
    "lote": (4, 7, PadType.ZERO_LEFT, ""),
    "registro": (8, 8, PadType.ZERO_LEFT, "5"),
    "cnab_vazio": (9, 17, PadType.SPACE_RIGHT, ""),
    "qtd_registros": (18, 23, PadType.ZERO_LEFT, ""), # Header + Details + Trailer
    "valor_total": (24, 41, PadType.ZERO_LEFT, ""), 
    "qtd_moeda": (42, 59, PadType.ZERO_LEFT, "0"),
    "n_aviso_debito": (60, 65, PadType.ZERO_LEFT, "0"),
    "cnab_vazio_2": (66, 230, PadType.SPACE_RIGHT, ""),
    "ocorrencias": (231, 240, PadType.SPACE_RIGHT, "")
}

TRAILER_ARQUIVO = {
    "banco": (1, 3, PadType.ZERO_LEFT, "237"),
    "lote": (4, 7, PadType.ZERO_LEFT, "9999"),
    "registro": (8, 8, PadType.ZERO_LEFT, "9"),
    "cnab_vazio": (9, 17, PadType.SPACE_RIGHT, ""),
    "qtd_lotes": (18, 23, PadType.ZERO_LEFT, ""),
    "qtd_registros": (24, 29, PadType.ZERO_LEFT, ""), # Total Lines
    "qtd_contas": (30, 35, PadType.ZERO_LEFT, "0"),
    "cnab_vazio_2": (36, 240, PadType.SPACE_RIGHT, "")
}
