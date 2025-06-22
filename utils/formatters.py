# -*- coding: utf-8 -*-
"""
Módulo de Formatação
Responsável por formatar valores monetários, percentuais e outros dados
"""

import locale
from datetime import datetime

# Configurar locale para formatação brasileira
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass

def format_currency(value):
    """Formata valor como moeda brasileira"""
    if value is None or pd.isna(value):
        return "R$ 0,00"
    
    try:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def format_percentage(value):
    """Formata valor como percentual"""
    if value is None or pd.isna(value):
        return "0,00%"
    
    try:
        return f"{value:.2f}%".replace(".", ",")
    except:
        return "0,00%"

def get_delta_html(current_value, previous_value, delta_type="currency"):
    """Gera HTML para delta de métricas"""
    if current_value is None or previous_value is None:
        return ""
    
    delta = current_value - previous_value
    
    if delta_type == "percentage":
        if delta > 0:
            return f"↗️ +{format_percentage(delta)}"
        elif delta < 0:
            return f"↘️ {format_percentage(delta)}"
        else:
            return f"→ {format_percentage(delta)}"
    else:
        if delta > 0:
            return f"↗️ +{format_currency(delta)}"
        elif delta < 0:
            return f"↘️ {format_currency(delta)}"
        else:
            return f"→ {format_currency(delta)}"

def safe_divide(numerator, denominator, default=0):
    """Divisão segura que evita divisão por zero"""
    if denominator == 0 or denominator is None or pd.isna(denominator):
        return default
    return numerator / denominator

def format_date(date_value):
    """Formata data no padrão brasileiro"""
    if date_value is None or pd.isna(date_value):
        return ""
    
    try:
        if isinstance(date_value, str):
            date_value = pd.to_datetime(date_value)
        return date_value.strftime("%d/%m/%Y")
    except:
        return str(date_value)

def format_datetime(datetime_value):
    """Formata data e hora no padrão brasileiro"""
    if datetime_value is None or pd.isna(datetime_value):
        return ""
    
    try:
        if isinstance(datetime_value, str):
            datetime_value = pd.to_datetime(datetime_value)
        return datetime_value.strftime("%d/%m/%Y %H:%M")
    except:
        return str(datetime_value)

def format_number(value, decimals=2):
    """Formata número com separadores de milhares"""
    if value is None or pd.isna(value):
        return "0"
    
    try:
        return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0"

# Importar pandas para funções que dependem dele
import pandas as pd 