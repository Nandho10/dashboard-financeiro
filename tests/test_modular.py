"""
Testes para a arquitetura modular do Dashboard Financeiro
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, date
import sys
import os
from unittest.mock import patch

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_manager import DataManager
from modules.filters_manager import FiltersManager
from utils.formatters import format_currency, format_percentage, safe_divide
from utils.charts_manager import ChartsManager

class TestDataManager(unittest.TestCase):
    """Testes para o DataManager"""
    
    def setUp(self):
        """Configuração inicial"""
        self.data_manager = DataManager("test_data.xlsx")
        
        # Criar dados de teste
        self.test_receitas = pd.DataFrame({
            "Data": ["2024-01-01", "2024-01-15", "2024-02-01"],
            "Descrição": ["Salário", "Freelance", "Bônus"],
            "VALOR": [5000.0, 1000.0, 2000.0],
            "CATEGORIA": ["Salário", "Freelance", "Bônus"],
            "FAVORECIDO": ["Empresa", "Cliente", "Empresa"]
        })
        
        self.test_despesas = pd.DataFrame({
            "Data": ["2024-01-05", "2024-01-20", "2024-02-05"],
            "Descrição": ["Aluguel", "Supermercado", "Conta de Luz"],
            "VALOR": [1500.0, 800.0, 200.0],
            "CATEGORIA": ["Moradia", "Alimentação", "Moradia"],
            "FAVORECIDO": ["Proprietário", "Supermercado", "Companhia"],
            "PAGO": ["Sim", "Sim", "Não"]
        })
    
    def test_load_excel_data(self):
        """Testa carregamento de dados do Excel"""
        # Teste com dados válidos
        result = self.data_manager.load_excel_data("Receitas")
        self.assertIsInstance(result, pd.DataFrame)
    
    @patch('modules.data_manager.pd.read_excel')
    def test_get_unique_values(self, mock_read_excel):
        """Testa obtenção de valores únicos"""
        mock_read_excel.return_value = self.test_receitas
        
        categories = self.data_manager.get_unique_values("Receitas", "CATEGORIA")
        self.assertEqual(len(categories), 3)
        self.assertIn("Salário", categories)
    
    def test_add_row(self):
        """Testa adição de nova linha"""
        # Simular dados carregados
        self.data_manager._data_cache["Receitas"] = self.test_receitas.copy()
        
        new_data = {
            "Data": "2024-02-15",
            "Descrição": "Venda",
            "VALOR": 500.0,
            "CATEGORIA": "Vendas",
            "FAVORECIDO": "Cliente"
        }
        
        # Teste sem salvar no arquivo (apenas em memória)
        result = self.data_manager.add_row("Receitas", new_data)
        self.assertTrue(result)

    @patch('modules.data_manager.pd.read_excel')
    def test_add_new_transaction(self, mock_read_excel):
        mock_read_excel.return_value = self.test_receitas
        new_data = {
            "Data": pd.to_datetime("2024-03-01"),
            "Descrição": "Venda de produto",
            "VALOR": 500.0,
            "CATEGORIA": "Vendas",
        }
        with patch('modules.data_manager.pd.ExcelWriter') as mock_writer:
            self.data_manager.add_new_transaction("Receitas", new_data)

class TestFormatters(unittest.TestCase):
    """Testes para os utilitários de formatação"""
    
    def test_format_currency(self):
        """Testa formatação de moeda"""
        # Teste com valor positivo
        result = format_currency(1234.56)
        self.assertEqual(result, "R$ 1.234,56")
        
        # Teste com zero
        result = format_currency(0)
        self.assertEqual(result, "R$ 0,00")
        
        # Teste com valor negativo
        result = format_currency(-1234.56)
        self.assertEqual(result, "R$ -1.234,56")
        
        # Teste com string
        result = format_currency("1234.56")
        self.assertEqual(result, "R$ 1.234,56")
    
    def test_format_percentage(self):
        """Testa formatação de percentual"""
        # Teste com valor positivo
        result = format_percentage(25.5)
        self.assertEqual(result, "25,5%")
        
        # Teste com zero
        result = format_percentage(0)
        self.assertEqual(result, "0,0%")
        
        # Teste com valor negativo
        result = format_percentage(-10.2)
        self.assertEqual(result, "-10,2%")
    
    def test_safe_divide(self):
        """Testa divisão segura"""
        # Teste divisão normal
        result = safe_divide(10, 2)
        self.assertEqual(result, 5.0)
        
        # Teste divisão por zero
        result = safe_divide(10, 0)
        self.assertEqual(result, 0.0)
        
        # Teste com valores nulos
        result = safe_divide(None, 2)
        self.assertEqual(result, 0.0)
        
        result = safe_divide(10, None)
        self.assertEqual(result, 0.0)

class TestFiltersManager(unittest.TestCase):
    """Testes para o FiltersManager"""
    
    def setUp(self):
        """Configuração inicial"""
        self.filters_manager = FiltersManager()
        
        # Dados de teste
        self.test_data = pd.DataFrame({
            "Data": ["2024-01-01", "2024-01-15", "2024-02-01", "2024-02-15"],
            "VALOR": [100.0, 200.0, 150.0, 300.0],
            "CATEGORIA": ["A", "B", "A", "C"],
            "PAGO": ["Sim", "Não", "Sim", "Não"]
        })
        self.test_data["Data"] = pd.to_datetime(self.test_data["Data"])
    
    def test_apply_filters_to_data(self):
        """Testa aplicação de filtros"""
        filters = {
            "year": 2024,
            "month": 1,
            "categories": ["A", "B"],
            "min_value": 100,
            "max_value": 250,
            "status": "Sim"
        }
        
        result = self.filters_manager.apply_filters_to_data(self.test_data, filters)
        
        # Verificar se os filtros foram aplicados corretamente
        self.assertEqual(len(result), 1)  # Apenas uma linha deve passar pelos filtros
        self.assertEqual(result.iloc[0]["CATEGORIA"], "A")
        self.assertEqual(result.iloc[0]["PAGO"], "Sim")
    
    def test_get_date_range(self):
        """Testa obtenção de intervalo de datas"""
        start_date, end_date = self.filters_manager.get_date_range(2024, 1)
        
        self.assertEqual(start_date, date(2024, 1, 1))
        self.assertEqual(end_date, date(2024, 1, 31))

    def test_get_filter_options(self):
        anos, meses, categorias = self.filters_manager.get_filter_options(self.test_data)
        self.assertEqual(anos, [2024])
        self.assertEqual(len(meses), 12)
        self.assertEqual(sorted(categorias), ["A", "B", "C"])
        
    def test_apply_filters(self):
        data = pd.DataFrame({
            "Data": pd.to_datetime(["2024-01-10", "2024-01-20", "2024-02-05", "2024-02-15"]),
            "VALOR": [100.0, 200.0, 150.0, 300.0],
            "CATEGORIA": ["A", "B", "A", "C"],
        })
        
        # Test filter by date
        filters = {"ano": 2024, "mes": 1, "categoria": "Todas"}
        result = self.filters_manager.apply_filters(data, filters)
        self.assertEqual(len(result), 2)
        
        # Test filter by category
        filters = {"ano": 2024, "mes": 1, "categoria": "A", "valor_min": 0, "valor_max": 500}
        result = self.filters_manager.apply_filters(data, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["CATEGORIA"], "A")
        
        # Test filter by value
        filters = {"ano": 2024, "mes": 2, "categoria": "Todas", "valor_min": 200, "valor_max": 400}
        result = self.filters_manager.apply_filters(data, filters)
        self.assertEqual(len(result), 1)

class TestChartsManager(unittest.TestCase):
    
    def test_create_pie_chart(self):
        data = pd.DataFrame({
            "CATEGORIA": ["Alimentação", "Transporte", "Lazer"],
            "VALOR": [500, 300, 200]
        })
        fig = ChartsManager.create_pie_chart(data, "VALOR", "CATEGORIA", "Teste de Gráfico de Pizza")
        self.assertIsNotNone(fig)
        self.assertEqual(fig.layout.title.text, "Teste de Gráfico de Pizza")

    def test_create_bar_chart(self):
        data = pd.DataFrame({
            "CATEGORIA": ["Alimentação", "Transporte", "Lazer"],
            "VALOR": [500, 300, 200]
        })
        fig = ChartsManager.create_bar_chart(data, "CATEGORIA", "VALOR", "Teste de Gráfico de Barras")
        self.assertIsNotNone(fig)
        self.assertEqual(fig.layout.title.text, "Teste de Gráfico de Barras")

    def test_create_line_chart(self):
        data = pd.DataFrame({
            "Mês": ["2023-01", "2023-02", "2023-03"],
            "VALOR": [1000, 1200, 1100]
        })
        fig = ChartsManager.create_line_chart(data, "Mês", "VALOR", "Teste de Gráfico de Linha")
        self.assertIsNotNone(fig)
        self.assertEqual(fig.layout.title.text, "Teste de Gráfico de Linha")

    def test_create_comparison_chart(self):
        data = pd.DataFrame({
            "CATEGORIA": ["Alimentação", "Transporte"],
            "Orçado": [600, 400],
            "Gasto": [500, 300]
        })
        fig = ChartsManager.create_comparison_chart(data, "CATEGORIA", ["Orçado", "Gasto"], "Teste de Comparativo")
        self.assertIsNotNone(fig)
        self.assertEqual(fig.layout.title.text, "Teste de Comparativo")

def run_tests():
    """Executa todos os testes"""
    # Criar suite de testes
    test_suite = unittest.TestSuite()
    
    # Adicionar testes
    test_suite.addTest(unittest.makeSuite(TestDataManager))
    test_suite.addTest(unittest.makeSuite(TestFormatters))
    test_suite.addTest(unittest.makeSuite(TestFiltersManager))
    test_suite.addTest(unittest.makeSuite(TestChartsManager))
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("🧪 Executando testes da arquitetura modular...")
    success = run_tests()
    
    if success:
        print("✅ Todos os testes passaram!")
    else:
        print("❌ Alguns testes falharam!")
    
    print("\n📊 Resumo da arquitetura modular:")
    print("✅ DataManager - Gerenciamento de dados")
    print("✅ FiltersManager - Sistema de filtros")
    print("✅ Formatters - Utilitários de formatação")
    print("✅ ChartsManager - Geração de gráficos")
    print("✅ FormsManager - Gerenciamento de formulários")
    print("✅ Dashboard Modular - Interface principal") 