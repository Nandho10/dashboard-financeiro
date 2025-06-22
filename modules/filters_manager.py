# -*- coding: utf-8 -*-
"""
Módulo de Gerenciamento de Filtros
Responsável por configurar e aplicar filtros no dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from modules.data_manager import data_manager  # Importação local para evitar dependência circular

class FiltersManager:
    def __init__(self):
        self.excel_file = "Base_financas.xlsx"
    
    def setup_sidebar_filters(self):
        """Configura os filtros na sidebar e gerencia o estado usando st.session_state."""
        st.sidebar.markdown("## 🔍 Filtros")

        periodo_options = ["Todos", "Último mês", "Últimos 3 meses", "Últimos 6 meses", "Último ano", "Personalizado"]
        categorias = self.get_available_categories()
        categoria_options = ["Todas"] + categorias

        # Inicializa o estado dos filtros na primeira execução
        if 'filters' not in st.session_state:
            st.session_state.filters = {
                "periodo": "Todos",
                "data_inicio": date(datetime.now().year, 1, 1),
                "data_fim": date.today(),
                "categoria": "Todas",
                "valor_min": 0.0,
                "valor_max": 10000.0
            }

        # Garante que os valores no estado são válidos para as opções atuais
        if st.session_state.filters.get("periodo") not in periodo_options:
            st.session_state.filters["periodo"] = "Todos"
        if st.session_state.filters.get("categoria") not in categoria_options:
            st.session_state.filters["categoria"] = "Todas"

        # --- UI dos Filtros ---
        st.sidebar.markdown("### 📅 Período")
        st.session_state.filters["periodo"] = st.sidebar.selectbox(
            "Selecione o período:",
            periodo_options,
            index=periodo_options.index(st.session_state.filters["periodo"])
        )
        
        data_inicio = st.session_state.filters["data_inicio"]
        data_fim = st.session_state.filters["data_fim"]

        if st.session_state.filters["periodo"] == "Personalizado":
            col1, col2 = st.sidebar.columns(2)
            with col1:
                data_inicio = st.date_input("Data Início", value=st.session_state.filters["data_inicio"])
            with col2:
                data_fim = st.date_input("Data Fim", value=st.session_state.filters["data_fim"])
        
        st.sidebar.markdown("### 📂 Categoria")
        categoria_selecionada = st.sidebar.selectbox(
            "Selecione a categoria:", 
            categoria_options, 
            index=categoria_options.index(st.session_state.filters["categoria"])
        )
        
        st.sidebar.markdown("### 💰 Valor")
        valor_min = st.sidebar.number_input("Valor mínimo:", min_value=0.0, value=st.session_state.filters["valor_min"], step=0.01)
        valor_max = st.sidebar.number_input("Valor máximo:", min_value=0.0, value=st.session_state.filters["valor_max"], step=0.01)
        
        # Atualiza o session_state com os valores atuais dos widgets
        st.session_state.filters.update({
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "categoria": categoria_selecionada,
            "valor_min": valor_min,
            "valor_max": valor_max
        })

        return st.session_state.filters
    
    def get_available_categories(self):
        """Obtém as categorias disponíveis no arquivo Excel"""
        try:
            # Carregar dados usando o data_manager para consistência
            receitas = data_manager.load_excel_data("Receitas")
            despesas = data_manager.load_excel_data("Despesas")
            
            categorias_receitas = receitas["CATEGORIA"].dropna().unique().tolist() if not receitas.empty and "CATEGORIA" in receitas.columns else []
            categorias_despesas = despesas["CATEGORIA"].dropna().unique().tolist() if not despesas.empty and "CATEGORIA" in despesas.columns else []
            
            # Combinar, remover duplicatas e ordenar
            todas_categorias = sorted(list(set(categorias_receitas + categorias_despesas)))
            return todas_categorias
        except Exception as e:
            st.error(f"Erro ao carregar categorias: {e}")
            return []
    
    def apply_filters_to_data(self, data, filters):
        """Aplica os filtros aos dados"""
        if data.empty:
            return data
        
        filtered_data = data.copy()
        
        if "DATA" not in filtered_data.columns:
            return filtered_data 
            
        filtered_data["DATA"] = pd.to_datetime(filtered_data["DATA"], errors='coerce')
        filtered_data.dropna(subset=["DATA"], inplace=True)

        if filtered_data.empty:
            return filtered_data

        # Define a data de referência como a data mais recente nos dados, com fallback para hoje
        today = filtered_data["DATA"].max() if not filtered_data.empty else datetime.now()

        # Filtro de período
        if filters["periodo"] != "Todos":
            if filters["periodo"] == "Último mês":
                data_limite = today - pd.DateOffset(months=1)
                filtered_data = filtered_data[filtered_data["DATA"] >= data_limite]
            elif filters["periodo"] == "Últimos 3 meses":
                data_limite = today - pd.DateOffset(months=3)
                filtered_data = filtered_data[filtered_data["DATA"] >= data_limite]
            elif filters["periodo"] == "Últimos 6 meses":
                data_limite = today - pd.DateOffset(months=6)
                filtered_data = filtered_data[filtered_data["DATA"] >= data_limite]
            elif filters["periodo"] == "Último ano":
                data_limite = today - pd.DateOffset(years=1)
                filtered_data = filtered_data[filtered_data["DATA"] >= data_limite]
            elif filters["periodo"] == "Personalizado":
                data_inicio = pd.to_datetime(filters.get("data_inicio"))
                data_fim = pd.to_datetime(filters.get("data_fim"))
                if data_inicio and data_fim:
                    filtered_data = filtered_data[
                        (filtered_data["DATA"] >= data_inicio) &
                        (filtered_data["DATA"] <= data_fim)
                    ]
        
        # Filtro de categoria
        if filters["categoria"] != "Todas" and "CATEGORIA" in filtered_data.columns:
            filtered_data = filtered_data[filtered_data["CATEGORIA"] == filters["categoria"]]
        
        # Filtro de valor
        # if filters.get("valor_min") is not None and filters.get("valor_max") is not None:
        #     if "VALOR" in filtered_data.columns:
        #         filtered_data = filtered_data[
        #             (filtered_data["VALOR"] >= filters["valor_min"]) &
        #             (filtered_data["VALOR"] <= filters["valor_max"])
        #         ]
        
        return filtered_data

# Instância global
filters_manager = FiltersManager() 