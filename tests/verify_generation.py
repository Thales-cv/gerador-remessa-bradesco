import sys
import os
sys.path.append(os.getcwd())

import pandas as pd
from src.generator import CNABGenerator

def test_generation():
    # Mock Data
    empresa_data = {
        "nome": "TESTE EMPRESA",
        "cnpj": "12345678000199",
        "convenio": "12345",
        "agencia": "1234",
        "conta": "12345",
        "pix_flag": "PIX"
    }
    
    # Create DF with mixed types
    data = [
        {
            "Nome Favorecido": "JOAO TED",
            "CPF/CNPJ": "111.222.333-44",
            "Banco (Código)": "341",
            "Agência": "1234",
            "Conta": "55555",
            "Valor": 100.00,
            "Data Pagamento (DD/MM/AAAA)": "13/01/2026",
            "Tipo de Pagamento (PIX/TED/DOC/CC)": "TED"
        },
        {
            "Nome Favorecido": "MARIA PIX",
            "CPF/CNPJ": "555.666.777-88",
            "Banco (Código)": "237",
            "Agência": "1234",
            "Conta": "66666",
            "Valor": 50.00,
            "Data Pagamento (DD/MM/AAAA)": "13/01/2026",
            "Tipo de Pagamento (PIX/TED/DOC/CC)": "PIX",
            "Chave Pix (Se PIX)": "maria@pix.com",
            "Tipo Chave Pix (Email, Telefone, CPF, Aleatoria, Banco)": "Email"
        }
    ]
    
    df = pd.DataFrame(data)
    
    generator = CNABGenerator(nsa=1, empresa_data=empresa_data)
    content = generator.generate(df)
    
    lines = content.split('\r\n')
    
    print(f"Generated {len(lines)} lines.")
    
    for i, line in enumerate(lines):
        print(f"Line {i+1} Length: {len(line)}")
        if len(line) != 240:
            print(f"ERROR: Line {i+1} is not 240 chars!")
        
        # Check specific content
        # Line 3 should be Seg A for TED (HeaderFile, HeaderLote(Pix? No mix groups?), HeaderLote(Ted?))
        # Batching logic: Group by 'is_pix'.
        # Group 1: TED (is_pix=False). Header Lote. Seg A. Trailer Lote.
        # Group 2: PIX (is_pix=True). Header Lote. Seg A. Seg B. Trailer Lote.
        # Trailer Arquivo.
        
        # Let's inspect content
        print(f"Line {i+1} Content: {line}")

if __name__ == "__main__":
    test_generation()
