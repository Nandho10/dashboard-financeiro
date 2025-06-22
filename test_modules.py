# -*- coding: utf-8 -*-
"""
Teste dos módulos do dashboard financeiro
"""

print("Testando importação dos módulos...")

try:
    from modules.data_manager import data_manager
    print("✅ data_manager importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar data_manager: {e}")

try:
    from modules.filters_manager import filters_manager
    print("✅ filters_manager importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar filters_manager: {e}")

try:
    from modules.charts_manager import charts_manager
    print("✅ charts_manager importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar charts_manager: {e}")

try:
    from utils.formatters import format_currency, format_percentage
    print("✅ formatters importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar formatters: {e}")

print("Teste concluído!") 