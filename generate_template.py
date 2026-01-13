import pandas as pd
import os

def create_template():
    # Columns strictly as requested
    columns = [
        "NOME_FAVORECIDO",
        "CPF_CNPJ",
        "COD_BANCO",
        "AGENCIA",
        "CONTA",
        "DIGITO_CONTA",
        "VALOR_PAGAMENTO",
        "DATA_PAGAMENTO",
        "TIPO_CHAVE_PIX", # Email, CPF, Telefone, Aleatoria
        "CHAVE_PIX",
        "DESCRICAO" # Optional description
    ]
    
    df = pd.DataFrame(columns=columns)
    
    # Updated Example
    example_row = {
        "NOME_FAVORECIDO": "FULANO DE TAL PAGO",
        "CPF_CNPJ": "000.123.456-78",
        "COD_BANCO": "237",
        "AGENCIA": "1234",
        "CONTA": "0012345",
        "DIGITO_CONTA": "0",
        "VALOR_PAGAMENTO": 150.50,
        "DATA_PAGAMENTO": "25/12/2026",
        "TIPO_CHAVE_PIX": "Email",
        "CHAVE_PIX": "pix@exemplo.com",
        "DESCRICAO": "Servico Prestado"
    }
    
    df = pd.concat([df, pd.DataFrame([example_row])], ignore_index=True)
    
    output_path = "templates/modelo_remessa.xlsx"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_excel(output_path, index=False)
    print(f"Template created at {output_path}")

if __name__ == "__main__":
    create_template()
