"""
Configurações centralizadas do Dashboard Financeiro
"""

import os
from pathlib import Path

# Configurações de caminhos
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backups"
EXCEL_FILE = BASE_DIR / "Base_financas.xlsx"

# Configurações do Streamlit
STREAMLIT_CONFIG = {
    "page_title": "Dashboard Financeiro",
    "page_icon": "💰",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": {
        "Get help": "https://github.com/seu-usuario/dashboard-financeiro",
        "Report a bug": "https://github.com/seu-usuario/dashboard-financeiro/issues",
        "About": "Dashboard Financeiro - Sistema de Gestão Financeira Pessoal"
    }
}

# Configurações de cores
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e", 
    "success": "#2ca02c",
    "warning": "#d62728",
    "info": "#9467bd",
    "light": "#8c564b",
    "dark": "#e377c2",
    "muted": "#7f7f7f",
    "white": "#ffffff",
    "black": "#000000"
}

# Configurações de categorias padrão
DEFAULT_CATEGORIES = {
    "Moradia": 15,
    "Alimentação": 20,
    "Saúde": 10,
    "Transporte": 15,
    "Vestuário": 10,
    "Educação": 10,
    "Lazer": 5,
    "Dívidas/Investimentos": 15
}

# Configurações de formatação
FORMAT_CONFIG = {
    "currency": "R$ {:,.2f}",
    "percentage": "{:.1f}%",
    "date_format": "%d/%m/%Y",
    "datetime_format": "%d/%m/%Y %H:%M"
}

# Configurações de validação
VALIDATION_CONFIG = {
    "max_file_size_mb": 50,
    "allowed_extensions": [".xlsx", ".xls"],
    "required_sheets": ["Receitas", "Despesas", "Div_CC", "Orcamento"],
    "required_columns": {
        "Receitas": ["Data", "Descrição", "VALOR", "CATEGORIA"],
        "Despesas": ["Data", "Descrição", "VALOR", "CATEGORIA", "FAVORECIDO", "PAGO"],
        "Div_CC": ["Data", "Descrição", "VALOR", "CATEGORIA"],
        "Orcamento": ["CATEGORIA", "Percentual"]
    }
}

# Configurações de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": BASE_DIR / "logs" / "dashboard.log"
}

# Configurações de cache
CACHE_CONFIG = {
    "ttl": 300,  # 5 minutos
    "max_entries": 100
}

# Configurações de backup
BACKUP_CONFIG = {
    "auto_backup": True,
    "backup_interval_hours": 24,
    "max_backups": 30,
    "backup_before_changes": True
}

# Configurações de segurança
SECURITY_CONFIG = {
    "max_login_attempts": 3,
    "session_timeout_minutes": 60,
    "password_min_length": 8
}

# Configurações de performance
PERFORMANCE_CONFIG = {
    "max_rows_display": 1000,
    "chunk_size": 100,
    "enable_caching": True,
    "optimize_queries": True
} 