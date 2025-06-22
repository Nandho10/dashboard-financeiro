import pandas as pd

def inspect_excel_file(file_path):
    """Lista as abas e as colunas da aba 'Orcamento' de um arquivo Excel."""
    try:
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        print("Abas encontradas no arquivo:")
        for name in sheet_names:
            print(f"- {name}")
        
        if 'Orcamento' in sheet_names:
            print("\nVerificando colunas da aba 'Orcamento':")
            df_orcamento = pd.read_excel(file_path, sheet_name='Orcamento')
            print(f"Colunas: {df_orcamento.columns.tolist()}")
        else:
            print("\nAba 'Orcamento' não foi encontrada no arquivo.")
            
    except FileNotFoundError:
        print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao inspecionar o arquivo: {e}")

if __name__ == "__main__":
    inspect_excel_file('Base_financas.xlsx') 