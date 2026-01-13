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
36: conta = st.sidebar.text_input("Conta (Sem dígito)", config.get("conta", "559461"))
37: digito_conta = st.sidebar.text_input("Dígito da Conta", config.get("digito_conta", "8"), max_chars=1)
38: nsa_atual = st.sidebar.number_input("NSA (Nº Sequencial Arquivo)", min_value=1, value=config.get("nsa", 1))
39: pix_flag = st.sidebar.checkbox("Habilitar Remessa PIX", value=True)
40: 
41: # --- 1. Download Template ---
42: st.subheader("1. Download do Modelo")
43: st.markdown("Utilize o modelo atualizado abaixo. Não altere os nomes das colunas.")
44: try:
45:     with open("templates/modelo_remessa.xlsx", "rb") as f:
46:         st.download_button("📥 Baixar Modelo Excel (.xlsx)", f, "modelo_remessa_bradesco_v2.xlsx")
47: except:
48:     st.error("Template não encontrado. Verifique se generated_template.py foi executado.")
49: 
50: # --- 2. Upload & Validation ---
51: st.subheader("2. Upload e Conferência")
52: uploaded_file = st.file_uploader("Carregar Excel Preenchido", type=["xlsx"])
53: 
54: if uploaded_file:
55:     # Strictly enforce string types
56:     try:
57:         df = pd.read_excel(uploaded_file, dtype=str)
58:         # Clean NaNs
59:         df = df.fillna("")
60:         
61:         # Filter Empty Rows (where NOME_FAVORECIDO or VALOR_PAGAMENTO is empty)
62:         df = df[df["NOME_FAVORECIDO"].str.strip() != ""]
63:         df = df[df["VALOR_PAGAMENTO"].str.strip() != ""]
64:         
65:         # Verify Columns
66:         req_cols = ["NOME_FAVORECIDO", "CPF_CNPJ", "COD_BANCO", "VALOR_PAGAMENTO", "DATA_PAGAMENTO"]
67:         missing = [c for c in req_cols if c not in df.columns]
68:         
69:         if missing:
70:             st.error(f"❌ Erro: Colunas faltando no Excel: {', '.join(missing)}")
71:         else:
72:             # --- Validations ---
73:             errors = []
74:             warnings = []
75:             
76:             total_val = 0.0
77:             
78:             for idx, row in df.iterrows():
79:                 line_no = idx + 2
80:                 
81:                 # Value Validation
82:                 try:
83:                     val = float(row['VALOR_PAGAMENTO'].replace('R$', '').replace(',', '.')) if row['VALOR_PAGAMENTO'] else 0.0
84:                     total_val += val
85:                     if val <= 0:
86:                         errors.append(f"Linha {line_no}: Valor inválido (R$ {val})")
87:                 except:
88:                     errors.append(f"Linha {line_no}: Formato de valor inválido")
89:                 
90:                 # Date Validation
91:                 dt_str = str(row['DATA_PAGAMENTO']).split()[0] # Handle "2026-01-01 00:00:00"
92:                 # If excel read as YYYY-MM-DD, try to convert or validate
93:                 # Ideally user puts DD/MM/YYYY text.
94:                 # If panda read it as timestamp:
95:                 if '-' in dt_str:
96:                      # Attempt to parse YYYY-MM-DD
97:                      try:
98:                          # Normalize to DD/MM/YYYY for internal use
99:                          dt_obj = pd.to_datetime(dt_str)
100:                          row['DATA_PAGAMENTO'] = dt_obj.strftime("%d/%m/%Y")
101:                      except:
102:                          pass
103:                 
104:                 if not validate_date_not_past(row['DATA_PAGAMENTO']):
105:                     errors.append(f"Linha {line_no}: Data no passado ou inválida ({row['DATA_PAGAMENTO']})")
106:                 
107:                 # Bank Warning
108:                 banco = str(row['COD_BANCO']).strip()
109:                 pix_key = str(row.get('CHAVE_PIX', '')).strip()
110:                 if not pix_key and banco != '237' and banco != '':
111:                     warnings.append(f"Linha {line_no}: Transferência para Banco {banco} (Será gerado como TED). Verifique se é intencional.")
112: 
113:             # --- Dashboard ---
114:             st.markdown("### 📊 Dashboard de Conferência")
115:             c1, c2, c3 = st.columns(3)
116:             c1.metric("Total Registros", len(df))
117:             c1.metric("Soma Total", f"R$ {total_val:,.2f}")
118:             c2.info(f"NSA a ser gerado: {nsa_atual}")
119:             
120:             st.dataframe(df)
121: 
122:             if warnings:
123:                 with st.expander("⚠️ Alertas não impeditivos"):
124:                     for w in warnings: st.write(w)
125:             
126:             if errors:
127:                 st.error("⛔ Foram encontrados erros impeditivos:")
128:                 for e in errors: st.write(f"- {e}")
129:             else:
130:                 # --- Generation ---
131:                 if st.button("🚀 Gerar Arquivo Remessa (ANSI)"):
132:                     empresa_data = {
133:                         "nome": nome_empresa,
134:                         "cnpj": cnpj_empresa,
135:                         "convenio": convenio,
136:                         "agencia": agencia,
137:                         "conta": conta,
138:                         "digito_conta": digito_conta,
139:                         "pix_flag": "PIX" if pix_flag else ""
140:                     }
                    
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
