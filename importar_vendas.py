import pandas as pd

# Caminho do arquivo Excel
excel_path = 'Base_financas.xlsx'

# Lê a aba Receitas
xls = pd.ExcelFile(excel_path)
df = pd.read_excel(xls, sheet_name='Receitas')

# Filtra apenas as vendas
vendas = df[df['CATEGORIA'] == 'Vendas'][['DATA','DESCRIÇÃO','CONTA','TIPO DE RECEBIMENTO','VALOR','PAGO']]

# Escreve na aba Vendas (sobrescreve)
with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    vendas.to_excel(writer, sheet_name='Vendas', index=False)

print('Importação de vendas concluída!') 