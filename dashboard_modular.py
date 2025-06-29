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
import uuid
warnings.filterwarnings('ignore')

# Importar módulos
from modules.data_manager import data_manager
from modules.filters_manager import filters_manager
from modules.charts_manager import charts_manager
from modules.forms_manager import forms_manager, FormsManager, consultar_despesas
from utils.formatters import format_currency, format_percentage, safe_divide
from utils.metrics_manager import render_metric_card
# KpiManager para calculos de Kpis de Vendas
from utils.kpi_manager import calculate_sales_kpis, get_top_five, calculate_sales_by_weekday, calculate_new_customers

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
        show_overview(receitas_filtradas, despesas_filtradas, vendas_filtradas, vendas)
    elif selected == "💸 Despesas":
        show_expenses(despesas_filtradas, crud_system, forms_manager)
    elif selected == "💰 Receitas":
        show_revenues(receitas_filtradas, filters, crud_system, forms_manager)
    elif selected == "🛒 Vendas":
        show_sales(vendas_filtradas, filters, crud_system, forms_manager)
    elif selected == "💳 Cartão de Crédito":
        show_credit_card(cc_filtrado, filters, crud_system, forms_manager)
    elif selected == "💰 Investimentos":
        show_investments(investimentos_filtrados, filters, crud_system, forms_manager)
    elif selected == "📋 Orçamento":
        show_budget(receitas_filtradas, despesas_filtradas, orcamento, filters)
    elif selected == "📈 Análises":
        show_analytics(receitas_filtradas, despesas_filtradas)

def show_overview(receitas, despesas, vendas, all_vendas):
    st.markdown("## 📊 Visão Geral")
    
    st.markdown("#### **Resumo Financeiro**")
    # Métricas principais
    col1, col2, col3 = st.columns(3)
    
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
            icon="⚖️"
        )
        
    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Análise de Vendas ---
    st.markdown("#### **Análise de Vendas**")
    
    # KPIs de Vendas
    sales_kpis = calculate_sales_kpis(vendas)
    new_customers = calculate_new_customers(all_vendas, vendas)
    
    col_vendas1, col_vendas2, col_vendas3, col_vendas4 = st.columns(4)
    with col_vendas1:
        render_metric_card(
            "Receita de Vendas", 
            format_currency(sales_kpis['revenue']), 
            icon="💲"
        )
    with col_vendas2:
        render_metric_card(
            "Total de Transações", 
            str(sales_kpis['transactions']), 
            icon="🛒"
        )
    with col_vendas3:
        render_metric_card(
            "Ticket Médio", 
            format_currency(sales_kpis['avg_ticket']), 
            icon="🎫"
        )
    with col_vendas4:
        render_metric_card(
            "Novos Clientes", 
            str(new_customers), 
            icon="👤"
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos de Vendas
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Top 5 Clientes
        top_clientes_df = get_top_five(
            vendas, 
            category_col_options=['CLIENTE', 'Cliente', 'Favorecido'],
            value_col_options=['VALOR', 'Valor']
        )
        cliente_col = get_col(top_clientes_df, 'CLIENTE', 'Cliente', 'Favorecido')
        valor_col = get_col(top_clientes_df, 'VALOR', 'Valor')
        
        if cliente_col and valor_col and not top_clientes_df.empty:
            fig_clientes = charts_manager.create_pie_chart(
                top_clientes_df,
                values_col=valor_col,
                names_col=cliente_col,
                title="Top 5 Clientes por Receita",
                hole=0.6 # Donut
            )
            st.plotly_chart(fig_clientes, use_container_width=True)
        else:
            st.info("Sem dados de clientes para exibir no período.")

    with col_chart2:
        # Top 5 Produtos
        top_produtos_df = get_top_five(
            vendas, 
            category_col_options=['PRODUTO'],
            value_col_options=['VALOR', 'Valor']
        )
        produto_col = get_col(top_produtos_df, 'PRODUTO')
        valor_col = get_col(top_produtos_df, 'VALOR', 'Valor')
        
        if produto_col and valor_col and not top_produtos_df.empty:
            fig_produtos = charts_manager.create_top_products_chart(
                top_produtos_df,
                x_col=valor_col,
                y_col=produto_col,
                title="Top 5 Produtos por Receita"
            )
            st.plotly_chart(fig_produtos, use_container_width=True)
        else:
            st.info("Para ver este gráfico, adicione uma coluna 'PRODUTO' na sua planilha 'Vendas'.")

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- Análise de Pagamentos e Dias da Semana ---
    st.markdown("#### **Análise Adicional de Vendas**")
    col_pagto, col_dias = st.columns(2)

    with col_pagto:
        pagamento_col = get_col(vendas, 'TIPO DE RECEBIMENTO')
        valor_col = get_col(vendas, 'VALOR')

        if pagamento_col and valor_col and not vendas.empty:
            pagamentos_df = vendas.groupby(pagamento_col)[valor_col].sum().reset_index()
            fig_pagamentos = charts_manager.create_pie_chart(
                pagamentos_df,
                values_col=valor_col,
                names_col=pagamento_col,
                title="Receita por Forma de Pagamento"
            )
            st.plotly_chart(fig_pagamentos, use_container_width=True)
        else:
            st.info("Dados de forma de pagamento não encontrados.")

    with col_dias:
        vendas_por_dia = calculate_sales_by_weekday(vendas)
        valor_col = get_col(vendas, 'VALOR')

        if not vendas_por_dia.empty:
            fig_dias = charts_manager.create_bar_chart(
                vendas_por_dia,
                x_col='Dia_Semana',
                y_col=valor_col,
                title="Vendas por Dia da Semana"
            )
            st.plotly_chart(fig_dias, use_container_width=True)
        else:
            st.info("Sem dados de vendas para analisar por dia da semana.")

def show_expenses(despesas_filtradas, crud_system, forms_manager):
    st.markdown("## 💸 Despesas Detalhadas")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    total_despesas = despesas_filtradas["VALOR"].sum() if "VALOR" in despesas_filtradas.columns and not despesas_filtradas.empty else 0
    num_despesas = len(despesas_filtradas) if not despesas_filtradas.empty else 0
    valor_medio = total_despesas / num_despesas if num_despesas > 0 else 0
    num_categorias = despesas_filtradas["CATEGORIA"].nunique() if "CATEGORIA" in despesas_filtradas.columns and not despesas_filtradas.empty else 0
    
    # Determinar se despesas estão controladas (baseado no valor médio)
    if valor_medio >= -2000:  # Limite arbitrário para "despesas controladas"
        status_icon = "✅"
        status_title = "Despesas Controladas"
        status_color = "green"
        status_message = "Continue controlando! 💪"
    elif valor_medio >= -3000:
        status_icon = "⚠️"
        status_title = "Despesas Moderadas"
        status_color = "orange"
        status_message = "Atenção aos gastos! 📊"
    else:
        status_icon = "🚨"
        status_title = "Despesas Altas"
        status_color = "red"
        status_message = "Reveja seus gastos! 💡"
    
    with col1:
        render_metric_card(
            title="Total Despesas",
            value=format_currency(total_despesas),
            icon="💸"
        )
    with col2:
        render_metric_card(
            title="Nº de Despesas",
            value=str(num_despesas),
            icon="📊"
        )
    with col3:
        render_metric_card(
            title="Valor Médio",
            value=format_currency(valor_medio),
            icon="📈"
        )
    with col4:
        # Card personalizado para status das despesas
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {'#d4edda' if status_color == 'green' else '#fff3cd' if status_color == 'orange' else '#f8d7da'}, {'#c3e6cb' if status_color == 'green' else '#ffeaa7' if status_color == 'orange' else '#f5c6cb'});
            border: 2px solid {'#28a745' if status_color == 'green' else '#ffc107' if status_color == 'orange' else '#dc3545'};
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 10px 0;
        ">
            <div style="font-size: 2.5em; margin-bottom: 10px;">{status_icon}</div>
            <div style="font-size: 1.2em; font-weight: bold; color: {'#155724' if status_color == 'green' else '#856404' if status_color == 'orange' else '#721c24'}; margin-bottom: 5px;">
                {status_title}
            </div>
            <div style="font-size: 1.1em; color: {'#155724' if status_color == 'green' else '#856404' if status_color == 'orange' else '#721c24'}; margin-bottom: 5px;">
                Média: {format_currency(valor_medio)}
            </div>
            <div style="font-size: 0.9em; color: {'#155724' if status_color == 'green' else '#856404' if status_color == 'orange' else '#721c24'}; margin-top: 5px;">
                {status_message}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Gráficos de rosca "Top 5"
    st.markdown("### Top 5 Despesas")
    col_pie1, col_pie2, col_pie3 = st.columns(3)
    
    if not despesas_filtradas.empty and "VALOR" in despesas_filtradas.columns:
        # Top 5 por categoria
        with col_pie1:
            if 'CATEGORIA' in despesas_filtradas.columns:
                df_cat = despesas_filtradas.dropna(subset=['CATEGORIA'])
                df_cat = df_cat[df_cat['CATEGORIA'].str.strip() != '']
                if not df_cat.empty:
                    top_categorias = df_cat.groupby('CATEGORIA')["VALOR"].sum().abs().sort_values(ascending=False).head(5).reset_index()
                    fig_categorias = charts_manager.create_pie_chart(
                        top_categorias, "VALOR", 'CATEGORIA', "Top 5 Categorias", hole=0.5, showlegend=True
                    )
                    st.plotly_chart(fig_categorias, use_container_width=True)
        # Top 5 por descrição
        with col_pie2:
            if 'DESCRIÇÃO' in despesas_filtradas.columns:
                df_desc = despesas_filtradas.dropna(subset=['DESCRIÇÃO'])
                df_desc = df_desc[df_desc['DESCRIÇÃO'].str.strip() != '']
                if not df_desc.empty:
                    top_descricoes = df_desc.groupby('DESCRIÇÃO')["VALOR"].sum().abs().sort_values(ascending=False).head(5).reset_index()
                    fig_descricoes = charts_manager.create_pie_chart(
                        top_descricoes, "VALOR", 'DESCRIÇÃO', "Top 5 Descrições", hole=0.5, showlegend=True
                    )
                    st.plotly_chart(fig_descricoes, use_container_width=True)
        # Top 5 por favorecido
        with col_pie3:
            if 'FAVORECIDO' in despesas_filtradas.columns:
                df_fav = despesas_filtradas.dropna(subset=['FAVORECIDO'])
                df_fav = df_fav[df_fav['FAVORECIDO'].str.strip() != '']
                if not df_fav.empty:
                    top_favorecidos = df_fav.groupby('FAVORECIDO')["VALOR"].sum().abs().sort_values(ascending=False).head(5).reset_index()
                    fig_favorecidos = charts_manager.create_pie_chart(
                        top_favorecidos, "VALOR", 'FAVORECIDO', "Top 5 Favorecidos", hole=0.5, showlegend=True
                    )
                    st.plotly_chart(fig_favorecidos, use_container_width=True)
        
        # Evolução temporal
        if "DATA" in despesas_filtradas.columns and not despesas_filtradas.empty:
            despesas_copy = despesas_filtradas.copy()
            despesas_copy["DATA"] = pd.to_datetime(despesas_copy["DATA"], errors='coerce')
            despesas_copy = despesas_copy.dropna(subset=["DATA"])

            if not despesas_copy.empty:
                # Decide o período de agrupamento (diário vs. mensal)
                date_range_days = (despesas_copy["DATA"].max() - despesas_copy["DATA"].min()).days
                
                if date_range_days <= 90:
                    # Agrupamento diário para períodos curtos
                    despesas_temporais = despesas_copy.groupby(despesas_copy["DATA"].dt.date)["VALOR"].sum().reset_index()
                    x_axis_col = "DATA"
                    chart_title = "Evolução Diária das Despesas"
                else:
                    # Agrupamento mensal para períodos longos
                    despesas_copy["Mes"] = despesas_copy["DATA"].dt.strftime("%Y-%m")
                    despesas_temporais = despesas_copy.groupby("Mes")["VALOR"].sum().sort_index().reset_index()
                    x_axis_col = "Mes"
                    chart_title = "Evolução Mensal das Despesas"
                
                # Garante que há pelo menos 2 pontos para desenhar uma linha
                if len(despesas_temporais) > 1:
                    fig_temporal = charts_manager.create_line_chart(
                        despesas_temporais, x_axis_col, "VALOR", chart_title
                    )
                    st.plotly_chart(fig_temporal, use_container_width=True)
                else:
                    st.info("Não há dados suficientes no período selecionado para exibir a evolução temporal.")

    # Tabela de despesas detalhadas (agora renderizada antes dos formulários)
    st.markdown("### 📋 Despesas Lançadas")
    if not despesas_filtradas.empty:
        despesas_crud = despesas_filtradas.copy()
        df_display = format_dataframe_for_display(despesas_crud, "Despesas")
        create_editable_table(df_display, "Despesas", crud_system)
    else:
        st.info("Nenhuma despesa encontrada para o período selecionado.")

    # --- BOTÕES DE AÇÃO UNIFICADOS (agora IMEDIATAMENTE abaixo da tabela) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Novo Lançamento", type="primary", use_container_width=True):
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

    # --- FASE 3: FORMULÁRIO DE INCLUSÃO DE NOVA DESPESA ---
    if st.session_state.get("show_expense_form", False):
        forms_manager.create_expense_form()

    # --- LÓGICA PARA EXIBIR OUTROS FORMULÁRIOS ---
    if st.session_state.get("show_edit_Despesas", False):
        forms_manager.render_edit_expense_form(despesas_filtradas, crud_system)

    if st.session_state.get("show_delete_Despesas", False):
        forms_manager.render_delete_expense_form(despesas_filtradas, crud_system)

    if st.session_state.get("show_bulk_delete_Despesas", False):
        forms_manager.render_bulk_delete_expense_form(despesas_filtradas, crud_system)

def show_revenues(receitas, filters, crud_system, forms_manager):
    st.markdown("## 💰 Análise de Receitas")
    
    # --- BOTÕES DE AÇÃO UNIFICADOS ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Nova Receita", type="primary", use_container_width=True):
            st.session_state.show_revenue_form = not st.session_state.get("show_revenue_form", False)
            st.session_state.show_edit_Receitas = False
            st.session_state.show_delete_Receitas = False
            st.session_state.show_bulk_delete_Receitas = False
    with col2:
        if st.button("✏️ Editar", use_container_width=True):
            st.session_state.show_edit_Receitas = not st.session_state.get("show_edit_Receitas", False)
            st.session_state.show_revenue_form = False
            st.session_state.show_delete_Receitas = False
            st.session_state.show_bulk_delete_Receitas = False
    with col3:
        if st.button("🗑️ Excluir", use_container_width=True):
            st.session_state.show_delete_Receitas = not st.session_state.get("show_delete_Receitas", False)
            st.session_state.show_revenue_form = False
            st.session_state.show_edit_Receitas = False
            st.session_state.show_bulk_delete_Receitas = False
    with col4:
        if st.button("🗑️ Excl. em Lote", use_container_width=True):
            st.session_state.show_bulk_delete_Receitas = not st.session_state.get("show_bulk_delete_Receitas", False)
            st.session_state.show_revenue_form = False
            st.session_state.show_edit_Receitas = False
            st.session_state.show_delete_Receitas = False
    
    st.divider()

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    total_receitas = receitas["VALOR"].sum() if "VALOR" in receitas.columns and not receitas.empty else 0
    num_receitas = len(receitas) if not receitas.empty else 0
    valor_medio = total_receitas / num_receitas if num_receitas > 0 else 0
    num_categorias = receitas["CATEGORIA"].nunique() if "CATEGORIA" in receitas.columns and not receitas.empty else 0
    
    # Determinar se receitas estão boas (baseado no valor médio)
    if valor_medio >= 1000:  # Limite arbitrário para "boas receitas"
        status_icon = "🚀"
        status_title = "Receitas Excelentes"
        status_color = "green"
        status_message = "Continue assim! 💪"
    elif valor_medio >= 500:
        status_icon = "📈"
        status_title = "Receitas Boas"
        status_color = "blue"
        status_message = "Bom desempenho! 👍"
    else:
        status_icon = "💡"
        status_title = "Receitas Baixas"
        status_color = "orange"
        status_message = "Busque oportunidades! 🔍"
    
    with col1:
        render_metric_card(
            title="Total Receitas",
            value=format_currency(total_receitas),
            icon="💰"
        )
    with col2:
        render_metric_card(
            title="Nº de Receitas",
            value=str(num_receitas),
            icon="📈"
        )
    with col3:
        render_metric_card(
            title="Valor Médio",
            value=format_currency(valor_medio),
            icon="📊"
        )
    with col4:
        # Card personalizado para status das receitas
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {'#d4edda' if status_color == 'green' else '#d1ecf1' if status_color == 'blue' else '#fff3cd'}, {'#c3e6cb' if status_color == 'green' else '#bee5eb' if status_color == 'blue' else '#ffeaa7'});
            border: 2px solid {'#28a745' if status_color == 'green' else '#17a2b8' if status_color == 'blue' else '#ffc107'};
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 10px 0;
        ">
            <div style="font-size: 2.5em; margin-bottom: 10px;">{status_icon}</div>
            <div style="font-size: 1.2em; font-weight: bold; color: {'#155724' if status_color == 'green' else '#0c5460' if status_color == 'blue' else '#856404'}; margin-bottom: 5px;">
                {status_title}
            </div>
            <div style="font-size: 1.1em; color: {'#155724' if status_color == 'green' else '#0c5460' if status_color == 'blue' else '#856404'}; margin-bottom: 5px;">
                Média: {format_currency(valor_medio)}
            </div>
            <div style="font-size: 0.9em; color: {'#155724' if status_color == 'green' else '#0c5460' if status_color == 'blue' else '#856404'}; margin-top: 5px;">
                {status_message}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Gráficos de rosca "Top 5"
    st.markdown("### Top 5 Receitas")
    col_pie1, col_pie2, col_pie3 = st.columns(3)
    
    if not receitas.empty and "VALOR" in receitas.columns:
        # Top 5 por categoria
        with col_pie1:
            if 'CATEGORIA' in receitas.columns:
                # Remove valores nulos ou vazios antes de agrupar
                df_cat = receitas.dropna(subset=['CATEGORIA'])
                df_cat = df_cat[df_cat['CATEGORIA'].str.strip() != '']
                
                if not df_cat.empty:
                    top_categorias = df_cat.groupby('CATEGORIA')["VALOR"].sum().sort_values(ascending=False).head(5).reset_index()
                    fig_categorias = charts_manager.create_pie_chart(
                        top_categorias, "VALOR", 'CATEGORIA', "Top 5 Categorias", hole=0.5, showlegend=True
                    )
                    st.plotly_chart(fig_categorias, use_container_width=True)
        
        # Top 5 por descrição
        with col_pie2:
            if 'DESCRIÇÃO' in receitas.columns:
                # Remove valores nulos ou vazios antes de agrupar
                df_desc = receitas.dropna(subset=['DESCRIÇÃO'])
                df_desc = df_desc[df_desc['DESCRIÇÃO'].str.strip() != '']
                
                if not df_desc.empty:
                    top_descricoes = df_desc.groupby('DESCRIÇÃO')["VALOR"].sum().sort_values(ascending=False).head(5).reset_index()
                    fig_descricoes = charts_manager.create_pie_chart(
                        top_descricoes, "VALOR", 'DESCRIÇÃO', "Top 5 Descrições", hole=0.5, showlegend=True
                    )
                    st.plotly_chart(fig_descricoes, use_container_width=True)
        
        # Top 5 por forma de recebimento
        with col_pie3:
            if 'FORMA_RECEBIMENTO' in receitas.columns:
                # Remove valores nulos ou vazios antes de agrupar
                df_rec = receitas.dropna(subset=['FORMA_RECEBIMENTO'])
                df_rec = df_rec[df_rec['FORMA_RECEBIMENTO'].str.strip() != '']
                
                if not df_rec.empty:
                    top_recebimentos = df_rec.groupby('FORMA_RECEBIMENTO')["VALOR"].sum().sort_values(ascending=False).head(5).reset_index()
                    fig_recebimentos = charts_manager.create_pie_chart(
                        top_recebimentos, "VALOR", 'FORMA_RECEBIMENTO', "Top 5 Formas de Recebimento", hole=0.5, showlegend=True
                    )
                    st.plotly_chart(fig_recebimentos, use_container_width=True)
        
        # Evolução temporal
        if "DATA" in receitas.columns and not receitas.empty:
            receitas_copy = receitas.copy()
            receitas_copy["DATA"] = pd.to_datetime(receitas_copy["DATA"], errors='coerce')
            receitas_copy = receitas_copy.dropna(subset=["DATA"])

            if not receitas_copy.empty:
                # Decide o período de agrupamento (diário vs. mensal)
                date_range_days = (receitas_copy["DATA"].max() - receitas_copy["DATA"].min()).days
                
                if date_range_days <= 90:
                    # Agrupamento diário para períodos curtos
                    receitas_temporais = receitas_copy.groupby(receitas_copy["DATA"].dt.date)["VALOR"].sum().reset_index()
                    x_axis_col = "DATA"
                    chart_title = "Evolução Diária das Receitas"
                else:
                    # Agrupamento mensal para períodos longos
                    receitas_copy["Mes"] = receitas_copy["DATA"].dt.strftime("%Y-%m")
                    receitas_temporais = receitas_copy.groupby("Mes")["VALOR"].sum().sort_index().reset_index()
                    x_axis_col = "Mes"
                    chart_title = "Evolução Mensal das Receitas"
                
                # Garante que há pelo menos 2 pontos para desenhar uma linha
                if len(receitas_temporais) > 1:
                    fig_temporal = charts_manager.create_line_chart(
                        receitas_temporais, x_axis_col, "VALOR", chart_title
                    )
                    st.plotly_chart(fig_temporal, use_container_width=True)
                else:
                    st.info("Não há dados suficientes no período selecionado para exibir a evolução temporal.")

    # Tabela de transações (agora renderizada antes dos formulários)
    st.markdown("### 📋 Transações")
    if not receitas.empty:
        receitas_crud = receitas.copy()
        df_display = format_dataframe_for_display(receitas_crud, "Receitas")
        create_editable_table(df_display, "Receitas", crud_system)
    else:
        st.info("Nenhuma receita encontrada para o período selecionado.")

    st.divider()

    # --- LÓGICA PARA EXIBIR FORMULÁRIOS (agora renderizada depois da tabela) ---
    if st.session_state.get("show_revenue_form", False):
        forms_manager.create_revenue_form()

    if st.session_state.get("show_edit_Receitas", False):
        forms_manager.render_edit_revenue_form(receitas, crud_system)

    if st.session_state.get("show_delete_Receitas", False):
        forms_manager.render_delete_revenue_form(receitas, crud_system)

    if st.session_state.get("show_bulk_delete_Receitas", False):
        forms_manager.render_bulk_delete_revenue_form(receitas, crud_system)

def show_credit_card(cc_data, filters, crud_system, forms_manager):
    st.markdown("## 💳 Análise do Cartão de Crédito")
    
    # --- BOTÕES DE AÇÃO UNIFICADOS ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Nova Despesa CC", type="primary", use_container_width=True):
            st.session_state.show_credit_card_form = not st.session_state.get("show_credit_card_form", False)
            st.session_state.show_edit_Div_CC = False
            st.session_state.show_delete_Div_CC = False
            st.session_state.show_bulk_delete_Div_CC = False
    with col2:
        if st.button("✏️ Editar", use_container_width=True):
            st.session_state.show_edit_Div_CC = not st.session_state.get("show_edit_Div_CC", False)
            st.session_state.show_credit_card_form = False
            st.session_state.show_delete_Div_CC = False
            st.session_state.show_bulk_delete_Div_CC = False
    with col3:
        if st.button("🗑️ Excluir", use_container_width=True):
            st.session_state.show_delete_Div_CC = not st.session_state.get("show_delete_Div_CC", False)
            st.session_state.show_credit_card_form = False
            st.session_state.show_edit_Div_CC = False
            st.session_state.show_bulk_delete_Div_CC = False
    with col4:
        if st.button("🗑️ Excl. em Lote", use_container_width=True):
            st.session_state.show_bulk_delete_Div_CC = not st.session_state.get("show_bulk_delete_Div_CC", False)
            st.session_state.show_credit_card_form = False
            st.session_state.show_edit_Div_CC = False
            st.session_state.show_delete_Div_CC = False
    
    st.divider()

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    total_cc = cc_data["VALOR"].sum() if "VALOR" in cc_data.columns and not cc_data.empty else 0
    num_transacoes = len(cc_data) if not cc_data.empty else 0
    valor_medio = total_cc / num_transacoes if num_transacoes > 0 else 0
    num_cartoes = cc_data["CARTAO"].nunique() if "CARTAO" in cc_data.columns and not cc_data.empty else 0
    
    with col1:
        render_metric_card(
            title="Total no Cartão",
            value=format_currency(total_cc),
            icon="💳"
        )
    with col2:
        render_metric_card(
            title="Nº de Transações",
            value=str(num_transacoes),
            icon="🔄"
        )
    with col3:
        render_metric_card(
            title="Valor Médio",
            value=format_currency(valor_medio),
            icon="📊"
        )
    with col4:
        render_metric_card(
            title="Nº de Cartões",
            value=str(num_cartoes),
            icon="💳"
        )
    
    # Gráficos de rosca "Top 5"
    st.markdown("### Top 5 Cartão de Crédito")
    col_pie1, col_pie2, col_pie3 = st.columns(3)
    
    if not cc_data.empty and "VALOR" in cc_data.columns:
        # Top 5 por categoria
        with col_pie1:
            if 'CATEGORIA' in cc_data.columns:
                # Remove valores nulos ou vazios antes de agrupar
                df_cat = cc_data.dropna(subset=['CATEGORIA'])
                df_cat = df_cat[df_cat['CATEGORIA'].str.strip() != '']
                
                if not df_cat.empty:
                    top_categorias = df_cat.groupby('CATEGORIA')["VALOR"].sum().sort_values(ascending=False).head(5).reset_index()
                    fig_categorias = charts_manager.create_pie_chart(
                        top_categorias, "VALOR", 'CATEGORIA', "Top 5 Categorias", hole=0.5, showlegend=True
                    )
                    st.plotly_chart(fig_categorias, use_container_width=True)
        
        # Top 5 por descrição
        with col_pie2:
            if 'DESCRIÇÃO' in cc_data.columns:
                # Remove valores nulos ou vazios antes de agrupar
                df_desc = cc_data.dropna(subset=['DESCRIÇÃO'])
                df_desc = df_desc[df_desc['DESCRIÇÃO'].str.strip() != '']
                
                if not df_desc.empty:
                    top_descricoes = df_desc.groupby('DESCRIÇÃO')["VALOR"].sum().sort_values(ascending=False).head(5).reset_index()
                    fig_descricoes = charts_manager.create_pie_chart(
                        top_descricoes, "VALOR", 'DESCRIÇÃO', "Top 5 Descrições", hole=0.5, showlegend=True
                    )
                    st.plotly_chart(fig_descricoes, use_container_width=True)
        
        # Top 5 por cartão
        with col_pie3:
            if 'CARTAO' in cc_data.columns:
                # Remove valores nulos ou vazios antes de agrupar
                df_cartao = cc_data.dropna(subset=['CARTAO'])
                df_cartao = df_cartao[df_cartao['CARTAO'].str.strip() != '']
                
                if not df_cartao.empty:
                    top_cartoes = df_cartao.groupby('CARTAO')["VALOR"].sum().sort_values(ascending=False).head(5).reset_index()
                    fig_cartoes = charts_manager.create_pie_chart(
                        top_cartoes, "VALOR", 'CARTAO', "Top 5 Cartões", hole=0.5, showlegend=True
                    )
                    st.plotly_chart(fig_cartoes, use_container_width=True)
        
        # Evolução temporal
        if "DATA" in cc_data.columns and not cc_data.empty:
            cc_copy = cc_data.copy()
            cc_copy["DATA"] = pd.to_datetime(cc_copy["DATA"], errors='coerce')
            cc_copy = cc_copy.dropna(subset=["DATA"])

            if not cc_copy.empty:
                # Decide o período de agrupamento (diário vs. mensal)
                date_range_days = (cc_copy["DATA"].max() - cc_copy["DATA"].min()).days
                
                if date_range_days <= 90:
                    # Agrupamento diário para períodos curtos
                    cc_temporais = cc_copy.groupby(cc_copy["DATA"].dt.date)["VALOR"].sum().reset_index()
                    x_axis_col = "DATA"
                    chart_title = "Evolução Diária do Cartão"
                else:
                    # Agrupamento mensal para períodos longos
                    cc_copy["Mes"] = cc_copy["DATA"].dt.strftime("%Y-%m")
                    cc_temporais = cc_copy.groupby("Mes")["VALOR"].sum().sort_index().reset_index()
                    x_axis_col = "Mes"
                    chart_title = "Evolução Mensal do Cartão"
                
                # Garante que há pelo menos 2 pontos para desenhar uma linha
                if len(cc_temporais) > 1:
                    fig_temporal = charts_manager.create_line_chart(
                        cc_temporais, x_axis_col, "VALOR", chart_title
                    )
                    st.plotly_chart(fig_temporal, use_container_width=True)
                else:
                    st.info("Não há dados suficientes no período selecionado para exibir a evolução temporal.")

    # Tabela de transações (agora renderizada antes dos formulários)
    st.markdown("### 📋 Transações")
    if not cc_data.empty:
        cc_crud = cc_data.copy()
        df_display = format_dataframe_for_display(cc_crud, "Div_CC")
        create_editable_table(df_display, "Div_CC", crud_system)
    else:
        st.info("Nenhuma transação no cartão encontrada para o período selecionado.")

    st.divider()

    # --- LÓGICA PARA EXIBIR FORMULÁRIOS (agora renderizada depois da tabela) ---
    if st.session_state.get("show_credit_card_form", False):
        forms_manager.create_credit_card_form()

    if st.session_state.get("show_edit_Div_CC", False):
        forms_manager.render_edit_credit_card_form(cc_data, crud_system)

    if st.session_state.get("show_delete_Div_CC", False):
        forms_manager.render_delete_credit_card_form(cc_data, crud_system)

    if st.session_state.get("show_bulk_delete_Div_CC", False):
        forms_manager.render_bulk_delete_credit_card_form(cc_data, crud_system)

def show_investments(investimentos, filters, crud_system, forms_manager):
    st.markdown("## 💰 Análise de Investimentos")
    
    # --- BOTÕES DE AÇÃO UNIFICADOS ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Novo Investimento", type="primary", use_container_width=True):
            st.session_state.show_investment_form = not st.session_state.get("show_investment_form", False)
            st.session_state.show_edit_Investimentos = False
            st.session_state.show_delete_Investimentos = False
            st.session_state.show_bulk_delete_Investimentos = False
    with col2:
        if st.button("✏️ Editar", use_container_width=True):
            st.session_state.show_edit_Investimentos = not st.session_state.get("show_edit_Investimentos", False)
            st.session_state.show_investment_form = False
            st.session_state.show_delete_Investimentos = False
            st.session_state.show_bulk_delete_Investimentos = False
    with col3:
        if st.button("🗑️ Excluir", use_container_width=True):
            st.session_state.show_delete_Investimentos = not st.session_state.get("show_delete_Investimentos", False)
            st.session_state.show_investment_form = False
            st.session_state.show_edit_Investimentos = False
            st.session_state.show_bulk_delete_Investimentos = False
    with col4:
        if st.button("🗑️ Excl. em Lote", use_container_width=True):
            st.session_state.show_bulk_delete_Investimentos = not st.session_state.get("show_bulk_delete_Investimentos", False)
            st.session_state.show_investment_form = False
            st.session_state.show_edit_Investimentos = False
            st.session_state.show_delete_Investimentos = False
    
    st.divider()

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    total_investido = investimentos["VALOR_APORTE"].sum() if "VALOR_APORTE" in investimentos.columns and not investimentos.empty else 0
    num_aportes = len(investimentos) if not investimentos.empty else 0
    valor_medio_aporte = total_investido / num_aportes if num_aportes > 0 else 0
    num_ativos = investimentos["ATIVO"].nunique() if "ATIVO" in investimentos.columns and not investimentos.empty else 0
    
    # Determinar se investimentos estão diversificados
    if num_ativos >= 5:  # Limite arbitrário para "diversificado"
        status_icon = "🌱"
        status_title = "Portfólio Diversificado"
        status_color = "green"
        status_message = "Excelente diversificação! 🎯"
    elif num_ativos >= 3:
        status_icon = "📊"
        status_title = "Portfólio Moderado"
        status_color = "blue"
        status_message = "Boa diversificação! 👍"
    else:
        status_icon = "⚠️"
        status_title = "Portfólio Concentrado"
        status_color = "orange"
        status_message = "Considere diversificar! 💡"
    
    with col1:
        render_metric_card(
            title="Total Investido",
            value=format_currency(total_investido),
            icon="💰"
        )
    with col2:
        render_metric_card(
            title="Nº de Aportes",
            value=str(num_aportes),
            icon="📈"
        )
    with col3:
        render_metric_card(
            title="Valor Médio",
            value=format_currency(valor_medio_aporte),
            icon="📊"
        )
    with col4:
        # Card personalizado para status dos investimentos
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {'#d4edda' if status_color == 'green' else '#d1ecf1' if status_color == 'blue' else '#fff3cd'}, {'#c3e6cb' if status_color == 'green' else '#bee5eb' if status_color == 'blue' else '#ffeaa7'});
            border: 2px solid {'#28a745' if status_color == 'green' else '#17a2b8' if status_color == 'blue' else '#ffc107'};
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 10px 0;
        ">
            <div style="font-size: 2.5em; margin-bottom: 10px;">{status_icon}</div>
            <div style="font-size: 1.2em; font-weight: bold; color: {'#155724' if status_color == 'green' else '#0c5460' if status_color == 'blue' else '#856404'}; margin-bottom: 5px;">
                {status_title}
            </div>
            <div style="font-size: 1.1em; color: {'#155724' if status_color == 'green' else '#0c5460' if status_color == 'blue' else '#856404'}; margin-bottom: 5px;">
                {num_ativos} ativos
            </div>
            <div style="font-size: 0.9em; color: {'#155724' if status_color == 'green' else '#0c5460' if status_color == 'blue' else '#856404'}; margin-top: 5px;">
                {status_message}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Gráficos de rosca "Top 5"
    st.markdown("### Top 5 Investimentos")
    col_pie1, col_pie2, col_pie3 = st.columns(3)

    if not investimentos.empty and "VALOR_APORTE" in investimentos.columns:
        # Top 5 por ativo
        with col_pie1:
            if 'ATIVO' in investimentos.columns:
                # Remove valores nulos ou vazios antes de agrupar
                df_ativo = investimentos.dropna(subset=['ATIVO'])
                df_ativo = df_ativo[df_ativo['ATIVO'].str.strip() != '']
                
                if not df_ativo.empty:
                    top_ativos = df_ativo.groupby('ATIVO')["VALOR_APORTE"].sum().sort_values(ascending=False).head(5).reset_index()
                    fig_ativos = charts_manager.create_pie_chart(
                        top_ativos, "VALOR_APORTE", 'ATIVO', "Top 5 Ativos", hole=0.5, showlegend=True
                    )
                    st.plotly_chart(fig_ativos, use_container_width=True)
        
        # Top 5 por tipo de investimento
        with col_pie2:
            if 'TIPO_INVESTIMENTO' in investimentos.columns:
                # Remove valores nulos ou vazios antes de agrupar
                df_tipo = investimentos.dropna(subset=['TIPO_INVESTIMENTO'])
                df_tipo = df_tipo[df_tipo['TIPO_INVESTIMENTO'].str.strip() != '']
                
                if not df_tipo.empty:
                    top_tipos = df_tipo.groupby('TIPO_INVESTIMENTO')["VALOR_APORTE"].sum().sort_values(ascending=False).head(5).reset_index()
                    fig_tipos = charts_manager.create_pie_chart(
                        top_tipos, "VALOR_APORTE", 'TIPO_INVESTIMENTO', "Top 5 Tipos", hole=0.5, showlegend=True
                    )
                    st.plotly_chart(fig_tipos, use_container_width=True)
        
        # Top 5 por observações (se houver dados significativos)
        with col_pie3:
            if 'OBSERVACOES' in investimentos.columns:
                # Remove valores nulos ou vazios antes de agrupar
                df_obs = investimentos.dropna(subset=['OBSERVACOES'])
                df_obs = df_obs[df_obs['OBSERVACOES'].str.strip() != '']
                
                if not df_obs.empty and len(df_obs['OBSERVACOES'].unique()) > 1:
                    top_obs = df_obs.groupby('OBSERVACOES')["VALOR_APORTE"].sum().sort_values(ascending=False).head(5).reset_index()
                    fig_obs = charts_manager.create_pie_chart(
                        top_obs, "VALOR_APORTE", 'OBSERVACOES', "Top 5 Observações", hole=0.5, showlegend=True
                    )
                    st.plotly_chart(fig_obs, use_container_width=True)
        
        # Evolução temporal
        if "DATA" in investimentos.columns and not investimentos.empty:
            inv_copy = investimentos.copy()
            inv_copy["DATA"] = pd.to_datetime(inv_copy["DATA"], errors='coerce')
            inv_copy = inv_copy.dropna(subset=["DATA"])

            if not inv_copy.empty:
                # Decide o período de agrupamento (diário vs. mensal)
                date_range_days = (inv_copy["DATA"].max() - inv_copy["DATA"].min()).days
                
                if date_range_days <= 90:
                    # Agrupamento diário para períodos curtos
                    inv_temporais = inv_copy.groupby(inv_copy["DATA"].dt.date)["VALOR_APORTE"].sum().reset_index()
                    x_axis_col = "DATA"
                    chart_title = "Evolução Diária dos Investimentos"
                else:
                    # Agrupamento mensal para períodos longos
                    inv_copy["Mes"] = inv_copy["DATA"].dt.strftime("%Y-%m")
                    inv_temporais = inv_copy.groupby("Mes")["VALOR_APORTE"].sum().sort_index().reset_index()
                    x_axis_col = "Mes"
                    chart_title = "Evolução Mensal dos Investimentos"
                
                # Garante que há pelo menos 2 pontos para desenhar uma linha
                if len(inv_temporais) > 1:
                    fig_temporal = charts_manager.create_line_chart(
                        inv_temporais, x_axis_col, "VALOR_APORTE", chart_title
                    )
                    st.plotly_chart(fig_temporal, use_container_width=True)
                else:
                    st.info("Não há dados suficientes no período selecionado para exibir a evolução temporal.")

    # Tabela de transações (agora renderizada antes dos formulários)
    st.markdown("### 📋 Transações")
    if not investimentos.empty:
        inv_crud = investimentos.copy()
        df_display = format_dataframe_for_display(inv_crud, "Investimentos")
        create_editable_table(df_display, "Investimentos", crud_system)
    else:
        st.info("Nenhum investimento encontrado para o período selecionado.")

    st.divider()

    # --- LÓGICA PARA EXIBIR FORMULÁRIOS (agora renderizada depois da tabela) ---
    if st.session_state.get("show_investment_form", False):
        forms_manager.create_investment_form()

    if st.session_state.get("show_edit_Investimentos", False):
        forms_manager.render_edit_investment_form(investimentos, crud_system)

    if st.session_state.get("show_delete_Investimentos", False):
        forms_manager.render_delete_investment_form(investimentos, crud_system)

    if st.session_state.get("show_bulk_delete_Investimentos", False):
        forms_manager.render_bulk_delete_investment_form(investimentos, crud_system)

def show_budget(receitas, despesas, orcamento, filters):
    st.markdown("## 📋 Análise do Orçamento")
    
    # Calcular renda líquida (receitas - despesas)
    renda_liquida = receitas["VALOR"].sum() if not receitas.empty and "VALOR" in receitas.columns else 0
    total_gasto = despesas["VALOR"].sum() if not despesas.empty and "VALOR" in despesas.columns else 0
    total_orcado = renda_liquida
    saldo_orcamento = total_orcado - total_gasto
    
    # Determinar ícone e cor baseado no saldo
    if saldo_orcamento >= 0:
        saldo_icon = "✅"
        saldo_title = "Saldo Positivo"
        saldo_color = "green"
    else:
        saldo_icon = "⚠️"
        saldo_title = "Saldo Negativo"
        saldo_color = "red"
    
    # Métricas do orçamento
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card(
            title="Renda Líquida",
            value=format_currency(renda_liquida),
            icon="💰"
        )
    with col2:
        render_metric_card(
            title="Total Gasto",
            value=format_currency(total_gasto),
            icon="💸"
        )
    with col3:
        render_metric_card(
            title="Total Orçado",
            value=format_currency(total_orcado),
            icon="📊"
        )
    with col4:
        # Card personalizado para saldo
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {'#d4edda' if saldo_orcamento >= 0 else '#f8d7da'}, {'#c3e6cb' if saldo_orcamento >= 0 else '#f5c6cb'});
            border: 2px solid {'#28a745' if saldo_orcamento >= 0 else '#dc3545'};
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 10px 0;
        ">
            <div style="font-size: 2.5em; margin-bottom: 10px;">{saldo_icon}</div>
            <div style="font-size: 1.2em; font-weight: bold; color: {'#155724' if saldo_orcamento >= 0 else '#721c24'}; margin-bottom: 5px;">
                {saldo_title}
            </div>
            <div style="font-size: 1.5em; font-weight: bold; color: {'#155724' if saldo_orcamento >= 0 else '#721c24'};">
                {format_currency(saldo_orcamento)}
            </div>
            <div style="font-size: 0.9em; color: {'#155724' if saldo_orcamento >= 0 else '#721c24'}; margin-top: 5px;">
                {'Dentro do orçamento! 🎉' if saldo_orcamento >= 0 else 'Acima do orçamento! 📈'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        orcamento_por_categoria = orcamento.copy()
        orcamento_por_categoria["Valor_Orcado"] = (orcamento_por_categoria["Percentual"] / 100) * renda_liquida
        fig_orcado = charts_manager.create_pie_chart(
            orcamento_por_categoria, "Valor_Orcado", "Categoria", "Distribuição Orçada por Categoria"
        )
        st.plotly_chart(fig_orcado, use_container_width=True)
    with col2:
        if not despesas.empty and "VALOR" in despesas.columns:
            despesas_por_categoria = despesas.groupby("CATEGORIA")["VALOR"].sum().abs().reset_index()
            
            # Garante que há dados para plotar
            if not despesas_por_categoria.empty and despesas_por_categoria["VALOR"].sum() > 0:
                fig_real = charts_manager.create_pie_chart(
                    despesas_por_categoria, "VALOR", "CATEGORIA", "Distribuição Real dos Gastos"
                )
                st.plotly_chart(fig_real, use_container_width=True)
            else:
                st.info("Nenhum dado de gasto real para exibir no período selecionado.")
        else:
            st.info("Nenhum dado de gasto real para exibir no período selecionado.")
    
    # Comparativo
    if not despesas.empty and "VALOR" in despesas.columns:
        st.markdown("### 📊 Comparativo Orçado vs. Gasto")
        comparativo = orcamento.copy()
        comparativo["Valor_Orcado"] = (comparativo["Percentual"] / 100) * renda_liquida
        despesas_por_categoria = despesas.groupby("CATEGORIA")["VALOR"].sum().abs()
        comparativo["Valor_Gasto"] = comparativo["Categoria"].map(despesas_por_categoria).fillna(0)
        comparativo["Saldo"] = comparativo["Valor_Orcado"] - comparativo["Valor_Gasto"]
        
        # Divisão segura para Series, tratando divisão por zero (que resulta em infinito) e NaN.
        comparativo["Percentual_Uso"] = (comparativo["Valor_Gasto"] / comparativo["Valor_Orcado"] * 100).replace([np.inf, -np.inf], 0).fillna(0)
        
        fig_comparativo = charts_manager.create_comparison_chart(
            comparativo, "Categoria", ["Valor_Orcado", "Valor_Gasto"], "Comparativo Orçado vs. Gasto por Categoria"
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

def show_sales(vendas, filters, crud_system, forms_manager):
    st.markdown("## 🛒 Análise de Vendas")
    
    # --- BOTÕES DE AÇÃO UNIFICADOS ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Nova Venda", type="primary", use_container_width=True):
            st.session_state.show_sale_form = not st.session_state.get("show_sale_form", False)
            st.session_state.show_edit_Vendas = False
            st.session_state.show_delete_Vendas = False
            st.session_state.show_bulk_delete_Vendas = False
    with col2:
        if st.button("✏️ Editar", use_container_width=True):
            st.session_state.show_edit_Vendas = not st.session_state.get("show_edit_Vendas", False)
            st.session_state.show_sale_form = False
            st.session_state.show_delete_Vendas = False
            st.session_state.show_bulk_delete_Vendas = False
    with col3:
        if st.button("🗑️ Excluir", use_container_width=True):
            st.session_state.show_delete_Vendas = not st.session_state.get("show_delete_Vendas", False)
            st.session_state.show_sale_form = False
            st.session_state.show_edit_Vendas = False
            st.session_state.show_bulk_delete_Vendas = False
    with col4:
        if st.button("🗑️ Excl. em Lote", use_container_width=True):
            st.session_state.show_bulk_delete_Vendas = not st.session_state.get("show_bulk_delete_Vendas", False)
            st.session_state.show_sale_form = False
            st.session_state.show_edit_Vendas = False
            st.session_state.show_delete_Vendas = False
    
    st.divider()

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    total_vendido = vendas["VALOR"].sum() if "VALOR" in vendas.columns and not vendas.empty else 0
    num_vendas = len(vendas) if not vendas.empty else 0
    ticket_medio = total_vendido / num_vendas if num_vendas > 0 else 0
    num_clientes = vendas["Cliente"].nunique() if "Cliente" in vendas.columns and not vendas.empty else 0
    
    # Determinar se vendas estão boas (baseado no ticket médio)
    if ticket_medio >= 2000:  # Limite arbitrário para "excelentes vendas"
        status_icon = "🏆"
        status_title = "Vendas Excelentes"
        status_color = "green"
        status_message = "Desempenho incrível! 🎉"
    elif ticket_medio >= 1000:
        status_icon = "📈"
        status_title = "Vendas Boas"
        status_color = "blue"
        status_message = "Continue crescendo! 💪"
    else:
        status_icon = "💡"
        status_title = "Vendas Baixas"
        status_color = "orange"
        status_message = "Foque no ticket médio! 📊"
    
    with col1:
        render_metric_card(
            title="Total Vendido",
            value=format_currency(total_vendido),
            icon="💰"
        )
    with col2:
        render_metric_card(
            title="Nº de Vendas",
            value=str(num_vendas),
            icon="🛒"
        )
    with col3:
        render_metric_card(
            title="Ticket Médio",
            value=format_currency(ticket_medio),
            icon="📊"
        )
    with col4:
        # Card personalizado para status das vendas
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {'#d4edda' if status_color == 'green' else '#d1ecf1' if status_color == 'blue' else '#fff3cd'}, {'#c3e6cb' if status_color == 'green' else '#bee5eb' if status_color == 'blue' else '#ffeaa7'});
            border: 2px solid {'#28a745' if status_color == 'green' else '#17a2b8' if status_color == 'blue' else '#ffc107'};
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 10px 0;
        ">
            <div style="font-size: 2.5em; margin-bottom: 10px;">{status_icon}</div>
            <div style="font-size: 1.2em; font-weight: bold; color: {'#155724' if status_color == 'green' else '#0c5460' if status_color == 'blue' else '#856404'}; margin-bottom: 5px;">
                {status_title}
            </div>
            <div style="font-size: 1.1em; color: {'#155724' if status_color == 'green' else '#0c5460' if status_color == 'blue' else '#856404'}; margin-bottom: 5px;">
                Ticket: {format_currency(ticket_medio)}
            </div>
            <div style="font-size: 0.9em; color: {'#155724' if status_color == 'green' else '#0c5460' if status_color == 'blue' else '#856404'}; margin-top: 5px;">
                {status_message}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Gráficos de rosca "Top 5"
    st.markdown("### Top 5 Vendas")
    col_pie1, col_pie2, col_pie3 = st.columns(3)

    if not vendas.empty and "VALOR" in vendas.columns:
        # Top 5 por cliente
        with col_pie1:
            if 'Cliente' in vendas.columns:
                # Remove valores nulos ou vazios antes de agrupar
                df_cliente = vendas.dropna(subset=['Cliente'])
                df_cliente = df_cliente[df_cliente['Cliente'].str.strip() != '']
                
                if not df_cliente.empty:
                    top_clientes = df_cliente.groupby('Cliente')["VALOR"].sum().sort_values(ascending=False).head(5).reset_index()
                    fig_clientes = charts_manager.create_pie_chart(
                        top_clientes, "VALOR", 'Cliente', "Top 5 Clientes", hole=0.5, showlegend=True
                    )
                    st.plotly_chart(fig_clientes, use_container_width=True)
        
        # Top 5 por produto
        with col_pie2:
            if 'Produto' in vendas.columns:
                # Remove valores nulos ou vazios antes de agrupar
                df_produto = vendas.dropna(subset=['Produto'])
                df_produto = df_produto[df_produto['Produto'].str.strip() != '']
                
                if not df_produto.empty:
                    top_produtos = df_produto.groupby('Produto')["VALOR"].sum().sort_values(ascending=False).head(5).reset_index()
                    fig_produtos = charts_manager.create_pie_chart(
                        top_produtos, "VALOR", 'Produto', "Top 5 Produtos", hole=0.5, showlegend=True
                    )
                    st.plotly_chart(fig_produtos, use_container_width=True)
        
        # Top 5 por forma de pagamento
        with col_pie3:
            if 'Forma_Pagamento' in vendas.columns:
                # Remove valores nulos ou vazios antes de agrupar
                df_pagamento = vendas.dropna(subset=['Forma_Pagamento'])
                df_pagamento = df_pagamento[df_pagamento['Forma_Pagamento'].str.strip() != '']
                
                if not df_pagamento.empty:
                    top_pagamentos = df_pagamento.groupby('Forma_Pagamento')["VALOR"].sum().sort_values(ascending=False).head(5).reset_index()
                    fig_pagamentos = charts_manager.create_pie_chart(
                        top_pagamentos, "VALOR", 'Forma_Pagamento', "Top 5 Formas de Pagamento", hole=0.5, showlegend=True
                    )
                    st.plotly_chart(fig_pagamentos, use_container_width=True)
        
        # Evolução temporal
        if "DATA" in vendas.columns and not vendas.empty:
            vendas_copy = vendas.copy()
            vendas_copy["DATA"] = pd.to_datetime(vendas_copy["DATA"], errors='coerce')
            vendas_copy = vendas_copy.dropna(subset=["DATA"])

            if not vendas_copy.empty:
                # Decide o período de agrupamento (diário vs. mensal)
                date_range_days = (vendas_copy["DATA"].max() - vendas_copy["DATA"].min()).days
                
                if date_range_days <= 90:
                    # Agrupamento diário para períodos curtos
                    vendas_temporais = vendas_copy.groupby(vendas_copy["DATA"].dt.date)["VALOR"].sum().reset_index()
                    x_axis_col = "DATA"
                    chart_title = "Evolução Diária das Vendas"
                else:
                    # Agrupamento mensal para períodos longos
                    vendas_copy["Mes"] = vendas_copy["DATA"].dt.strftime("%Y-%m")
                    vendas_temporais = vendas_copy.groupby("Mes")["VALOR"].sum().sort_index().reset_index()
                    x_axis_col = "Mes"
                    chart_title = "Evolução Mensal das Vendas"
                
                # Garante que há pelo menos 2 pontos para desenhar uma linha
                if len(vendas_temporais) > 1:
                    fig_temporal = charts_manager.create_line_chart(
                        vendas_temporais, x_axis_col, "VALOR", chart_title
                    )
                    st.plotly_chart(fig_temporal, use_container_width=True)
                else:
                    st.info("Não há dados suficientes no período selecionado para exibir a evolução temporal.")

    # Tabela de transações (agora renderizada antes dos formulários)
    st.markdown("### 📋 Transações")
    if not vendas.empty:
        vendas_crud = vendas.copy()
        df_display = format_dataframe_for_display(vendas_crud, "Vendas")
        create_editable_table(df_display, "Vendas", crud_system)
    else:
        st.info("Nenhuma venda encontrada para o período selecionado.")

    st.divider()

    # --- LÓGICA PARA EXIBIR FORMULÁRIOS (agora renderizada depois da tabela) ---
    if st.session_state.get("show_sale_form", False):
        forms_manager.create_sale_form()

    if st.session_state.get("show_edit_Vendas", False):
        forms_manager.render_edit_sale_form(vendas, crud_system)

    if st.session_state.get("show_delete_Vendas", False):
        forms_manager.render_delete_sale_form(vendas, crud_system)

    if st.session_state.get("show_bulk_delete_Vendas", False):
        forms_manager.render_bulk_delete_sale_form(vendas, crud_system)

def show_analytics(receitas, despesas, filters):
    st.markdown("## 📈 Análises Avançadas")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    total_receitas = receitas["VALOR"].sum() if "VALOR" in receitas.columns and not receitas.empty else 0
    total_despesas = despesas["VALOR"].sum() if "VALOR" in despesas.columns and not despesas.empty else 0
    saldo = total_receitas + total_despesas
    percentual_despesas = (abs(total_despesas) / total_receitas) * 100 if total_receitas > 0 else 0
    
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
        render_metric_card(
            title="% Desp./Rec.",
            value=f"{percentual_despesas:.1f}%",
            icon="📊"
        )
    
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

def show_page_template(title, df, sheet_name, crud_system, forms_manager, form_name):
    st.markdown(f"## {title}")
    
    # Exibe a tabela de despesas detalhadas se for a página de despesas
    if sheet_name == "Despesas":
        st.markdown("### 📋 Despesas Lançadas")
        if not df.empty:
            df_display = format_dataframe_for_display(df, sheet_name)
            create_editable_table(df_display, sheet_name, crud_system)
        else:
            st.info("Nenhuma despesa encontrada para o período selecionado.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button(f"➕ Novo Lançamento", type="primary", use_container_width=True, key=f"add_{sheet_name}"):
            st.session_state[f"show_{form_name}_form"] = not st.session_state.get(f"show_{form_name}_form", False)
            # Reset other forms
            for other_form in ['expense', 'revenue', 'sale', 'credit_card', 'investment']:
                if other_form != form_name:
                    st.session_state[f"show_{other_form}_form"] = False
    with col2:
        if st.button("✏️ Editar", use_container_width=True, key=f"edit_{sheet_name}"):
            st.session_state[f"show_edit_{sheet_name}"] = not st.session_state.get(f"show_edit_{sheet_name}", False)
            st.session_state[f"show_{form_name}_form"] = False
    with col3:
        if st.button("🗑️ Excluir", use_container_width=True, key=f"delete_{sheet_name}"):
            st.session_state[f"show_delete_{sheet_name}"] = not st.session_state.get(f"show_delete_{sheet_name}", False)
            st.session_state[f"show_{form_name}_form"] = False
    with col4:
        if st.button("🗑️ Excl. em Lote", use_container_width=True, key=f"bulk_delete_{sheet_name}"):
            st.session_state[f"show_bulk_delete_{sheet_name}"] = not st.session_state.get(f"show_bulk_delete_{sheet_name}", False)
            st.session_state[f"show_{form_name}_form"] = False

    st.divider()
    
    # Exibe o formulário apenas se o botão foi clicado
    if sheet_name == "Despesas" and st.session_state.get(f"show_{form_name}_form", False):
        # Primeiro, obtenha a categoria selecionada
        categorias = self._get_dynamic_options("Despesas", "CATEGORIA")
        selected_categoria = st.selectbox("Categoria", options=categorias, key="categoria_selectbox")

        if selected_categoria:
            favorecidos = self._get_dynamic_options("Despesas", "FAVORECIDO")
            favorecidos.append("--- Digitar Novo Favorecido ---")
            form_id = str(uuid.uuid4())
            with st.form(key=f"form_despesa_{selected_categoria}_{form_id}"):
                st.info(f"Categoria selecionada: **{selected_categoria}**")
                col1, col2 = st.columns(2)
                with col1:
                    data = st.date_input("Data", value=date.today(), key=f"data_{selected_categoria}_{form_id}")
                    favorecido = st.selectbox(
                        "Favorecido",
                        options=favorecidos,
                        key=f"favorecido_select_{selected_categoria}_{form_id}"
                    )
                    if favorecido == "--- Digitar Novo Favorecido ---":
                        novo_favorecido_input = st.text_input(
                            "Novo Favorecido:",
                            placeholder="Digite o nome do novo favorecido",
                            key=f"novo_favorecido_input_{selected_categoria}_{form_id}"
                        )
                with col2:
                    conta = st.selectbox("Conta", options=contas, key=f"conta_{selected_categoria}_{form_id}")
                    forma_pagamento = st.selectbox("Forma de Pagamento", options=formas_pagamento, key=f"forma_pagamento_{selected_categoria}_{form_id}")
                    valor = st.number_input("Valor (R$)", min_value=0.01, step=50.0, format="%.2f", key=f"valor_{selected_categoria}_{form_id}")
                    pago = st.checkbox("Pago?", value=True, key=f"pago_{selected_categoria}_{form_id}")
                submitted = st.form_submit_button("Salvar", key=f"submit_{selected_categoria}_{form_id}")

    edit_key = f"show_edit_{sheet_name}"
    if st.session_state.get(edit_key, False):
        render_func = getattr(forms_manager, f"render_edit_{form_name}_form", None)
        if render_func:
            render_func(df, crud_system)

    delete_key = f"show_delete_{sheet_name}"
    if st.session_state.get(delete_key, False):
        render_func = getattr(forms_manager, f"render_delete_{form_name}_form", None)
        if render_func:
            render_func(df, crud_system)

    bulk_delete_key = f"show_bulk_delete_{sheet_name}"
    if st.session_state.get(bulk_delete_key, False):
        render_func = getattr(forms_manager, f"render_bulk_delete_form", None)
        if render_func:
            render_func(sheet_name, crud_system, df)

def consultar_despesas(storage):
    """Consulta todas as despesas cadastradas no armazenamento e exibe em tabela com filtros."""
    st.header("Consulta de Despesas")
    if storage.empty:
        st.info("Nenhuma despesa cadastrada.")
        return

    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        categorias = ["Todas"] + sorted(storage["CATEGORIA"].dropna().unique().tolist())
        filtro_categoria = st.selectbox("Filtrar por Categoria", categorias)
    with col2:
        favorecidos = ["Todos"] + sorted(storage["FAVORECIDO"].dropna().unique().tolist())
        filtro_favorecido = st.selectbox("Filtrar por Favorecido", favorecidos)
    with col3:
        datas = pd.to_datetime(storage["DATA"], errors="coerce")
        data_min = datas.min().date() if not datas.isnull().all() else date.today()
        data_max = datas.max().date() if not datas.isnull().all() else date.today()
        filtro_data = st.date_input("Filtrar por Data", (data_min, data_max))

    # Aplicar filtros
    df_filtrado = storage.copy()
    if filtro_categoria != "Todas":
        df_filtrado = df_filtrado[df_filtrado["CATEGORIA"] == filtro_categoria]
    if filtro_favorecido != "Todos":
        df_filtrado = df_filtrado[df_filtrado["FAVORECIDO"] == filtro_favorecido]
    if filtro_data:
        data_ini, data_fim = filtro_data
        datas = pd.to_datetime(df_filtrado["DATA"], errors="coerce")
        mask = (datas >= pd.to_datetime(data_ini)) & (datas <= pd.to_datetime(data_fim))
        df_filtrado = df_filtrado[mask]

    # Exibir tabela
    st.dataframe(df_filtrado.reset_index(drop=True))

    # Exportação
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button("Exportar para CSV", csv, "despesas_filtradas.csv", "text/csv")

if __name__ == "__main__":
    main() 