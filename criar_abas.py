import pandas as pd
from datetime import datetime, timedelta
import random
import openpyxl
import os

# Criar dados de exemplo para a aba Vendas
datas_vendas = [(datetime(2024, 1, 1) + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(60)]
clientes = ['Maria Silva', 'João Santos', 'Ana Oliveira', 'Pedro Costa', 'Lucia Pereira']
produtos = [
    ('Produto A', 50.0, 30.0),
    ('Produto B', 75.0, 45.0),
    ('Produto C', 120.0, 72.0),
    ('Produto D', 25.0, 15.0),
    ('Produto E', 200.0, 120.0)
]

vendas_data = []
for data in datas_vendas:
    num_vendas = random.randint(1, 3)
    for _ in range(num_vendas):
        cliente = random.choice(clientes)
        produto = random.choice(produtos)
        quantidade = random.randint(1, 5)
        valor_unitario = produto[1]
        custo_unitario = produto[2]
        valor_total = valor_unitario * quantidade
        custo_total = custo_unitario * quantidade
        lucro = valor_total - custo_total
        
        vendas_data.append({
            'DATA': data,
            'CLIENTE': cliente,
            'PRODUTO': produto[0],
            'QUANTIDADE': quantidade,
            'VALOR_UNITARIO': valor_unitario,
            'CUSTO_UNITARIO': custo_unitario,
            'VALOR_TOTAL': valor_total,
            'CUSTO_TOTAL': custo_total,
            'LUCRO': lucro
        })

df_vendas = pd.DataFrame(vendas_data)

# Criar dados de exemplo para a aba Investimentos
datas_invest = [(datetime(2024, 1, 1) + timedelta(days=x*15)).strftime('%Y-%m-%d') for x in range(24)]
tipos_invest = {
    'Ações': ['PETR4', 'VALE3', 'ITUB4', 'BBDC4'],
    'FIIs': ['HGLG11', 'XPLG11', 'MXRF11'],
    'Renda Fixa': ['Tesouro IPCA+', 'CDB Banco X', 'LCI Banco Y']
}

investimentos_data = []
for data in datas_invest:
    tipo = random.choice(list(tipos_invest.keys()))
    ativo = random.choice(tipos_invest[tipo])
    
    if tipo == 'Renda Fixa':
        valor_aporte = random.randint(5, 20) * 100
        quantidade = 1
        preco_medio = valor_aporte
    else:
        quantidade = random.randint(5, 20)
        preco_medio = random.randint(20, 100)
        valor_aporte = quantidade * preco_medio
    
    objetivo = random.choice(['Aposentadoria', 'Reserva de Emergência', 'Objetivo de Curto Prazo'])
    
    investimentos_data.append({
        'DATA': data,
        'TIPO': tipo,
        'ATIVO': ativo,
        'VALOR_APORTE': valor_aporte,
        'QUANTIDADE': quantidade,
        'PRECO_MEDIO': preco_medio,
        'OBJETIVO': objetivo
    })

df_investimentos = pd.DataFrame(investimentos_data)

def criar_aba_excel(nome_arquivo, nome_aba, colunas, dados=None):
    """
    Cria uma nova aba em um arquivo Excel, sem sobrescrever se já existir.
    - nome_arquivo: caminho do arquivo Excel
    - nome_aba: nome da nova aba
    - colunas: lista de nomes das colunas
    - dados: lista de dicionários ou DataFrame (opcional)
    """
    # Se o arquivo não existir, cria um novo
    if not os.path.exists(nome_arquivo):
        df_vazia = pd.DataFrame(columns=colunas)
        with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
            df_vazia.to_excel(writer, sheet_name=nome_aba, index=False)
        print(f"Arquivo '{nome_arquivo}' criado com a aba '{nome_aba}'.")
        return

    # Carrega as abas existentes
    xls = pd.ExcelFile(nome_arquivo)
    if nome_aba in xls.sheet_names:
        print(f"Aba '{nome_aba}' já existe. Nada foi alterado.")
        return

    # Cria DataFrame vazio ou com dados
    if dados is None:
        df = pd.DataFrame(columns=colunas)
    else:
        df = pd.DataFrame(dados, columns=colunas)

    # Adiciona a nova aba sem sobrescrever as existentes
    with pd.ExcelWriter(nome_arquivo, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name=nome_aba, index=False)
    print(f"Aba '{nome_aba}' criada com sucesso!")

# Exemplo de uso: criar aba 'Vendas' com as colunas desejadas
if __name__ == "__main__":
    nome_arquivo = 'Base_financas.xlsx'
    nome_aba = 'Vendas'
    colunas = ['DATA', 'DESCRIÇÃO', 'CONTA', 'TIPO DE RECEBIMENTO', 'VALOR', 'PAGO']
    criar_aba_excel(nome_arquivo, nome_aba, colunas)
    # Para criar outras abas, basta chamar novamente:
    # criar_aba_excel(nome_arquivo, 'NovaAba', ['Col1', 'Col2'])

    # Adicionar aba 'Investimentos'
    criar_aba_excel(nome_arquivo, 'Investimentos', ['DATA', 'TIPO', 'ATIVO', 'VALOR_APORTE', 'QUANTIDADE', 'PRECO_MEDIO', 'OBJETIVO'], df_investimentos)

    print("Novas abas 'Vendas' e 'Investimentos' foram adicionadas com sucesso!") 