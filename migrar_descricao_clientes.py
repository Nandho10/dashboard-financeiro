import pandas as pd
import openpyxl
from openpyxl import load_workbook

def migrar_descricao_para_clientes():
    """
    Migra os dados da coluna DESCRIÇÃO para a coluna CLIENTES na aba vendas
    e depois exclui a coluna DESCRIÇÃO
    """
    try:
        # Carregar o arquivo Excel
        arquivo = 'Base_financas.xlsx'
        print(f"Carregando arquivo: {arquivo}")
        
        # Ler a aba vendas
        df_vendas = pd.read_excel(arquivo, sheet_name='Vendas')
        print(f"Aba Vendas carregada com {len(df_vendas)} linhas")
        print(f"Colunas atuais: {list(df_vendas.columns)}")
        
        # Verificar se as colunas existem
        if 'DESCRIÇÃO' not in df_vendas.columns:
            print("ERRO: Coluna 'DESCRIÇÃO' não encontrada!")
            return
            
        if 'Cliente' not in df_vendas.columns:
            print("ERRO: Coluna 'Cliente' não encontrada!")
            return
        
        # Mostrar dados antes da migração
        print("\n=== DADOS ANTES DA MIGRAÇÃO ===")
        print("Coluna DESCRIÇÃO:")
        print(df_vendas['DESCRIÇÃO'].head(10))
        print("\nColuna Cliente:")
        print(df_vendas['Cliente'].head(10))
        
        # Migrar dados da DESCRIÇÃO para Cliente (apenas onde Cliente está vazio)
        mask_vazio = df_vendas['Cliente'].isna() | (df_vendas['Cliente'] == '')
        df_vendas.loc[mask_vazio, 'Cliente'] = df_vendas.loc[mask_vazio, 'DESCRIÇÃO']
        
        # Garantir que a coluna Cliente seja do tipo string
        df_vendas['Cliente'] = df_vendas['Cliente'].astype(str)
        
        # Mostrar dados após a migração
        print("\n=== DADOS APÓS A MIGRAÇÃO ===")
        print("Coluna Cliente (após migração):")
        print(df_vendas['Cliente'].head(10))
        
        # Contar quantos registros foram migrados
        registros_migrados = mask_vazio.sum()
        print(f"\nRegistros migrados: {registros_migrados}")
        
        # Excluir a coluna DESCRIÇÃO
        df_vendas = df_vendas.drop(columns=['DESCRIÇÃO'])
        
        # Salvar as alterações
        with pd.ExcelWriter(arquivo, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
            df_vendas.to_excel(writer, sheet_name='Vendas', index=False)
        
        print(f"\n✅ Migração concluída com sucesso!")
        print(f"✅ Coluna 'DESCRIÇÃO' foi excluída")
        print(f"✅ Dados salvos no arquivo {arquivo}")
        print(f"✅ Colunas finais: {list(df_vendas.columns)}")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {str(e)}")

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE DADOS: DESCRIÇÃO → CLIENTES ===")
    migrar_descricao_para_clientes() 