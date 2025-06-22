"""
Módulo para calcular KPIs (Key Performance Indicators)
"""
import pandas as pd
from utils.formatters import safe_divide

def _get_col_name(df, *potential_names):
    """Retorna o primeiro nome de coluna encontrado no DataFrame a partir de uma lista de nomes potenciais."""
    for name in potential_names:
        if name in df.columns:
            return name
    return None

def calculate_sales_kpis(df_vendas: pd.DataFrame) -> dict:
    """
    Calcula os principais KPIs de vendas.

    Args:
        df_vendas: DataFrame com os dados de vendas.

    Returns:
        Um dicionário contendo 'revenue', 'transactions', e 'avg_ticket'.
    """
    if df_vendas.empty:
        return {'revenue': 0, 'transactions': 0, 'avg_ticket': 0}

    valor_col = _get_col_name(df_vendas, 'VALOR', 'Valor')
    
    if not valor_col:
        return {'revenue': 0, 'transactions': 0, 'avg_ticket': 0}

    total_revenue = df_vendas[valor_col].sum()
    num_transactions = len(df_vendas)
    average_ticket = safe_divide(total_revenue, num_transactions)

    return {
        'revenue': total_revenue,
        'transactions': num_transactions,
        'avg_ticket': average_ticket
    }

def get_top_five(df: pd.DataFrame, category_col_options: list, value_col_options: list) -> pd.DataFrame:
    """
    Calcula o top 5 para uma determinada categoria com base em uma coluna de valor.

    Args:
        df: DataFrame de entrada.
        category_col_options: Lista de nomes de coluna possíveis para a categoria.
        value_col_options: Lista de nomes de coluna possíveis para o valor.

    Returns:
        Um DataFrame com o top 5 ou um DataFrame vazio se as colunas não existirem.
    """
    category_col = _get_col_name(df, *category_col_options)
    value_col = _get_col_name(df, *value_col_options)

    if not category_col or not value_col or df.empty:
        return pd.DataFrame()

    top_five_df = df.groupby(category_col)[value_col].sum().nlargest(5).reset_index()
    return top_five_df

def calculate_sales_by_weekday(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula o total de vendas para cada dia da semana.

    Args:
        df: DataFrame de vendas com as colunas 'DATA' e 'VALOR'.

    Returns:
        DataFrame com 'Dia da Semana', 'Soma_Valor' e 'Ordem'.
    """
    data_col = _get_col_name(df, 'DATA', 'Data')
    valor_col = _get_col_name(df, 'VALOR', 'Valor')

    if not data_col or not valor_col or df.empty:
        return pd.DataFrame(columns=['Dia_Semana', valor_col])

    df_copy = df.copy()
    df_copy[data_col] = pd.to_datetime(df_copy[data_col], errors='coerce')
    df_copy.dropna(subset=[data_col, valor_col], inplace=True)

    if df_copy.empty:
        return pd.DataFrame(columns=['Dia_Semana', valor_col])
        
    df_copy['Dia_Semana'] = df_copy[data_col].dt.day_name(locale='pt_BR.utf8')
    
    # Ordenar os dias da semana corretamente
    dias_ordenados = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
    df_copy['Dia_Semana'] = pd.Categorical(df_copy['Dia_Semana'].str.lower(), categories=dias_ordenados, ordered=True)

    sales_by_day = df_copy.groupby('Dia_Semana')[valor_col].sum().reset_index()
    
    return sales_by_day.sort_values('Dia_Semana')

def calculate_new_customers(all_sales_df: pd.DataFrame, filtered_sales_df: pd.DataFrame) -> int:
    """
    Calcula o número de novos clientes dentro de um período filtrado.

    Args:
        all_sales_df: DataFrame com todas as vendas (histórico completo).
        filtered_sales_df: DataFrame com as vendas do período selecionado.

    Returns:
        O número de novos clientes no período.
    """
    client_col = _get_col_name(all_sales_df, 'CLIENTE', 'Cliente')
    date_col = _get_col_name(all_sales_df, 'DATA', 'Data')

    if not client_col or not date_col or all_sales_df.empty or filtered_sales_df.empty:
        return 0

    # Copia para evitar SettingWithCopyWarning
    all_sales = all_sales_df.copy()
    filtered_sales = filtered_sales_df.copy()

    # Certifica que as datas são do tipo datetime
    all_sales[date_col] = pd.to_datetime(all_sales[date_col], errors='coerce')
    filtered_sales[date_col] = pd.to_datetime(filtered_sales[date_col], errors='coerce')
    
    # Encontra a data da primeira compra para cada cliente no histórico completo
    first_purchase_dates = all_sales.groupby(client_col)[date_col].min()
    
    # Pega os clientes únicos do período filtrado
    clients_in_period = filtered_sales[client_col].unique()
    
    # Determina o intervalo de datas do filtro
    start_date_period = filtered_sales[date_col].min()
    end_date_period = filtered_sales[date_col].max()
    
    new_customer_count = 0
    for client in clients_in_period:
        first_purchase = first_purchase_dates.get(client)
        if pd.notna(first_purchase) and start_date_period <= first_purchase <= end_date_period:
            new_customer_count += 1
            
    return new_customer_count 