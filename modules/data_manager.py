"""
Gerenciador de Dados - Módulo centralizado para operações com Excel
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class DataManager:
    """Classe centralizada para gerenciamento de dados do Excel"""
    
    def __init__(self, excel_file: str = "Base_financas.xlsx"):
        """
        Inicializa o gerenciador de dados
        
        Args:
            excel_file: Caminho para o arquivo Excel
        """
        self.excel_file = excel_file
        self._data_cache = {}
        self._last_modified = None
        
    def _check_file_exists(self) -> bool:
        """Verifica se o arquivo Excel existe"""
        if not Path(self.excel_file).exists():
            logger.error(f"Arquivo Excel não encontrado: {self.excel_file}")
            return False
        return True
    
    def load_excel_data(self, sheet_name: str = None) -> pd.DataFrame:
        """
        Carrega dados do Excel com cache e validação
        
        Args:
            sheet_name: Nome da aba (se None, carrega todas)
            
        Returns:
            DataFrame ou dict de DataFrames
        """
        try:
            if not self._check_file_exists():
                return pd.DataFrame()
            
            # Verificar se precisa recarregar (cache expirado ou arquivo modificado)
            current_modified = Path(self.excel_file).stat().st_mtime
            
            if (sheet_name in self._data_cache and 
                self._last_modified == current_modified):
                logger.info(f"Retornando dados em cache para aba: {sheet_name}")
                return self._data_cache[sheet_name]
            
            # Carregar dados, especificando a vírgula como separador decimal
            if sheet_name:
                df = pd.read_excel(self.excel_file, sheet_name=sheet_name, decimal=',')
                self._data_cache[sheet_name] = df
            else:
                # Carregar todas as abas
                excel_data = pd.read_excel(self.excel_file, sheet_name=None, decimal=',')
                for sheet, df in excel_data.items():
                    self._data_cache[sheet] = df
                df = excel_data
            
            self._last_modified = current_modified
            logger.info(f"Dados carregados com sucesso: {sheet_name or 'todas as abas'}")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados do Excel: {e}")
            st.error(f"Erro ao carregar dados: {e}")
            return pd.DataFrame()
    
    def save_data(self, df: pd.DataFrame, sheet_name: str) -> bool:
        """
        Salva dados em uma aba específica
        
        Args:
            df: DataFrame para salvar
            sheet_name: Nome da aba
            
        Returns:
            True se salvou com sucesso
        """
        try:
            # Carregar todas as abas existentes
            with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Limpar cache
            self._data_cache.pop(sheet_name, None)
            self._last_modified = None
            
            logger.info(f"Dados salvos com sucesso na aba: {sheet_name}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {e}")
            st.error(f"Erro ao salvar dados: {e}")
            return False
    
    def get_filtered_data(self, sheet_name: str, filters: Dict = None) -> pd.DataFrame:
        """
        Obtém dados filtrados de uma aba específica
        
        Args:
            sheet_name: Nome da aba
            filters: Dicionário com filtros a aplicar
            
        Returns:
            DataFrame filtrado
        """
        df = self.load_excel_data(sheet_name)
        
        if df.empty or not filters:
            return df
        
        try:
            # Aplicar filtros
            for column, value in filters.items():
                if column in df.columns and value:
                    if isinstance(value, (list, tuple)):
                        df = df[df[column].isin(value)]
                    else:
                        df = df[df[column] == value]
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao aplicar filtros: {e}")
            return df
    
    def get_unique_values(self, sheet_name: str, column: str) -> List:
        """
        Obtém valores únicos de uma coluna
        
        Args:
            sheet_name: Nome da aba
            column: Nome da coluna
            
        Returns:
            Lista de valores únicos
        """
        df = self.load_excel_data(sheet_name)
        
        if df.empty or column not in df.columns:
            return []
        
        try:
            values = df[column].dropna().unique().tolist()
            return sorted(values)
            
        except Exception as e:
            logger.error(f"Erro ao obter valores únicos: {e}")
            return []
    
    def add_row(self, sheet_name: str, data: Dict) -> bool:
        """
        Adiciona uma nova linha aos dados
        
        Args:
            sheet_name: Nome da aba
            data: Dicionário com os dados da nova linha
            
        Returns:
            True se adicionou com sucesso
        """
        try:
            df = self.load_excel_data(sheet_name)
            
            # Adicionar nova linha
            new_row = pd.DataFrame([data])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Salvar dados atualizados
            return self.save_data(df, sheet_name)
            
        except Exception as e:
            logger.error(f"Erro ao adicionar linha: {e}")
            return False
    
    def clear_cache(self):
        """Limpa o cache de dados"""
        self._data_cache.clear()
        self._last_modified = None
        logger.info("Cache limpo")

# Instância global do DataManager
data_manager = DataManager() 