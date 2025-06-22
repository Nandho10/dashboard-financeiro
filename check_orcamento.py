import pandas as pd
import openpyxl

def check_and_create_orcamento_tab(file_path):
    """
    Verifica a existência e a estrutura da aba 'Orcamento'.
    Se não existir ou estiver desatualizada, cria/recria a aba com os dados padrão.
    """
    try:
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
    except FileNotFoundError:
        print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
        return

    # Estrutura de orçamento padrão e correta
    orcamento_data = {
        'Categoria': [
            'Moradia', 'Alimentação', 'Saúde', 'Transporte', 'Vestuário',
            'Educação', 'Lazer', 'Dívidas/Investimentos'
        ],
        'Percentual': [
            15.0, 20.0, 10.0, 15.0, 10.0, 10.0, 5.0, 15.0
        ]
    }
    df_orcamento_padrao = pd.DataFrame(orcamento_data)

    needs_recreation = False
    if 'Orcamento' not in sheet_names:
        needs_recreation = True
        print("Aba 'Orcamento' não encontrada. Será criada.")
    else:
        print("Aba 'Orcamento' encontrada. Verificando estrutura...")
        df_existente = pd.read_excel(file_path, sheet_name='Orcamento')
        required_columns = {'Categoria', 'Percentual'}
        
        # Verifica se as colunas necessárias existem ou se as categorias estão desatualizadas
        if not required_columns.issubset(df_existente.columns) or \
           not set(df_orcamento_padrao['Categoria']).issubset(set(df_existente['Categoria'])):
            needs_recreation = True
            print("A estrutura da aba 'Orcamento' está desatualizada. Será recriada.")
        else:
            print("A aba 'Orcamento' já está com a estrutura correta.")

    if needs_recreation:
        print("Recriando a aba 'Orcamento' com os valores corretos...")
        try:
            # Carrega todas as abas, remove a antiga se existir, e adiciona a nova
            book = openpyxl.load_workbook(file_path)
            if 'Orcamento' in book.sheetnames:
                del book['Orcamento']
            book.save(file_path)
            book.close()

            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df_orcamento_padrao.to_excel(writer, sheet_name='Orcamento', index=False)
            print("Aba 'Orcamento' recriada com sucesso.")
        except Exception as e:
            print(f"Erro ao recriar a aba 'Orcamento': {e}")
            print("Por favor, feche o arquivo 'Base_financas.xlsx' se ele estiver aberto e tente novamente.")

if __name__ == "__main__":
    check_and_create_orcamento_tab('Base_financas.xlsx') 