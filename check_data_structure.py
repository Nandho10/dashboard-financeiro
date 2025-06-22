import pandas as pd

def check_data_structure():
    """Verifica a estrutura dos dados no arquivo Excel"""
    try:
        excel_file = "Base_financas.xlsx"
        xls = pd.ExcelFile(excel_file)
        
        print("=== ESTRUTURA DO ARQUIVO EXCEL ===")
        print(f"Arquivo: {excel_file}")
        print(f"Abas encontradas: {xls.sheet_names}")
        
        for sheet_name in xls.sheet_names:
            print(f"\n--- ABA: {sheet_name} ---")
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            print(f"Colunas: {df.columns.tolist()}")
            print(f"Linhas: {len(df)}")
            if not df.empty:
                print(f"Primeiras linhas:")
                print(df.head(2))
            print("-" * 50)
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    check_data_structure() 