import pandas as pd
from datetime import datetime, timedelta
import random
import openpyxl
import os

def criar_aba_investimentos():
    """
    Cria a aba de Investimentos com dados de exemplo incluindo metas
    """
    # Dados de exemplo para investimentos
    datas_invest = [(datetime(2024, 1, 1) + timedelta(days=x*15)).strftime('%Y-%m-%d') for x in range(24)]
    
    tipos_invest = {
        'Ações': ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3'],
        'FIIs': ['HGLG11', 'XPLG11', 'MXRF11', 'HABT11', 'IRDM11'],
        'Renda Fixa': ['Tesouro IPCA+', 'CDB Banco X', 'LCI Banco Y', 'Tesouro Selic'],
        'Criptomoedas': ['Bitcoin', 'Ethereum', 'Cardano'],
        'Fundos': ['Fundos Imobiliários', 'Fundos de Ações', 'Fundos Multimercado']
    }
    
    objetivos = ['Aposentadoria', 'Reserva de Emergência', 'Objetivo de Curto Prazo', 'Viagem', 'Compra de Casa']
    
    investimentos_data = []
    
    for data in datas_invest:
        tipo = random.choice(list(tipos_invest.keys()))
        ativo = random.choice(tipos_invest[tipo])
        objetivo = random.choice(objetivos)
        
        # Valor do aporte varia conforme o tipo
        if tipo == 'Renda Fixa':
            valor_aporte = random.randint(5, 20) * 100
            quantidade = 1
            preco_medio = valor_aporte
        elif tipo == 'Criptomoedas':
            valor_aporte = random.randint(1, 5) * 1000
            quantidade = random.randint(1, 3)
            preco_medio = valor_aporte / quantidade
        else:
            quantidade = random.randint(5, 50)
            preco_medio = random.randint(20, 150)
            valor_aporte = quantidade * preco_medio
        
        # Meta anual (exemplo: 30000 para 2025)
        meta_anual = 30000
        
        investimentos_data.append({
            'DATA': data,
            'TIPO': tipo,
            'ATIVO': ativo,
            'VALOR_APORTE': valor_aporte,
            'QUANTIDADE': quantidade,
            'PRECO_MEDIO': preco_medio,
            'OBJETIVO': objetivo,
            'META_ANUAL': meta_anual,
            'ANO': datetime.strptime(data, '%Y-%m-%d').year
        })
    
    return pd.DataFrame(investimentos_data)

def criar_aba_metas():
    """
    Cria a aba de Metas de Investimento
    """
    metas_data = [
        {
            'ANO': 2024,
            'META_TOTAL': 25000,
            'META_MENSAL': 2083.33,
            'OBJETIVO': 'Aposentadoria',
            'DESCRICAO': 'Meta de aportes para 2024'
        },
        {
            'ANO': 2025,
            'META_TOTAL': 30000,
            'META_MENSAL': 2500.00,
            'OBJETIVO': 'Aposentadoria',
            'DESCRICAO': 'Meta de aportes para 2025'
        },
        {
            'ANO': 2024,
            'META_TOTAL': 12000,
            'META_MENSAL': 1000.00,
            'OBJETIVO': 'Reserva de Emergência',
            'DESCRICAO': 'Meta para reserva de emergência 2024'
        },
        {
            'ANO': 2025,
            'META_TOTAL': 15000,
            'META_MENSAL': 1250.00,
            'OBJETIVO': 'Reserva de Emergência',
            'DESCRICAO': 'Meta para reserva de emergência 2025'
        }
    ]
    
    return pd.DataFrame(metas_data)

def criar_abas_excel():
    """
    Cria as abas de Investimentos e Metas no arquivo Excel
    """
    nome_arquivo = 'Base_financas.xlsx'
    
    # Criar aba de Investimentos
    df_investimentos = criar_aba_investimentos()
    colunas_invest = ['DATA', 'TIPO', 'ATIVO', 'VALOR_APORTE', 'QUANTIDADE', 'PRECO_MEDIO', 'OBJETIVO', 'META_ANUAL', 'ANO']
    
    # Criar aba de Metas
    df_metas = criar_aba_metas()
    colunas_metas = ['ANO', 'META_TOTAL', 'META_MENSAL', 'OBJETIVO', 'DESCRICAO']
    
    # Verificar se o arquivo existe
    if not os.path.exists(nome_arquivo):
        print(f"Arquivo '{nome_arquivo}' não encontrado. Criando novo arquivo...")
        with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
            df_investimentos.to_excel(writer, sheet_name='Investimentos', index=False)
            df_metas.to_excel(writer, sheet_name='Metas', index=False)
        print("Arquivo criado com as abas 'Investimentos' e 'Metas'!")
        return
    
    # Carregar abas existentes
    xls = pd.ExcelFile(nome_arquivo)
    
    # Criar aba Investimentos se não existir
    if 'Investimentos' not in xls.sheet_names:
        with pd.ExcelWriter(nome_arquivo, engine='openpyxl', mode='a') as writer:
            df_investimentos.to_excel(writer, sheet_name='Investimentos', index=False)
        print("Aba 'Investimentos' criada com sucesso!")
    else:
        print("Aba 'Investimentos' já existe.")
    
    # Criar aba Metas se não existir
    if 'Metas' not in xls.sheet_names:
        with pd.ExcelWriter(nome_arquivo, engine='openpyxl', mode='a') as writer:
            df_metas.to_excel(writer, sheet_name='Metas', index=False)
        print("Aba 'Metas' criada com sucesso!")
    else:
        print("Aba 'Metas' já existe.")

if __name__ == "__main__":
    criar_abas_excel()
    print("Processo concluído!") 