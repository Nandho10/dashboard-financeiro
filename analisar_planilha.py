import pandas as pd

# Carregar a planilha
xls = pd.ExcelFile('Base_financas.xlsx')
print('Abas disponíveis:', xls.sheet_names)

# Analisar a aba Despesas Categoria
df_cat = pd.read_excel(xls, 'Despesas Categoria')
print('\nColunas da aba Despesas Categoria:', df_cat.columns.tolist())
print('\nPrimeiras linhas da aba Despesas Categoria:')
print(df_cat.head())

# Analisar cada coluna (categoria) para ver os itens
print('\n=== ITENS POR CATEGORIA ===')
for coluna in df_cat.columns:
    if coluna != 'CATEGORIA':  # Pular a coluna CATEGORIA se existir
        itens = df_cat[coluna].dropna().tolist()
        print(f'\n{coluna}:')
        for item in itens:
            print(f'  - {item}')

# Analisar a aba Receitas Categoria também
if 'Receitas Categoria' in xls.sheet_names:
    df_rec_cat = pd.read_excel(xls, 'Receitas Categoria')
    print('\n=== ITENS DE RECEITAS ===')
    print('Colunas:', df_rec_cat.columns.tolist())
    if 'SUBCATEGORIA' in df_rec_cat.columns:
        subcategorias = df_rec_cat['SUBCATEGORIA'].dropna().unique().tolist()
        print('Subcategorias de receitas:', subcategorias) 