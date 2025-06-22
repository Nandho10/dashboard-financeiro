# -*- coding: utf-8 -*-
"""
Dashboard Financeiro Modular - Versão 2.0
Sistema de Gestão Financeira Pessoal com arquitetura modular
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import warnings
warnings.filterwarnings('ignore')

# Importar módulos
from modules.data_manager import data_manager
from modules.filters_manager import filters_manager
from modules.charts_manager import charts_manager
from modules.forms_manager import forms_manager
from utils.formatters import format_currency, format_percentage, safe_divide
from utils.metrics_manager import render_metric_card

# Importar sistemas CRUD e Backup
from crud_system import CRUDSystem, create_editable_table, format_dataframe_for_display
from backup_system import BackupSystem, safe_backup

# Configuração da página
st.set_page_config(
    page_title="Dashboard Financeiro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
try:
    with open('custom.css', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    # CSS de debug para sidebar
    with open('sidebar_debug.css', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass  # Não exibe aviso se o arquivo custom.css não for encontrado

def get_col(df, *options):
    """Retorna o nome da coluna existente entre as opções fornecidas."""
    for opt in options:
        if opt in df.columns:
            return opt
    return None

def initialize_session_state():
    """Inicializa o session_state para controlar a visibilidade dos formulários CRUD."""
    sheets_with_crud = ['Despesas', 'Receitas', 'Vendas', 'Investimentos', 'Div_CC']
    for sheet in sheets_with_crud:
        if f"show_edit_{sheet}" not in st.session_state:
            st.session_state[f"show_edit_{sheet}"] = False
        if f"show_delete_{sheet}" not in st.session_state:
            st.session_state[f"show_delete_{sheet}"] = False
        if f"show_bulk_delete_{sheet}" not in st.session_state:
            st.session_state[f"show_bulk_delete_{sheet}"] = False
        if f"selected_row_{sheet}" not in st.session_state:
            st.session_state[f"selected_row_{sheet}"] = None
        if f"selected_rows_{sheet}" not in st.session_state:
            st.session_state[f"selected_rows_{sheet}"] = []

# --- Caminho para o arquivo de dados ---
EXCEL_PATH = 'Base_financas.xlsx'

def main():
    """Função principal que renderiza a página do Streamlit."""
    initialize_session_state()

    st.set_page_config(
        page_title="Dashboard Financeiro Modular",
        page_icon="💲",
        layout="wide"
    )

    # --- INICIALIZAÇÃO DOS SISTEMAS ---
    backup_system = BackupSystem(EXCEL_PATH)
    crud_system = CRUDSystem(EXCEL_PATH)

    # Carrega os dados uma vez
    df_receitas = data_manager.load_excel_data("Receitas")
    df_despesas = data_manager.load_excel_data("Despesas")
    df_cartao = data_manager.load_excel_data("Div_CC")
    df_vendas = data_manager.load_excel_data("Vendas")
    df_investimentos = data_manager.load_excel_data("Investimentos")
    
    # Renderiza a sidebar e obtém os filtros
    filters = filters_manager.setup_sidebar_filters()
    
    # Menu de navegação
    menu_options = [
        "📊 Visão Geral",
        "💸 Despesas", 
        "💰 Receitas",
        "🛒 Vendas",
        "💳 Cartão de Crédito",
        "💰 Investimentos",
        "📋 Orçamento",
        "📈 Análises"
    ]
    selected = st.sidebar.selectbox("Navegação", options=menu_options, index=0)
    
    # Carregar dados
    receitas = data_manager.load_excel_data("Receitas")
    despesas = data_manager.load_excel_data("Despesas")
    cc_data = data_manager.load_excel_data("Div_CC")
    vendas = data_manager.load_excel_data("Vendas")
    investimentos = data_manager.load_excel_data("Investimentos")
    orcamento = data_manager.load_excel_data("Orcamento")
    
    # Aplicar filtros
    receitas_filtradas = filters_manager.apply_filters_to_data(receitas, filters)
    despesas_filtradas = filters_manager.apply_filters_to_data(despesas, filters)
    cc_filtrado = filters_manager.apply_filters_to_data(cc_data, filters)
    vendas_filtradas = filters_manager.apply_filters_to_data(vendas, filters)
    investimentos_filtrados = filters_manager.apply_filters_to_data(investimentos, filters)
    
    st.sidebar.markdown("---")
    
    # --- SEÇÃO DE GERENCIAMENTO DE BACKUP ---
    st.sidebar.markdown("### 💾 Gerenciamento de Backup")
    col_backup1, col_backup2 = st.sidebar.columns(2)
    
    with col_backup1:
        if st.button("🔄 Criar Backup", use_container_width=True):
            success, message = safe_backup("manual")
            if success:
                st.sidebar.success("Backup criado!")
            else:
                st.sidebar.error(f"Erro: {message}")
    
    with col_backup2:
        if st.button("📋 Listar Backups", use_container_width=True):
            backups = backup_system.list_backups()
            if backups:
                st.sidebar.write("**Backups disponíveis:**")
                for backup in backups[:3]:  # Mostra apenas os 3 mais recentes
                    st.sidebar.write(f"📁 {backup['filename']} ({backup['date'].strftime('%d/%m/%Y %H:%M')})")
            else:
                st.sidebar.info("Nenhum backup encontrado.")
    
    # Opção para restaurar backup
    backups = backup_system.list_backups()
    if backups:
        backup_options = [f"{b['filename']} ({b['date'].strftime('%d/%m/%Y %H:%M')})" for b in backups[:3]]
        selected_backup = st.sidebar.selectbox("Selecionar backup para restaurar:", backup_options, key="backup_restore")
        
        if st.sidebar.button("🔄 Restaurar Backup", use_container_width=True):
            if selected_backup:
                backup_filename = selected_backup.split(" (")[0]
                backup_path = f"backups/{backup_filename}"
                success, message = backup_system.restore_backup(backup_path)
                if success:
                    st.sidebar.success("Backup restaurado! Recarregue a página.")
                    st.rerun()
                else:
                    st.sidebar.error(f"Erro: {message}")
    
    st.sidebar.markdown("---")
    
    # Navegação
    if selected == "📊 Visão Geral":
        show_overview(receitas_filtradas, despesas_filtradas, filters)
    elif selected == "💸 Despesas":
        show_expenses(despesas_filtradas, filters, crud_system, forms_manager())
    elif selected == "💰 Receitas":
        show_revenues(receitas_filtradas, filters)
    elif selected == "🛒 Vendas":
        show_sales(vendas_filtradas, filters)
    elif selected == "💳 Cartão de Crédito":
        show_credit_card(cc_filtrado, filters)
    elif selected == "💰 Investimentos":
        show_investments(investimentos_filtrados, filters)
    elif selected == "📋 Orçamento":
        show_budget(receitas_filtradas, despesas_filtradas, orcamento, filters)
    elif selected == "📈 Análises":
        show_analytics(receitas_filtradas, despesas_filtradas, filters)

def show_overview(receitas, despesas, filters):
    st.markdown("## 📊 Visão Geral")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    total_receitas = receitas["VALOR"].sum() if "VALOR" in receitas.columns and not receitas.empty else 0
    total_despesas = despesas["VALOR"].sum() if "VALOR" in despesas.columns and not despesas.empty else 0
    saldo = total_receitas + total_despesas
    
    with col1:
        render_metric_card(
            title="Total Receitas",
            value=format_currency(total_receitas),
            icon="💰"
        )
    with col2:
        render_metric_card(
            title="Total Despesas",
            value=format_currency(total_despesas),
            icon="💸"
        )
    with col3:
        render_metric_card(
            title="Saldo",
            value=format_currency(saldo),
            icon="💵"
        )
    with col4:
        percentual_despesas = (abs(total_despesas) / total_receitas) * 100 if total_receitas > 0 else 0
        render_metric_card(
            title="% Desp./Rec.",
            value=f"{percentual_despesas:.1f}%",
            icon="📊"
        )
    
    # Gráficos de rosca "Top 5"
    st.markdown("### Top 5 Despesas")
    col_pie1, col_pie2, col_pie3 = st.columns(3)

    if not despesas.empty and "VALOR" in despesas.columns:
        despesas_abs = despesas.copy()
        despesas_abs['VALOR'] = despesas_abs['VALOR'].abs()
        # Top 5 por categoria
        with col_pie1:
            top_categorias = despesas_abs.groupby("CATEGORIA")["VALOR"].sum().sort_values(ascending=False).head(5).reset_index()
            fig_categorias = charts_manager.create_pie_chart(
                top_categorias, "VALOR", "CATEGORIA", "Top 5 Categorias de Despesas", hole=0.5, showlegend=True
            )
            st.plotly_chart(fig_categorias, use_container_width=True)
        # Top 5 por descrição
        with col_pie2:
            # Garante que a coluna 'DESCRIÇÃO' exista e renomeia se necessário
            if 'DESCRIÇÃO' not in despesas_abs.columns and 'DESCRICAO' in despesas_abs.columns:
                despesas_abs = despesas_abs.rename(columns={'DESCRICAO': 'DESCRIÇÃO'})
            
            if 'DESCRIÇÃO' in despesas_abs.columns:
                # Remove valores nulos ou vazios da descrição antes de agrupar
                df_desc = despesas_abs.dropna(subset=['DESCRIÇÃO'])
                df_desc = df_desc[df_desc['DESCRIÇÃO'].str.strip() != '']
                
                top_descricoes = df_desc.groupby('DESCRIÇÃO')["VALOR"].sum().sort_values(ascending=False).head(5).reset_index()
                
                fig_descricoes = charts_manager.create_pie_chart(
                    top_descricoes, "VALOR", 'DESCRIÇÃO', "Top 5 Descrições de Despesas", hole=0.5, showlegend=True
                )
                st.plotly_chart(fig_descricoes, use_container_width=True)
        # Top 5 por favorecido
        with col_pie3:
            if 'FAVORECIDO' in despesas_abs.columns:
                # Remove valores nulos ou vazios antes de agrupar
                df_fav = despesas_abs.dropna(subset=['FAVORECIDO'])
                df_fav = df_fav[df_fav['FAVORECIDO'].str.strip() != '']

                top_favorecido = df_fav.groupby('FAVORECIDO')["VALOR"].sum().sort_values(ascending=False).head(5).reset_index()
                fig_favorecido = charts_manager.create_pie_chart(
                    top_favorecido, "VALOR", 'FAVORECIDO', "Top 5 Despesas por Favorecido", hole=0.5, showlegend=True
                )
                st.plotly_chart(fig_favorecido, use_container_width=True)
        
        # Evolução temporal
        if "DATA" in despesas.columns:
            despesas_copy = despesas_abs.copy()
            despesas_copy["Mes"] = pd.to_datetime(despesas_copy["DATA"], errors='coerce').dt.strftime("%Y-%m")
            despesas_mensais = despesas_copy.groupby("Mes")["VALOR"].sum().reset_index()
            fig_temporal = charts_manager.create_line_chart(
                despesas_mensais, "Mes", "VALOR", "Evolução das Despesas por Mês"
            )
            st.plotly_chart(fig_temporal, use_container_width=True)
    
    # Resumo das transações
    st.markdown("### 📋 Resumo das Transações")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💰 Últimas Receitas")
        if not receitas.empty:
            receitas_display = receitas.head(10).copy()
            if "DATA" in receitas_display.columns:
                receitas_display["DATA"] = pd.to_datetime(receitas_display["DATA"], errors='coerce')
                receitas_display["DATA"] = receitas_display["DATA"].dt.strftime("%d/%m/%Y")
            if "VALOR" in receitas_display.columns:
                receitas_display["VALOR"] = receitas_display["VALOR"].apply(format_currency)
            st.dataframe(receitas_display, use_container_width=True)
        else:
            st.info("Nenhuma receita encontrada.")
    
    with col2:
        st.markdown("#### 💸 Últimas Despesas")
        if not despesas.empty:
            despesas_display = despesas.head(10).copy()
            if "DATA" in despesas_display.columns:
                despesas_display["DATA"] = pd.to_datetime(despesas_display["DATA"], errors='coerce')
                despesas_display["DATA"] = despesas_display["DATA"].dt.strftime("%d/%m/%Y")
            if "VALOR" in despesas_display.columns:
                despesas_display["VALOR"] = despesas_display["VALOR"].apply(format_currency)
            st.dataframe(despesas_display, use_container_width=True)
        else:
            st.info("Nenhuma despesa encontrada.")

def show_expenses(despesas, filters, crud_system, forms_manager):
    st.markdown("## 💸 Análise de Despesas")

    # --- BOTÕES DE AÇÃO UNIFICADOS ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Nova Despesa", type="primary", use_container_width=True):
            st.session_state.show_expense_form = not st.session_state.get("show_expense_form", False)
            st.session_state.show_edit_Despesas = False
            st.session_state.show_delete_Despesas = False
            st.session_state.show_bulk_delete_Despesas = False
    with col2:
        if st.button("✏️ Editar", use_container_width=True):
            st.session_state.show_edit_Despesas = not st.session_state.get("show_edit_Despesas", False)
            st.session_state.show_expense_form = False
            st.session_state.show_delete_Despesas = False
            st.session_state.show_bulk_delete_Despesas = False
    with col3:
        if st.button("🗑️ Excluir", use_container_width=True):
            st.session_state.show_delete_Despesas = not st.session_state.get("show_delete_Despesas", False)
            st.session_state.show_expense_form = False
            st.session_state.show_edit_Despesas = False
            st.session_state.show_bulk_delete_Despesas = False
    with col4:
        if st.button("🗑️ Excl. em Lote", use_container_width=True):
            st.session_state.show_bulk_delete_Despesas = not st.session_state.get("show_bulk_delete_Despesas", False)
            st.session_state.show_expense_form = False
            st.session_state.show_edit_Despesas = False
            st.session_state.show_delete_Despesas = False
    
    st.divider()

    # Tabela de transações (agora renderizada antes dos formulários)
    st.markdown("### 📋 Transações")
    if not despesas.empty:
        despesas_crud = despesas.copy()
        if 'DESCRICAO' in despesas_crud.columns and 'DESCRIÇÃO' not in despesas_crud.columns:
            despesas_crud = despesas_crud.rename(columns={'DESCRICAO': 'DESCRIÇÃO'})
        
        df_display = format_dataframe_for_display(despesas_crud, "Despesas")
        create_editable_table(df_display, "Despesas", crud_system)
    else:
        st.info("Nenhuma despesa encontrada para o período selecionado.")

    st.divider()

    # --- LÓGICA PARA EXIBIR FORMULÁRIOS (agora renderizada depois da tabela) ---
    if st.session_state.get("show_expense_form", False):
        forms_manager.create_expense_form()

    if st.session_state.get("show_edit_Despesas", False):
        forms_manager.render_edit_expense_form(despesas, crud_system)

    if st.session_state.get("show_delete_Despesas", False):
        forms_manager.render_delete_expense_form(despesas, crud_system)

    if st.session_state.get("show_bulk_delete_Despesas", False):
        forms_manager.render_bulk_delete_expense_form(despesas, crud_system)

def show_revenues(receitas, filters):
    st.markdown("## 💰 Análise de Receitas")
    
    # Botões CRUD
    col_crud1, col_crud2, col_crud3, col_crud4 = st.columns(4)
    with col_crud1:
        if st.button("➕ Nova Receita", type="primary", use_container_width=True):
            st.session_state.show_revenue_form = True
    with col_crud2:
        if st.button("✏️ Editar", use_container_width=True):
            st.session_state.show_edit_Receitas = True
    with col_crud3:
        if st.button("🗑️ Excluir", use_container_width=True):
            st.session_state.show_delete_Receitas = True
    with col_crud4:
        if st.button("🗑️ Exclusão em Lote", use_container_width=True):
            st.session_state.show_bulk_delete_Receitas = True
    
    # Formulário de nova receita
    if st.session_state.get("show_revenue_form", False):
        with st.expander("💰 Nova Receita", expanded=True):
            forms_manager.create_revenue_form()
            if st.button("❌ Fechar"):
                st.session_state.show_revenue_form = False
                st.rerun()
    
    if not receitas.empty and "VALOR" in receitas.columns:
        # Indicadores
        total_receitas = receitas["VALOR"].sum()
        num_receitas = len(receitas)
        valor_medio = total_receitas / num_receitas if num_receitas > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Receitas", format_currency(total_receitas))
        with col2:
            st.metric("Nº de Receitas", num_receitas)
        with col3:
            st.metric("Valor Médio", format_currency(valor_medio))
        
        # Gráficos
        col1, col2 = st.columns(2)
        with col1:
            receitas_por_categoria = receitas.groupby("CATEGORIA")["VALOR"].sum().reset_index()
            fig_categoria = charts_manager.create_pie_chart(
                receitas_por_categoria, "VALOR", "CATEGORIA", "Receitas por Categoria"
            )
            st.plotly_chart(fig_categoria, use_container_width=True)
        
        with col2:
            if "FORMA_RECEBIMENTO" in receitas.columns:
                receitas_por_recebimento = receitas.groupby("FORMA_RECEBIMENTO")["VALOR"].sum().reset_index()
                fig_recebimento = charts_manager.create_pie_chart(
                    receitas_por_recebimento, "VALOR", "FORMA_RECEBIMENTO", "Receitas por Forma de Recebimento"
                )
                st.plotly_chart(fig_recebimento, use_container_width=True)
    
    st.markdown("### 📋 Transações")
    if not receitas.empty:
        receitas_display = receitas.copy()
        if "DATA" in receitas_display.columns:
            receitas_display["DATA"] = pd.to_datetime(receitas_display["DATA"], errors='coerce')
            receitas_display["DATA"] = receitas_display["DATA"].dt.strftime("%d/%m/%Y")
        if "VALOR" in receitas_display.columns:
            receitas_display["VALOR"] = receitas_display["VALOR"].apply(format_currency)
        st.dataframe(receitas_display, use_container_width=True)
    else:
        st.info("Nenhuma receita encontrada para o período selecionado.")

def show_credit_card(cc_data, filters):
    st.markdown("## 💳 Análise do Cartão de Crédito")
    
    # Botões CRUD
    col_crud1, col_crud2, col_crud3, col_crud4 = st.columns(4)
    with col_crud1:
        if st.button("➕ Nova Despesa CC", type="primary", use_container_width=True):
            st.session_state.show_credit_card_form = True
    with col_crud2:
        if st.button("✏️ Editar", use_container_width=True):
            st.session_state.show_edit_Div_CC = True
    with col_crud3:
        if st.button("🗑️ Excluir", use_container_width=True):
            st.session_state.show_delete_Div_CC = True
    with col_crud4:
        if st.button("🗑️ Exclusão em Lote", use_container_width=True):
            st.session_state.show_bulk_delete_Div_CC = True
    
    # Formulário de nova despesa no cartão
    if st.session_state.get("show_credit_card_form", False):
        with st.expander("💳 Nova Despesa no Cartão", expanded=True):
            forms_manager.create_credit_card_form()
            if st.button("❌ Fechar"):
                st.session_state.show_credit_card_form = False
                st.rerun()
    
    if not cc_data.empty and "VALOR" in cc_data.columns:
        # Indicadores
        total_cc = cc_data["VALOR"].sum()
        num_transacoes = len(cc_data)
        valor_medio = total_cc / num_transacoes if num_transacoes > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total no Cartão", format_currency(total_cc))
        with col2:
            st.metric("Nº de Transações", num_transacoes)
        with col3:
            st.metric("Valor Médio", format_currency(valor_medio))
        
        # Gráficos
        col1, col2 = st.columns(2)
        with col1:
            cc_por_categoria = cc_data.groupby("CATEGORIA")["VALOR"].sum().reset_index()
            fig_categoria = charts_manager.create_pie_chart(
                cc_por_categoria, "VALOR", "CATEGORIA", "Despesas no Cartão por Categoria"
            )
            st.plotly_chart(fig_categoria, use_container_width=True)
        
        with col2:
            if "CARTAO" in cc_data.columns:
                cc_por_cartao = cc_data.groupby("CARTAO")["VALOR"].sum().reset_index()
                fig_cartao = charts_manager.create_pie_chart(
                    cc_por_cartao, "VALOR", "CARTAO", "Despesas por Cartão"
                )
                st.plotly_chart(fig_cartao, use_container_width=True)
    
    st.markdown("### 📋 Transações")
    if not cc_data.empty:
        cc_display = cc_data.copy()
        if "DATA" in cc_display.columns:
            cc_display["DATA"] = pd.to_datetime(cc_display["DATA"], errors='coerce')
            cc_display["DATA"] = cc_display["DATA"].dt.strftime("%d/%m/%Y")
        if "VALOR" in cc_display.columns:
            cc_display["VALOR"] = cc_display["VALOR"].apply(format_currency)
        st.dataframe(cc_display, use_container_width=True)
    else:
        st.info("Nenhuma transação no cartão encontrada para o período selecionado.")

def show_budget(receitas, despesas, orcamento, filters):
    st.markdown("## 📋 Análise do Orçamento")
    
    # Calcular renda líquida (receitas - despesas)
    renda_liquida = receitas["VALOR"].sum() if not receitas.empty and "VALOR" in receitas.columns else 0
    
    # Métricas do orçamento
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Renda Líquida", format_currency(renda_liquida))
    with col2:
        total_gasto = despesas["VALOR"].sum() if not despesas.empty and "VALOR" in despesas.columns else 0
        st.metric("💸 Total Gasto", format_currency(total_gasto))
    with col3:
        total_orcado = renda_liquida
        st.metric("📊 Total Orçado", format_currency(total_orcado))
    
    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        orcamento_por_categoria = orcamento.copy()
        orcamento_por_categoria["Valor_Orcado"] = (orcamento_por_categoria["Percentual"] / 100) * renda_liquida
        fig_orcado = charts_manager.create_pie_chart(
            orcamento_por_categoria, "Valor_Orcado", "CATEGORIA", "Distribuição Orçada por Categoria"
        )
        st.plotly_chart(fig_orcado, use_container_width=True)
    with col2:
        if not despesas.empty and "VALOR" in despesas.columns:
            despesas_por_categoria = despesas.groupby("CATEGORIA")["VALOR"].sum().reset_index()
            fig_real = charts_manager.create_pie_chart(
                despesas_por_categoria, "VALOR", "CATEGORIA", "Distribuição Real dos Gastos"
            )
            st.plotly_chart(fig_real, use_container_width=True)
    
    # Comparativo
    if not despesas.empty and "VALOR" in despesas.columns:
        st.markdown("### 📊 Comparativo Orçado vs. Gasto")
        comparativo = orcamento.copy()
        comparativo["Valor_Orcado"] = (comparativo["Percentual"] / 100) * renda_liquida
        despesas_por_categoria = despesas.groupby("CATEGORIA")["VALOR"].sum()
        comparativo["Valor_Gasto"] = comparativo["CATEGORIA"].map(despesas_por_categoria).fillna(0)
        comparativo["Saldo"] = comparativo["Valor_Orcado"] - comparativo["Valor_Gasto"]
        comparativo["Percentual_Uso"] = (comparativo["Valor_Gasto"] / comparativo["Valor_Orcado"]) * 100
        comparativo["Percentual_Uso"] = comparativo["Percentual_Uso"].fillna(0)
        
        fig_comparativo = charts_manager.create_comparison_chart(
            comparativo, "CATEGORIA", ["Valor_Orcado", "Valor_Gasto"], "Comparativo Orçado vs. Gasto por Categoria"
        )
        st.plotly_chart(fig_comparativo, use_container_width=True)
        
        st.markdown("### 📋 Acompanhamento do Orçamento")
        acompanhamento = comparativo.copy()
        acompanhamento["Valor_Orcado"] = acompanhamento["Valor_Orcado"].apply(format_currency)
        acompanhamento["Valor_Gasto"] = acompanhamento["Valor_Gasto"].apply(format_currency)
        acompanhamento["Saldo"] = acompanhamento["Saldo"].apply(format_currency)
        acompanhamento["Percentual_Uso"] = acompanhamento["Percentual_Uso"].apply(format_percentage)
        acompanhamento["Percentual"] = acompanhamento["Percentual"].apply(format_percentage)
        st.dataframe(acompanhamento, use_container_width=True)

def show_sales(vendas, filters):
    st.markdown("## 🛒 Análise de Vendas")
    
    # Botões CRUD
    col_crud1, col_crud2, col_crud3, col_crud4 = st.columns(4)
    with col_crud1:
        if st.button("➕ Nova Venda", type="primary", use_container_width=True):
            st.session_state.show_sale_form = True
    with col_crud2:
        if st.button("✏️ Editar", use_container_width=True):
            st.session_state.show_edit_Vendas = True
    with col_crud3:
        if st.button("🗑️ Excluir", use_container_width=True):
            st.session_state.show_delete_Vendas = True
    with col_crud4:
        if st.button("🗑️ Exclusão em Lote", use_container_width=True):
            st.session_state.show_bulk_delete_Vendas = True
    
    # Formulário de nova venda
    if st.session_state.get("show_sale_form", False):
        with st.expander("🛒 Nova Venda", expanded=True):
            forms_manager.create_sale_form()
            if st.button("❌ Fechar"):
                st.session_state.show_sale_form = False
                st.rerun()
    
    if not vendas.empty and "VALOR" in vendas.columns:
        # Indicadores
        total_vendido = vendas["VALOR"].sum()
        num_vendas = len(vendas)
        ticket_medio = total_vendido / num_vendas if num_vendas > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Vendido", format_currency(total_vendido))
        with col2:
            st.metric("Nº de Vendas", num_vendas)
        with col3:
            st.metric("Ticket Médio", format_currency(ticket_medio))
        
        st.markdown("### 📊 Resumo por Cliente")
        vendas_por_cliente = vendas.groupby("Cliente").agg({"VALOR": ["sum", "count", "mean"]}).round(2)
        vendas_por_cliente.columns = ["Total", "Quantidade", "Média"]
        vendas_por_cliente = vendas_por_cliente.sort_values("Total", ascending=False)
        vendas_por_cliente["Total"] = vendas_por_cliente["Total"].apply(format_currency)
        vendas_por_cliente["Média"] = vendas_por_cliente["Média"].apply(format_currency)
        st.dataframe(vendas_por_cliente, use_container_width=True)
        
        # Gráfico de pizza
        fig_pizza = charts_manager.create_pie_chart(
            vendas.groupby("Cliente")["VALOR"].sum().reset_index(), 
            "VALOR", "Cliente", "Vendas por Cliente"
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    st.markdown("### 📋 Transações")
    if not vendas.empty:
        vendas_display = vendas.copy()
        if "DATA" in vendas_display.columns:
            vendas_display["DATA"] = pd.to_datetime(vendas_display["DATA"], errors='coerce')
            vendas_display["DATA"] = vendas_display["DATA"].dt.strftime("%d/%m/%Y")
        if "VALOR" in vendas_display.columns:
            vendas_display["VALOR"] = vendas_display["VALOR"].apply(format_currency)
        st.dataframe(vendas_display, use_container_width=True)
    else:
        st.info("Nenhuma venda encontrada para o período selecionado.")

def show_investments(investimentos, filters):
    st.markdown("## 💰 Análise de Investimentos")
    
    # Botões CRUD
    col_crud1, col_crud2, col_crud3, col_crud4 = st.columns(4)
    with col_crud1:
        if st.button("➕ Novo Investimento", type="primary", use_container_width=True):
            st.session_state.show_investment_form = True
    with col_crud2:
        if st.button("✏️ Editar", use_container_width=True):
            st.session_state.show_edit_Investimentos = True
    with col_crud3:
        if st.button("🗑️ Excluir", use_container_width=True):
            st.session_state.show_delete_Investimentos = True
    with col_crud4:
        if st.button("🗑️ Exclusão em Lote", use_container_width=True):
            st.session_state.show_bulk_delete_Investimentos = True
    
    # Formulário de novo investimento
    if st.session_state.get("show_investment_form", False):
        with st.expander("💰 Novo Investimento", expanded=True):
            forms_manager.create_investment_form()
            if st.button("❌ Fechar"):
                st.session_state.show_investment_form = False
                st.rerun()
    
    if not investimentos.empty and "VALOR_APORTE" in investimentos.columns:
        # Indicadores
        total_investido = investimentos["VALOR_APORTE"].sum()
        num_aportes = len(investimentos)
        valor_medio_aporte = total_investido / num_aportes if num_aportes > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Investido", format_currency(total_investido))
        with col2:
            st.metric("Nº de Aportes", num_aportes)
        with col3:
            st.metric("Valor Médio", format_currency(valor_medio_aporte))
        
        st.markdown("### 📊 Resumo por Ativo")
        investimentos_por_ativo = investimentos.groupby("ATIVO").agg({"VALOR_APORTE": ["sum", "count", "mean"]}).round(2)
        investimentos_por_ativo.columns = ["Total", "Quantidade", "Média"]
        investimentos_por_ativo = investimentos_por_ativo.sort_values("Total", ascending=False)
        investimentos_por_ativo["Total"] = investimentos_por_ativo["Total"].apply(format_currency)
        investimentos_por_ativo["Média"] = investimentos_por_ativo["Média"].apply(format_currency)
        st.dataframe(investimentos_por_ativo, use_container_width=True)
        
        # Gráfico de pizza
        fig_pizza = charts_manager.create_pie_chart(
            investimentos.groupby("ATIVO")["VALOR_APORTE"].sum().reset_index(), 
            "VALOR_APORTE", "ATIVO", "Investimentos por Ativo"
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    st.markdown("### 📋 Transações")
    if not investimentos.empty:
        investimentos_display = investimentos.copy()
        if "DATA" in investimentos_display.columns:
            investimentos_display["DATA"] = pd.to_datetime(investimentos_display["DATA"], errors='coerce')
            investimentos_display["DATA"] = investimentos_display["DATA"].dt.strftime("%d/%m/%Y")
        if "VALOR_APORTE" in investimentos_display.columns:
            investimentos_display["VALOR_APORTE"] = investimentos_display["VALOR_APORTE"].apply(format_currency)
        st.dataframe(investimentos_display, use_container_width=True)
    else:
        st.info("Nenhum investimento encontrado para o período selecionado.")

def show_analytics(receitas, despesas, filters):
    st.markdown("## 📈 Análises Avançadas")
    
    st.markdown("### 📅 Análise Temporal")
    if not despesas.empty and "VALOR" in despesas.columns and "DATA" in despesas.columns:
        despesas_copy = despesas.copy()
        despesas_copy["Mes"] = pd.to_datetime(despesas_copy["DATA"], errors='coerce').dt.strftime("%Y-%m")
        despesas_mensais = despesas_copy.groupby("Mes")["VALOR"].sum().reset_index()
        fig_temporal = charts_manager.create_line_chart(
            despesas_mensais, "Mes", "VALOR", "Evolução das Despesas por Mês"
        )
        st.plotly_chart(fig_temporal, use_container_width=True)
    
    st.markdown("### 📂 Análise de Categorias")
    if not despesas.empty and "VALOR" in despesas.columns:
        top_categorias = despesas.groupby("CATEGORIA")["VALOR"].sum().sort_values(ascending=False).head(10)
        fig_top = charts_manager.create_bar_chart(
            top_categorias.reset_index(), "CATEGORIA", "VALOR", "Top 10 Categorias de Despesas", orientation="h"
        )
        st.plotly_chart(fig_top, use_container_width=True)

if __name__ == "__main__":
    main() 