import pandas as pd
import numpy as np

def adicionar_coluna_id(excel_path, sheet_name='Div_CC'):
    """
    Verifica se a coluna 'id' existe na aba especificada.
    Se não existir, adiciona a coluna e a preenche com um ID único para cada linha.
    """
    try:
        xls = pd.ExcelFile(excel_path)
        if sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            if 'id' not in df.columns:
                print(f"A coluna 'id' não foi encontrada na aba '{sheet_name}'. Adicionando...")
                
                # Gera IDs únicos para cada linha existente
                df['id'] = range(1, len(df) + 1)
                
                # Salva a alteração de volta no arquivo Excel
                with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                print("Coluna 'id' adicionada e preenchida com sucesso!")
            else:
                print(f"A coluna 'id' já existe na aba '{sheet_name}'. Nenhuma alteração necessária.")

        else:
            print(f"A aba '{sheet_name}' não foi encontrada no arquivo Excel.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    caminho_excel = 'Base_financas.xlsx'
    adicionar_coluna_id(caminho_excel) 