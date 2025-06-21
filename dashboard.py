import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from numerize.numerize import numerize
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components

# Outras importações úteis
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta

# Importação do módulo de relatórios
from relatorio_pdf import RelatorioPDF, create_download_button

# Função para carregar itens de validação das categorias
def carregar_itens_categoria():
    """Carrega os itens de cada categoria da planilha para validação"""
    try:
        xls = pd.ExcelFile(excel_path)
        
        # Carregar itens de despesas
        df_cat_desp = pd.read_excel(xls, sheet_name='Despesas Categoria')
        itens_despesas = {}
        for coluna in df_cat_desp.columns:
            itens = df_cat_desp[coluna].dropna().tolist()
            itens_despesas[coluna] = itens
        
        # Carregar itens de receitas
        df_cat_rec = pd.read_excel(xls, sheet_name='Receitas Categoria')
        itens_receitas = []
        if 'SUBCATEGORIA' in df_cat_rec.columns:
            itens_receitas = df_cat_rec['SUBCATEGORIA'].dropna().unique().tolist()
        
        return itens_despesas, itens_receitas
    except Exception as e:
        st.error(f"Erro ao carregar itens de categoria: {e}")
        return {}, []

# Inicialização do session_state para os formulários
if "show_despesa_form" not in st.session_state:
    st.session_state.show_despesa_form = False
if "show_receita_form" not in st.session_state:
    st.session_state.show_receita_form = False
if "show_cc_form" not in st.session_state:
    st.session_state.show_cc_form = False

st.set_page_config(page_title="DashBoard", layout="wide")

st.markdown("""
<style>
    /* Aumenta a largura da sidebar para evitar quebra de texto nos filtros */
    section[data-testid="stSidebar"] {
        width: 350px !important;
    }
    
    /* Estilos para os novos cards de métricas */
    .metric-card {
        background-color: #1c213c;
        border: 1px solid #293153;
        border-radius: 12px;
        padding: 25px 20px;
        margin-bottom: 10px;
        color: #f0f2f6;
        position: relative;
    }
    
    /* Corrige a quebra de linha no menu de navegação */
    div[data-testid="stOptionMenu"] > ul {
        white-space: nowrap;
    }
    div[data-testid="stOptionMenu"] > ul > li {
        display: inline-block;
        padding: 0 10px; /* Adiciona um espaçamento mais uniforme */
    }
    
    .metric-card.saldo {
        background: linear-gradient(to right, #e96443, #904e95);
        border: none;
    }
    .metric-card .title-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .metric-card h4 {
        font-size: 1rem;
        font-weight: 400;
        margin: 0;
        opacity: 0.8;
        color: #d1d5db;
    }
    .metric-card.saldo h4, .metric-card.saldo h2 {
        color: white;
    }
    .metric-card h2 {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        color: #f9fafb;
    }
    .metric-card .delta {
        font-size: 0.8rem;
        font-weight: 500;
        background-color: rgba(255, 255, 255, 0.1);
        padding: 2px 8px;
        border-radius: 8px;
    }
    .delta-p-green { color: #34d399; }
    .delta-p-red { color: #f87171; }

    /* Correção para o menu de navegação (option_menu) */
    ul[class^="nav"] {
        display: flex;
        flex-wrap: nowrap !important; /* Impede a quebra de linha */
        white-space: nowrap;
        overflow-x: auto; /* Adiciona scroll horizontal se necessário */
        -webkit-overflow-scrolling: touch; /* Melhora a rolagem em dispositivos móveis */
    }

    li[class^="nav-item"] {
        flex-shrink: 0; /* Impede que os itens do menu encolham */
    }

    a[class^="nav-link"] {
        display: flex !important;
        align-items: center !important; /* Alinha ícone e texto verticalmente */
        white-space: nowrap !important; /* Garante que o texto dentro do link não quebre */
        padding: 10px 15px !important; /* Ajusta o espaçamento interno */
    }

    a[class^="nav-link"] > i {
        margin-right: 8px !important; /* Adiciona espaço entre o ícone e o texto */
        padding-bottom: 2px; /* Ajuste fino do alinhamento vertical do ícone */
    }

</style>
""", unsafe_allow_html=True)

# Ícone de finanças (exemplo: 💰)
st.markdown("## 💰 Análise Descritiva de Finanças Pessoais")

# --- SISTEMA DE NAVEGAÇÃO ---
selected = option_menu(
    menu_title=None,
    options=["Visão Geral", "Transações", "Para onde vai", "Pra quem vai", "Classificação ABC", "Fluxo de Caixa", "Despesas por Categoria", "Vendas", "Investimentos", "Cartão de Crédito", "Orçamento"],
    icons=["bar-chart", "table", "graph-up", "people-fill", "list-ol", "graph-up-arrow", "bar-chart-fill", "cart-fill", "piggy-bank", "credit-card", "target"],
    orientation="horizontal",
    default_index=0,
)

# Caminho do arquivo Excel
excel_path = 'Base_financas.xlsx'

# Lê todas as abas do arquivo Excel
xls = pd.ExcelFile(excel_path)
abas = xls.sheet_names

# Exemplo de leitura de uma aba específica:
# df_despesas = pd.read_excel(xls, sheet_name='Despesas')

# Sidebar para filtros
with st.sidebar:
    with st.expander('Filtros Gerais', expanded=False):
        st.header('Filtros')
        st.write('Selecione os filtros desejados abaixo:')
        if 'reset_filtros' not in st.session_state:
            st.session_state['reset_filtros'] = False
        # Lê a aba 'Conta' para obter as opções de contas
        df_conta = pd.read_excel(xls, sheet_name='Conta')
        contas = df_conta['Contas'].dropna().unique().tolist()

        # Filtro de tipo de análise com checkboxes para evitar texto cortado
        st.write('**Tipo de análise**')
        col_rec, col_desp = st.columns(2)
        show_receitas = col_rec.checkbox('Receitas', value=True)
        show_despesas = col_desp.checkbox('Despesas', value=True)

        tipos_selecionados = []
        if show_receitas:
            tipos_selecionados.append('Receitas')
        if show_despesas:
            tipos_selecionados.append('Despesas')

        # Filtro de conta com opção 'Todas'
        contas_opcoes = ['Todas'] + contas
        if st.session_state['reset_filtros']:
            conta_selecionada = st.selectbox('Conta', contas_opcoes, index=0, key='conta_filtro_reset')
        else:
            conta_selecionada = st.selectbox('Conta', contas_opcoes, key='conta_filtro')

        # Filtro dinâmico de categoria
        if 'Receitas' in tipos_selecionados:
            df_cat = pd.read_excel(xls, sheet_name='Receitas Categoria')
            categorias = df_cat['SUBCATEGORIA'].dropna().unique().tolist()
        else:
            df_cat = pd.read_excel(xls, sheet_name='Despesas Categoria')
            categorias = df_cat.columns.tolist()

        # Filtro de categoria com opção 'Todas'
        categorias_opcoes = ['Todas'] + categorias
        if st.session_state['reset_filtros']:
            categoria_selecionada = st.selectbox('Categoria', categorias_opcoes, index=0, key='cat_filtro_reset')
        else:
            categoria_selecionada = st.selectbox('Categoria', categorias_opcoes, key='cat_filtro')

        # Filtros de tempo extraindo Ano e Mês da coluna 'DATA'
        if 'Receitas' in tipos_selecionados:
            df_dados = pd.read_excel(xls, sheet_name='Receitas')
        else:
            df_dados = pd.read_excel(xls, sheet_name='Despesas')

        # Garante que a coluna DATA está em formato datetime
        df_dados['DATA'] = pd.to_datetime(df_dados['DATA'], errors='coerce')
        df_dados = df_dados.dropna(subset=['DATA'])
        df_dados['Ano'] = df_dados['DATA'].dt.year.astype(str)

        # Lista de meses em ordem cronológica (abreviações em português)
        meses_ordem = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

        # Ajusta o nome dos meses para português, se necessário
        df_dados['Mês'] = df_dados['DATA'].dt.strftime('%b').str.capitalize().replace({'Feb': 'Fev', 'Apr': 'Abr', 'May': 'Mai', 'Aug': 'Ago', 'Sep': 'Set', 'Oct': 'Out', 'Dec': 'Dez'})

        # Filtro de ano com multiselect
        anos = df_dados['Ano'].dropna().unique().tolist()
        if st.session_state['reset_filtros']:
            anos_selecionados = st.multiselect('Ano', sorted(anos, reverse=True), default=sorted(anos, reverse=True), key='ano_filtro_reset')
        else:
            anos_selecionados = st.multiselect('Ano', sorted(anos, reverse=True), default=sorted(anos, reverse=True), key='ano_filtro')

        # Filtro de mês com multiselect
        meses = [m for m in meses_ordem if m in df_dados['Mês'].unique()]
        if st.session_state['reset_filtros']:
            meses_selecionados = st.multiselect('Mês', meses, default=meses, key='mes_filtro_reset')
        else:
            meses_selecionados = st.multiselect('Mês', meses, default=meses, key='mes_filtro')

    # Só mostra o expander de vendas se a aba Vendas estiver selecionada
    if selected == 'Vendas':
        df_vendas = pd.read_excel(xls, sheet_name='Vendas')
        df_vendas['DATA'] = pd.to_datetime(df_vendas['DATA'], errors='coerce')
        df_vendas = df_vendas.dropna(subset=['DATA'])
        df_vendas['Ano'] = df_vendas['DATA'].dt.year.astype(str)
        df_vendas['Mês'] = df_vendas['DATA'].dt.strftime('%b').str.capitalize().replace({'Feb': 'Fev', 'Apr': 'Abr', 'May': 'Mai', 'Aug': 'Ago', 'Sep': 'Set', 'Oct': 'Out', 'Dec': 'Dez'})
        with st.expander('Filtros de Vendas', expanded=True):
            anos_vendas = df_vendas['Ano'].dropna().unique().tolist()
            anos_vendas_sel = st.multiselect('Ano (Vendas)', sorted(anos_vendas, reverse=True), default=sorted(anos_vendas, reverse=True), key='ano_vendas')
            meses_ordem = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            meses_vendas = [m for m in meses_ordem if m in df_vendas['Mês'].unique()]
            meses_vendas_sel = st.multiselect('Mês (Vendas)', meses_vendas, default=meses_vendas, key='mes_vendas')
            contas_vendas = ['Todas'] + df_vendas['CONTA'].dropna().unique().tolist()
            conta_vendas_sel = st.selectbox('Conta (Vendas)', contas_vendas, key='conta_vendas')
            tipos_receb = ['Todos'] + df_vendas['TIPO DE RECEBIMENTO'].dropna().unique().tolist()
            tipo_receb_sel = st.selectbox('Tipo de Recebimento', tipos_receb, key='tipo_receb_vendas')
            pago_opcoes = ['Todos', 'Sim', 'Não']
            pago_sel = st.selectbox('Pago?', pago_opcoes, key='pago_vendas')
    
    # Só mostra o expander de investimentos se a aba Investimentos estiver selecionada
    if selected == 'Investimentos':
        df_investimentos = pd.read_excel(xls, sheet_name='Investimentos')
        df_investimentos['DATA'] = pd.to_datetime(df_investimentos['DATA'], errors='coerce')
        df_investimentos = df_investimentos.dropna(subset=['DATA'])
        df_investimentos['Ano'] = df_investimentos['DATA'].dt.year.astype(str)
        df_investimentos['Mês'] = df_investimentos['DATA'].dt.strftime('%b').str.capitalize().replace({'Feb': 'Fev', 'Apr': 'Abr', 'May': 'Mai', 'Aug': 'Ago', 'Sep': 'Set', 'Oct': 'Out', 'Dec': 'Dez'})
        with st.expander('Filtros de Investimentos', expanded=True):
            anos_invest = df_investimentos['Ano'].dropna().unique().tolist()
            anos_invest_sel = st.multiselect('Ano (Investimentos)', sorted(anos_invest, reverse=True), default=sorted(anos_invest, reverse=True), key='ano_invest')
            meses_ordem = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            meses_invest = [m for m in meses_ordem if m in df_investimentos['Mês'].unique()]
            meses_invest_sel = st.multiselect('Mês (Investimentos)', meses_invest, default=meses_invest, key='mes_invest')
            tipos_invest = ['Todos'] + df_investimentos['TIPO'].dropna().unique().tolist()
            tipo_invest_sel = st.selectbox('Tipo de Investimento', tipos_invest, key='tipo_invest')
            objetivos_invest = ['Todos'] + df_investimentos['OBJETIVO'].dropna().unique().tolist()
            objetivo_invest_sel = st.selectbox('Objetivo', objetivos_invest, key='objetivo_invest')
            ativos_invest = ['Todos'] + df_investimentos['ATIVO'].dropna().unique().tolist()
            ativo_invest_sel = st.selectbox('Ativo', ativos_invest, key='ativo_invest')
    
    # Só mostra o expander de Cartão de Crédito se a aba estiver selecionada
    if selected == 'Cartão de Crédito':
        df_cc = pd.read_excel(xls, sheet_name='Div_CC')
        df_cc['Data'] = pd.to_datetime(df_cc['Data'], errors='coerce')
        df_cc.dropna(subset=['Data'], inplace=True)
        df_cc['Ano'] = df_cc['Data'].dt.year.astype(str)
        df_cc['Mês'] = df_cc['Data'].dt.strftime('%b').str.capitalize().replace({'Feb': 'Fev', 'Apr': 'Abr', 'May': 'Mai', 'Aug': 'Ago', 'Sep': 'Set', 'Oct': 'Out', 'Dec': 'Dez'})
        with st.expander('Filtros do Cartão de Crédito', expanded=True):
            anos_cc = df_cc['Ano'].dropna().unique().tolist()
            anos_cc_sel = st.multiselect('Ano (Cartão)', sorted(anos_cc, reverse=True), default=sorted(anos_cc, reverse=True), key='ano_cc_sidebar')
            
            meses_ordem = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            meses_cc = [m for m in meses_ordem if m in df_cc['Mês'].unique()]
            meses_cc_sel = st.multiselect('Mês (Cartão)', meses_cc, default=meses_cc, key='mes_cc_sidebar')

            cartoes_cc = ['Todos'] + df_cc['Cartão'].dropna().unique().tolist()
            cartao_cc_sel = st.selectbox('Cartão', cartoes_cc, key='cartao_cc_sidebar')

            situacao_cc = ['Todas'] + df_cc['Situação'].dropna().unique().tolist()
            situacao_cc_sel = st.selectbox('Situação', situacao_cc, key='situacao_cc_sidebar')

            tipos_compra = ['Todos'] + df_cc['Tipo de Compra'].dropna().unique().tolist()
            tipo_compra_sel = st.selectbox('Tipo de Compra', tipos_compra, key='tipo_compra_cc_sidebar')

            parcelas_opcoes = ['Todas'] + [str(x) for x in sorted(df_cc['Quantidade de parcelas'].dropna().unique())]
            parcelas_sel = st.selectbox('Quantidade de Parcelas', parcelas_opcoes, key='parcelas_cc_sidebar')

    st.markdown('---')
    if st.button('Redefinir Filtros'):
        st.session_state['reset_filtros'] = True
    
    st.markdown('---')
    with st.expander("🚀 Lançamentos Rápidos", expanded=True):
        if st.button("➕ Nova Despesa", use_container_width=True, type="primary"):
            st.session_state.show_despesa_form = True
        if st.button("💰 Nova Receita", use_container_width=True):
            st.session_state.show_receita_form = True
        if st.button("💳 Nova Compra (CC)", use_container_width=True):
            st.session_state.show_cc_form = True

# --- CÁLCULO DOS INDICADORES BÁSICOS ---

# Filtra receitas
receitas = pd.read_excel(xls, sheet_name='Receitas')
receitas['DATA'] = pd.to_datetime(receitas['DATA'], errors='coerce')
receitas = receitas.dropna(subset=['DATA'])
receitas['Ano'] = receitas['DATA'].dt.year.astype(str)
receitas['Mês'] = receitas['DATA'].dt.strftime('%b').str.capitalize().replace({'Feb': 'Fev', 'Apr': 'Abr', 'May': 'Mai', 'Aug': 'Ago', 'Sep': 'Set', 'Oct': 'Out', 'Dec': 'Dez'})

receitas_filtradas = receitas[
    ((receitas['CONTA'] == conta_selecionada) | (conta_selecionada == 'Todas')) &
    (receitas['Ano'].isin(anos_selecionados) if anos_selecionados else True) &
    (receitas['Mês'].isin(meses_selecionados) if meses_selecionados else True)
]

# Categoria de receitas
if 'Receitas' in tipos_selecionados and categoria_selecionada != 'Todas':
    receitas_filtradas = receitas_filtradas[receitas_filtradas['CATEGORIA'] == categoria_selecionada]

# Filtra despesas

despesas = pd.read_excel(xls, sheet_name='Despesas')
despesas['DATA'] = pd.to_datetime(despesas['DATA'], errors='coerce')
despesas = despesas.dropna(subset=['DATA'])
despesas['Ano'] = despesas['DATA'].dt.year.astype(str)
despesas['Mês'] = despesas['DATA'].dt.strftime('%b').str.capitalize().replace({'Feb': 'Fev', 'Apr': 'Abr', 'May': 'Mai', 'Aug': 'Ago', 'Sep': 'Set', 'Oct': 'Out', 'Dec': 'Dez'})

despesas_filtradas = despesas[
    ((despesas['CONTA'] == conta_selecionada) | (conta_selecionada == 'Todas')) &
    (despesas['Ano'].isin(anos_selecionados) if anos_selecionados else True) &
    (despesas['Mês'].isin(meses_selecionados) if meses_selecionados else True)
]

# Categoria de despesas
if 'Despesas' in tipos_selecionados and categoria_selecionada != 'Todas':
    despesas_filtradas = despesas_filtradas[despesas_filtradas['CATEGORIA'] == categoria_selecionada]

# Se o tipo não estiver selecionado, zera os valores
if 'Receitas' not in tipos_selecionados:
    valor_recebidos = 0
else:
    valor_recebidos = receitas_filtradas['VALOR'].sum()

if 'Despesas' not in tipos_selecionados:
    valor_despesas = 0
else:
    valor_despesas = despesas_filtradas['VALOR'].sum()

saldo = valor_recebidos + valor_despesas  # Despesas já são negativas
# Corrige o cálculo do percentual para evitar divisão por zero
if valor_recebidos > 0:
    percentual = (abs(valor_despesas) / valor_recebidos * 100)
else:
    percentual = 0.0

# --- CÁLCULO DE PERÍODO ANTERIOR E DELTAS ---
saldo_anterior = 0
# Define um valor padrão caso o cálculo não seja possível
delta_receitas = 0
delta_despesas = 0

# A comparação só faz sentido se um único mês e ano forem selecionados
if len(meses_selecionados) == 1 and len(anos_selecionados) == 1:
    ano_atual_num = int(anos_selecionados[0])
    mes_atual_idx = meses_ordem.index(meses_selecionados[0])
    
    if mes_atual_idx > 0:
        mes_ant_str = meses_ordem[mes_atual_idx - 1]
        ano_ant_num = ano_atual_num
    else:
        # Janeiro -> Dezembro do ano anterior
        mes_ant_str = 'Dez'
        ano_ant_num = ano_atual_num - 1

    ano_ant_str = str(ano_ant_num)

    # Filtra dados do período anterior
    receitas_ant_df = receitas[
        (receitas['Ano'] == ano_ant_str) & (receitas['Mês'] == mes_ant_str)
    ]
    despesas_ant_df = despesas[
        (despesas['Ano'] == ano_ant_str) & (despesas['Mês'] == mes_ant_str)
    ]
    
    if conta_selecionada != 'Todas':
        receitas_ant_df = receitas_ant_df[receitas_ant_df['CONTA'] == conta_selecionada]
        despesas_ant_df = despesas_ant_df[despesas_ant_df['CONTA'] == conta_selecionada]

    receitas_anterior = receitas_ant_df['VALOR'].sum()
    despesas_anterior = despesas_ant_df['VALOR'].sum()
    saldo_anterior = receitas_anterior + despesas_anterior

    # Calcular deltas
    if receitas_anterior > 0:
        delta_receitas = ((valor_recebidos - receitas_anterior) / receitas_anterior) * 100
    else:
        delta_receitas = 0.0
        
    if abs(despesas_anterior) > 0:
        delta_despesas = ((abs(valor_despesas) - abs(despesas_anterior)) / abs(despesas_anterior)) * 100
    else:
        delta_despesas = 0.0

def format_brl(valor):
    # Verifica se o valor é NaN ou None
    if pd.isna(valor) or valor is None:
        return "R$ 0,00"
    
    # Converte para float se necessário
    try:
        valor = float(valor)
    except (ValueError, TypeError):
        return "R$ 0,00"
    
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

# Helper para HTML do delta
def get_delta_html(delta, reverse_colors=False):
    # Verifica se o delta é NaN ou None
    if pd.isna(delta) or delta is None:
        return ""
    
    # Converte para float se necessário
    try:
        delta = float(delta)
    except (ValueError, TypeError):
        return ""
    
    if delta > 0:
        arrow = "↑"
        color_class = "delta-p-green" if not reverse_colors else "delta-p-red"
    elif delta < 0:
        arrow = "↓"
        color_class = "delta-p-red" if not reverse_colors else "delta-p-green"
    else:
        arrow = ""
        color_class = ""
    
    return f'<span class="delta {color_class}">{abs(delta):.1f}% {arrow}</span>' if delta != 0 else ''

# Exibe cards principais apenas se não estiver na aba Vendas
if selected != 'Vendas' and selected != 'Cartão de Crédito' and selected != 'Investimentos':
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="metric-card saldo">
            <h4>Saldo</h4>
            <h2>{format_brl(saldo)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        delta_html = get_delta_html(delta_receitas)
        st.markdown(f"""
        <div class="metric-card">
            <div class="title-row">
                <h4>Recebimentos</h4>{delta_html}
            </div>
            <h2>{format_brl(valor_recebidos)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        delta_html = get_delta_html(delta_despesas, reverse_colors=True)
        st.markdown(f"""
        <div class="metric-card">
            <div class="title-row">
                <h4>Despesas</h4>{delta_html}
            </div>
            <h2>{format_brl(abs(valor_despesas))}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        saldo_ant_text = format_brl(saldo_anterior) if (len(meses_selecionados) == 1 and len(anos_selecionados) == 1) else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <h4>Saldo Anterior</h4>
            <h2>{saldo_ant_text}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Despesas vs Receitas %</h4>
            <h2>{percentual:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)

if selected == "Visão Geral":
    # Botão de exportação de relatório
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📄 Exportar Relatório PDF", type="primary", use_container_width=True):
            # Criar instância do gerador de relatórios
            relatorio = RelatorioPDF()
            
            # Preparar dados para o relatório
            dados_relatorio = {
                'saldo': saldo,
                'receitas': valor_recebidos,
                'despesas': abs(valor_despesas),
                'percentual': percentual,
                'graficos': []
            }
            
            # Adicionar gráficos se existirem dados
            if not despesas_filtradas.empty:
                # Gráfico de evolução das despesas
                df_evolucao = despesas_filtradas.copy()
                df_evolucao['Dia'] = df_evolucao['DATA'].dt.day
                evolucao = (
                    df_evolucao.groupby('Dia')['VALOR']
                    .sum()
                    .abs()
                    .reset_index()
                    .sort_values('Dia')
                )
                fig_evol = px.bar(
                    evolucao,
                    x='Dia',
                    y='VALOR',
                    labels={'Dia': 'Dia do Mês', 'VALOR': 'Despesas (R$)'},
                    title='Evolução das Despesas ao Longo dos Dias',
                )
                dados_relatorio['graficos'].append({
                    'titulo': 'Evolução das Despesas ao Longo dos Dias',
                    'fig': fig_evol,
                    'descricao': 'Análise da distribuição das despesas por dia do mês'
                })
            
            # Gerar relatório
            try:
                filename = relatorio.generate_dashboard_report(dados_relatorio, "relatorio_visao_geral.pdf")
                st.success("✅ Relatório gerado com sucesso!")
                create_download_button(filename, "📥 Download Relatório Visão Geral")
            except Exception as e:
                st.error(f"❌ Erro ao gerar relatório: {e}")
    
    st.markdown("---")
    
    # --- GRÁFICOS DE ROSCA LADO A LADO ---
    cols = st.columns([1, 0.08, 1, 0.08, 1])
    col_g1, col_g2, col_g3 = cols[0], cols[2], cols[4]

    with col_g1:
        # Gráfico 1 (Categoria)
        df_top5 = despesas_filtradas.copy()
        if not df_top5.empty:
            top5 = (
                df_top5.groupby('CATEGORIA')['VALOR']
                .sum()
                .abs()
                .sort_values(ascending=False)
                .head(5)
            )
            fig = px.pie(
                names=top5.index,
                values=top5.values,
                hole=0.5,
                title='Top 5 Despesas por Categoria',
            )
            fig.update_traces(
                textinfo='percent',
                textposition='outside',
                pull=[0.05]*5,
                textfont_size=16,
            )
            fig.update_layout(
                legend=dict(orientation='h', yanchor='bottom', y=-0.35, xanchor='center', x=0.5, font=dict(size=11))
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info('Não há despesas para exibir no gráfico com os filtros selecionados.')

    with col_g2:
        # Gráfico 2 (Descrição)
        df_top5_desc = despesas_filtradas.copy()
        if not df_top5_desc.empty:
            top5_desc = (
                df_top5_desc.groupby('DESCRIÇÃO')['VALOR']
                .sum()
                .abs()
                .sort_values(ascending=False)
                .head(5)
            )
            fig_desc = px.pie(
                names=top5_desc.index,
                values=top5_desc.values,
                hole=0.5,
                title='Top 5 Despesas por Descrição',
            )
            fig_desc.update_traces(
                textinfo='percent',
                textposition='outside',
                pull=[0.05]*5,
                textfont_size=16,
            )
            fig_desc.update_layout(
                legend=dict(orientation='h', yanchor='bottom', y=-0.35, xanchor='center', x=0.5)
            )
            st.plotly_chart(fig_desc, use_container_width=True)
        else:
            st.info('Não há despesas para exibir no gráfico de descrição com os filtros selecionados.')

    with col_g3:
        # Gráfico 3 (Favorecido)
        df_top5_fav = despesas_filtradas.copy()
        if not df_top5_fav.empty:
            top5_fav = (
                df_top5_fav.groupby('FAVORECIDO')['VALOR']
                .sum()
                .abs()
                .sort_values(ascending=False)
                .head(5)
            )
            fig_fav = px.pie(
                names=top5_fav.index,
                values=top5_fav.values,
                hole=0.5,
                title='Top 5 Despesas por Favorecido',
            )
            fig_fav.update_traces(
                textinfo='percent',
                textposition='outside',
                pull=[0.05]*5,
                textfont_size=16,
            )
            fig_fav.update_layout(
                legend=dict(orientation='h', yanchor='bottom', y=-0.35, xanchor='center', x=0.5, font=dict(size=11))
            )
            st.plotly_chart(fig_fav, use_container_width=True)
        else:
            st.info('Não há despesas para exibir no gráfico de favorecido com os filtros selecionados.')

    # --- GRÁFICO DE EVOLUÇÃO DAS DESPESAS AO LONGO DOS DIAS ---
    st.markdown('---')
    df_evolucao = despesas_filtradas.copy()
    if not df_evolucao.empty:
        df_evolucao['Dia'] = df_evolucao['DATA'].dt.day
        evolucao = (
            df_evolucao.groupby('Dia')['VALOR']
            .sum()
            .abs()
            .reset_index()
            .sort_values('Dia')
        )
        fig_evol = px.bar(
            evolucao,
            x='Dia',
            y='VALOR',
            labels={'Dia': 'Dia do Mês', 'VALOR': 'Despesas (R$)'},
            title='Evolução das Despesas ao Longo dos Dias',
        )
        fig_evol.update_layout(
            xaxis=dict(dtick=1),
            yaxis_tickformat = ',.2f',
            yaxis_title='Despesas (R$)',
            xaxis_title='Dia do Mês',
            bargap=0.2
        )
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info('Não há despesas para exibir a evolução ao longo dos dias com os filtros selecionados.')

elif selected == "Transações":
    # --- TABELA DE TRANSAÇÕES ---
    df_trans = pd.concat([
        receitas_filtradas.assign(TIPO='Recebido'),
        despesas_filtradas.assign(TIPO='Pagamento')
    ], ignore_index=True)
    df_trans = df_trans.sort_values('DATA')
    df_trans['Recebidos'] = df_trans.apply(lambda x: x['VALOR'] if x['TIPO']=='Recebido' else 0, axis=1)
    df_trans['Pagamentos'] = df_trans.apply(lambda x: abs(x['VALOR']) if x['TIPO']=='Pagamento' else 0, axis=1)
    df_trans['Saldo'] = df_trans['Recebidos'] - df_trans['Pagamentos']
    df_trans['Saldo Acumulado Num'] = df_trans['Saldo'].cumsum()
    df_trans['DATA'] = df_trans['DATA'].dt.strftime('%d/%m/%Y')
    df_trans = df_trans.rename(columns={
        'DATA': 'Data',
        'FAVORECIDO': 'Favorecido',
        'DESCRIÇÃO': 'Descrição',
        'CATEGORIA': 'Categoria'
    })
    df_trans = df_trans[['Data', 'Favorecido', 'Descrição', 'Categoria', 'Recebidos', 'Pagamentos', 'Saldo Acumulado Num']]
    # Formatar valores
    df_trans['Recebidos'] = df_trans['Recebidos'].apply(format_brl)
    df_trans['Pagamentos'] = df_trans['Pagamentos'].apply(format_brl)

    # Adiciona setas Unicode coloridas via CSS
    saldo_acum = df_trans['Saldo Acumulado Num'].tolist()
    saldo_acum_str = []
    for i, val in enumerate(saldo_acum):
        seta = ''
        if i == 0:
            seta = '—'
        else:
            if val > saldo_acum[i-1]:
                seta = '<span class="seta-verde">▲</span>'
            elif val < saldo_acum[i-1]:
                seta = '<span class="seta-vermelha">▼</span>'
            else:
                seta = '—'
        saldo_acum_str.append(f'{format_brl(val)} {seta}')
    df_trans['Saldo Acumulado'] = saldo_acum_str

    # Monta tabela HTML com estilos para tema escuro
    st.markdown('### Transações Detalhadas')
    table_html = """
    <style>
    .trans-table {
        width: 100%;
        border-collapse: collapse;
        color: #f0f2f6; /* Texto claro para tema escuro */
        font-family: 'sans-serif';
    }
    .trans-table th, .trans-table td {
        border: 1px solid #3a3f44;
        padding: 8px 12px;
        text-align: left;
    }
    .trans-table th {
        background-color: #1a1f24; /* Cabeçalho mais escuro */
    }
    .trans-table tr:nth-child(even) {
        background-color: #262c31; /* Listras para melhor leitura */
    }
    .pagamento {
        color: #ff6961; /* Vermelho suave para pagamentos */
        font-weight: bold;
    }
    .seta-verde {
        color: #77dd77; /* Verde suave */
        font-weight: bold;
    }
    .seta-vermelha {
        color: #ff6961; /* Vermelho suave */
        font-weight: bold;
    }
    </style>
    <table class='trans-table'>
        <tr>
            <th>Data</th>
            <th>Favorecido</th>
            <th>Descrição</th>
            <th>Categoria</th>
            <th>Recebidos</th>
            <th>Pagamentos</th>
            <th>Saldo Acumulado</th>
        </tr>
    """
    for _, row in df_trans.iterrows():
        # Adiciona a classe 'pagamento' apenas se houver um valor de pagamento
        pagamento_class = "class='pagamento'" if row['Pagamentos'] != 'R$ 0,00' else ""
        table_html += f"""
        <tr>
            <td>{row['Data']}</td>
            <td>{row['Favorecido']}</td>
            <td>{row['Descrição']}</td>
            <td>{row['Categoria']}</td>
            <td>{row['Recebidos']}</td>
            <td {pagamento_class}>{row['Pagamentos']}</td>
            <td>{row['Saldo Acumulado']}</td>
        </tr>
        """
    table_html += "</table>"
    components.html(table_html, height=800, scrolling=True)

elif selected == "Para onde vai":
    st.markdown('### Gráfico de Pareto das Despesas por Categoria')
    df_pareto = despesas_filtradas.copy()
    if not df_pareto.empty:
        pareto = (
            df_pareto.groupby('CATEGORIA')['VALOR']
            .sum()
            .abs()
            .sort_values(ascending=False)
            .reset_index()
        )
        pareto['%'] = pareto['VALOR'] / pareto['VALOR'].sum() * 100
        pareto['% Acumulado'] = pareto['%'].cumsum()
        pareto['Classe'] = 'C'
        pareto.loc[pareto['% Acumulado'] <= 80, 'Classe'] = 'A'
        pareto.loc[(pareto['% Acumulado'] > 80) & (pareto['% Acumulado'] <= 90), 'Classe'] = 'B'
        
        # Define as cores com base na classe ABC
        cores = pareto['Classe'].map({'A': '#fc6076', 'B': '#ffd200', 'C': '#b0b0b0'}).tolist()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=pareto['CATEGORIA'],
            y=pareto['VALOR'],
            marker_color=cores, # Restaura as cores das barras
            name='Despesas',
            text=pareto['VALOR'].apply(lambda x: format_brl(x)),
            textposition='auto',
            width=0.4  # barras mais finas
        ))
        fig.add_trace(go.Scatter(
            x=pareto['CATEGORIA'],
            y=pareto['% Acumulado'],
            mode='lines+markers',
            name='Acumulado (%)',
            line=dict(color='#FFD700', width=3, dash='solid'), # Linha dourada
            marker=dict(color='#FFD700', size=8),
            yaxis='y2'
        ))
        fig.add_trace(go.Scatter(
            x=pareto['CATEGORIA'],
            y=[80]*len(pareto),
            mode='lines',
            name='80%',
            line=dict(color='#FFD700', width=2, dash='dash'), # Linha do limite de 80%
            yaxis='y2',
            showlegend=True
        ))
        fig.update_layout(
            yaxis=dict(title='Despesas (R$)', showgrid=False),
            yaxis2=dict(title='% Acumulado', overlaying='y', side='right', range=[0, 110], showgrid=False),
            xaxis=dict(title='Categoria', automargin=True, tickangle=-45, tickfont=dict(size=12)),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            bargap=0.2,
            margin=dict(t=40, b=120),
            height=500,
            plot_bgcolor='rgba(0,0,0,0)', # Fundo transparente para se adaptar ao tema
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('Não há despesas suficientes para exibir o gráfico de Pareto com os filtros selecionados.')

elif selected == "Pra quem vai":
    st.markdown('### Gráfico de Pareto das Despesas por Descrição')
    df_pareto = despesas_filtradas.copy()
    if not df_pareto.empty:
        pareto = (
            df_pareto.groupby('DESCRIÇÃO')['VALOR']
            .sum()
            .abs()
            .sort_values(ascending=False)
            .reset_index()
        )
        pareto['%'] = pareto['VALOR'] / pareto['VALOR'].sum() * 100
        pareto['% Acumulado'] = pareto['%'].cumsum()
        pareto['Classe'] = 'C'
        pareto.loc[pareto['% Acumulado'] <= 80, 'Classe'] = 'A'
        pareto.loc[(pareto['% Acumulado'] > 80) & (pareto['% Acumulado'] <= 90), 'Classe'] = 'B'
        
        # Define as cores com base na classe ABC
        cores = pareto['Classe'].map({'A': '#fc6076', 'B': '#ffd200', 'C': '#b0b0b0'}).tolist()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=pareto['DESCRIÇÃO'],
            y=pareto['VALOR'],
            marker_color=cores, # Restaura as cores das barras
            name='Despesas',
            text=pareto['VALOR'].apply(lambda x: format_brl(x)),
            textposition='auto',
            width=0.4
        ))
        fig.add_trace(go.Scatter(
            x=pareto['DESCRIÇÃO'],
            y=pareto['% Acumulado'],
            mode='lines+markers',
            name='Acumulado (%)',
            line=dict(color='#FFD700', width=3, dash='solid'), # Linha dourada
            marker=dict(color='#FFD700', size=8),
            yaxis='y2'
        ))
        fig.add_trace(go.Scatter(
            x=pareto['DESCRIÇÃO'],
            y=[80]*len(pareto),
            mode='lines',
            name='80%',
            line=dict(color='#FFD700', width=2, dash='dash'), # Linha do limite de 80%
            yaxis='y2',
            showlegend=True
        ))
        fig.update_layout(
            yaxis=dict(title='Despesas (R$)', showgrid=False),
            yaxis2=dict(title='% Acumulado', overlaying='y', side='right', range=[0, 110], showgrid=False),
            xaxis=dict(title='Descrição', automargin=True, tickangle=-45, tickfont=dict(size=12)),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            bargap=0.2,
            margin=dict(t=40, b=120),
            height=500,
            plot_bgcolor='rgba(0,0,0,0)', # Fundo transparente para se adaptar ao tema
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('Não há despesas suficientes para exibir o gráfico de Pareto com os filtros selecionados.')

elif selected == "Classificação ABC":
    st.markdown('### Classificação ABC das Despesas por Descrição')
    df_abc = despesas_filtradas.copy()
    if not df_abc.empty:
        # Soma por descrição no mês atual
        desc_mes_atual = (
            df_abc.groupby('DESCRIÇÃO')['VALOR']
            .sum()
            .abs()
            .sort_values(ascending=False)
            .reset_index()
        )
        desc_mes_atual['%Despesas'] = desc_mes_atual['VALOR'] / desc_mes_atual['VALOR'].sum() * 100
        desc_mes_atual['Despesa Acumulada'] = desc_mes_atual['VALOR'].cumsum()
        desc_mes_atual['%Acum'] = desc_mes_atual['Despesa Acumulada'] / desc_mes_atual['VALOR'].sum() * 100
        desc_mes_atual['Ranking'] = desc_mes_atual['VALOR'].rank(ascending=False, method='min').astype(int)
        desc_mes_atual['Classe'] = 'C'
        desc_mes_atual.loc[desc_mes_atual['%Acum'] <= 80, 'Classe'] = 'A'
        desc_mes_atual.loc[(desc_mes_atual['%Acum'] > 80) & (desc_mes_atual['%Acum'] <= 90), 'Classe'] = 'B'
        # Soma por descrição no mês anterior
        if len(meses_selecionados) == 1:
            idx_mes = meses_ordem.index(meses_selecionados[0])
            if idx_mes > 0:
                mes_ant = meses_ordem[idx_mes-1]
                df_ant = despesas[(despesas['Ano'].isin(anos_selecionados)) & (despesas['Mês'] == mes_ant)]
                desc_mes_ant = df_ant.groupby('DESCRIÇÃO')['VALOR'].sum().abs().reset_index()
                desc_mes_ant = desc_mes_ant.rename(columns={'VALOR': 'Mês Anterior'})
            else:
                desc_mes_ant = desc_mes_atual[['DESCRIÇÃO']].copy()
                desc_mes_ant['Mês Anterior'] = 0
        else:
            desc_mes_ant = desc_mes_atual[['DESCRIÇÃO']].copy()
            desc_mes_ant['Mês Anterior'] = 0
        # Junta mês anterior
        df_abc = desc_mes_atual.merge(desc_mes_ant, on='DESCRIÇÃO', how='left')
        df_abc['Mês Anterior'] = df_abc['Mês Anterior'].fillna(0)
        # MoM e MoM%
        df_abc['MoM'] = df_abc['VALOR'] - df_abc['Mês Anterior']
        df_abc['MoM%_num'] = df_abc.apply(lambda x: (x['MoM']/x['Mês Anterior']*100) if x['Mês Anterior'] > 0 else 0, axis=1)
        # Formatação
        df_abc['Despesas(R$)'] = df_abc['VALOR'].apply(format_brl)
        df_abc['Mês Anterior'] = df_abc['Mês Anterior'].apply(format_brl)
        df_abc['MoM'] = df_abc['MoM'].apply(format_brl)
        df_abc['%Despesas'] = df_abc['%Despesas'].apply(lambda x: f'{x:.1f}%')
        df_abc['Despesa Acumulada'] = df_abc['Despesa Acumulada'].apply(format_brl)
        df_abc['%Acum'] = df_abc['%Acum'].apply(lambda x: f'{x:.1f}%')
        # MoM% com setas
        mom_seta = []
        for val in df_abc['MoM%_num']:
            if val > 0:
                seta = '<span class="seta-verde">▲</span>'
            elif val < 0:
                seta = '<span class="seta-vermelha">▼</span>'
            else:
                seta = '—'
            mom_seta.append(f'{val:.1f}% {seta}')
        df_abc['MoM%'] = mom_seta
        # Classe com ícones
        classe_icone = []
        for classe in df_abc['Classe']:
            if classe == 'A':
                icone = '<span class="seta-vermelha">▼</span>'
            elif classe == 'B':
                icone = '<span class="classe-b-icone">●</span>'
            else:
                icone = '<span class="seta-cinza">▼</span>'
            classe_icone.append(f'{classe} {icone}')
        df_abc['Classe_Icone'] = classe_icone
        # Seleção de colunas e renomeação
        df_abc = df_abc.rename(columns={'DESCRIÇÃO': 'Descrição'})
        df_abc = df_abc[['Descrição', 'Ranking', 'Despesas(R$)', '%Despesas', 'Despesa Acumulada', '%Acum', 'Classe_Icone', 'Mês Anterior', 'MoM', 'MoM%']]
        # Renderização
        st.markdown('#### Tabela ABC detalhada das despesas')
        # Tabela HTML customizada para colorir Descrição
        table_html = """
        <style>
        .abc-table {
            width: 100%;
            border-collapse: collapse;
            color: #f0f2f6; /* Texto claro para tema escuro */
            font-family: 'sans-serif';
        }
        .abc-table th, .abc-table td {
            border: 1px solid #3a3f44;
            padding: 8px 12px;
            text-align: center;
        }
        .abc-table th {
            background-color: #1a1f24; /* Cabeçalho mais escuro */
        }
        .abc-table tr:nth-child(even) {
            background-color: #262c31; /* Listras para melhor leitura */
        }
        .cat-a { color: #ff6961; font-weight: bold; } /* Vermelho para Classe A */
        .cat-b { color: #fdfd96; font-weight: bold; } /* Amarelo para Classe B */
        .seta-verde { color: #77dd77; font-weight: bold; } /* Verde suave */
        .seta-vermelha { color: #ff6961; font-weight: bold; } /* Vermelho suave */
        .seta-cinza { color: #8390a2; font-weight: bold; } /* Cinza azulado */
        .classe-b-icone { color: #fdfd96; font-weight: bold; } /* Amarelo para Classe B */
        </style>
        <table class='abc-table'>
            <tr>
                <th>Descrição</th>
                <th>Ranking</th>
                <th>Despesas(R$)</th>
                <th>%Despesas</th>
                <th>Despesa Acumulada</th>
                <th>%Acum</th>
                <th>Classe</th>
                <th>Mês Anterior</th>
                <th>MoM</th>
                <th>MoM%</th>
            </tr>
        """
        for _, row in df_abc.iterrows():
            classe = row['Classe_Icone']
            if 'A' in classe:
                desc_class = 'cat-a'
            elif 'B' in classe:
                desc_class = 'cat-b'
            else:
                desc_class = ''
            table_html += f"""
            <tr>
                <td class='{desc_class}'>{row['Descrição']}</td>
                <td>{row['Ranking']}</td>
                <td>{row['Despesas(R$)']}</td>
                <td>{row['%Despesas']}</td>
                <td>{row['Despesa Acumulada']}</td>
                <td>{row['%Acum']}</td>
                <td>{row['Classe_Icone']}</td>
                <td>{row['Mês Anterior']}</td>
                <td>{row['MoM']}</td>
                <td>{row['MoM%']}</td>
            </tr>
            """
        table_html += "</table>"
        components.html(table_html, height=600, scrolling=True)
    else:
        st.info('Não há despesas suficientes para exibir a tabela ABC com os filtros selecionados.')

elif selected == "Fluxo de Caixa":
    st.markdown('### Fluxo de Caixa')
    # Junta receitas e despesas filtradas
    df_fluxo = pd.concat([
        receitas_filtradas.assign(TIPO='Receita'),
        despesas_filtradas.assign(TIPO='Despesa')
    ], ignore_index=True)
    df_fluxo = df_fluxo.sort_values('DATA')
    df_fluxo['VALOR'] = df_fluxo.apply(lambda x: x['VALOR'] if x['TIPO']=='Receita' else x['VALOR'], axis=1)
    df_fluxo['Saldo Acumulado'] = df_fluxo['VALOR'].cumsum()
    df_fluxo['DATA'] = df_fluxo['DATA'].dt.strftime('%d/%m/%Y')
    # Gráfico de área customizado estilo dark
    if not df_fluxo.empty:
        fig_fluxo = go.Figure()
        fig_fluxo.add_trace(go.Scatter(
            x=df_fluxo['DATA'],
            y=df_fluxo['Saldo Acumulado'],
            mode='lines+markers+text',
            text=[f"R$ {v:,.0f}".replace(",", ".") for v in df_fluxo['Saldo Acumulado']],
            textposition='top center',
            hovertemplate='Data: %{x}<br>Saldo: R$ %{y:,.2f}<extra></extra>',
            name='Saldo Acumulado'
        ))
        fig_fluxo.update_layout(
            title='Análise do Saldo Acumulado (YTD)',
            xaxis=dict(title='Data'),
            yaxis=dict(title='Saldo Acumulado (R$)'),
            margin=dict(l=30, r=30, t=50, b=40),
            height=420,
            showlegend=False,
        )
        st.plotly_chart(fig_fluxo, use_container_width=True)
    else:
        st.info('Não há dados suficientes para exibir o fluxo de caixa com os filtros selecionados.')

elif selected == "Despesas por Categoria":
    st.markdown('### Despesas por Subcategoria dentro da Categoria')
    df_cat = despesas_filtradas.copy()
    if not df_cat.empty:
        if categoria_selecionada == 'Todas':
            st.info('Selecione uma categoria específica na barra lateral para ver o detalhamento por subcategoria.')
        else:
            df_cat = df_cat[df_cat['CATEGORIA'] == categoria_selecionada]
            subcats = df_cat['DESCRIÇÃO'].dropna().unique().tolist()
            subcats = sorted(subcats)
            subcats_opcoes = ['Todas'] + subcats
            subcats_selecionadas = st.multiselect('Filtrar Subcategoria', subcats_opcoes, default=['Todas'])
            if 'Todas' in subcats_selecionadas or not subcats_selecionadas:
                df_sub = df_cat
                subcats_plot = subcats
            else:
                df_sub = df_cat[df_cat['DESCRIÇÃO'].isin(subcats_selecionadas)]
                subcats_plot = subcats_selecionadas
            # Agrupa por mês e subcategoria
            df_sub['MÊS_ANO'] = df_sub['DATA'].dt.strftime('%b/%Y').str.capitalize().replace({'Feb': 'Fev', 'Apr': 'Abr', 'May': 'Mai', 'Aug': 'Ago', 'Sep': 'Set', 'Oct': 'Out', 'Dec': 'Dez'})
            evolucao = df_sub.groupby(['MÊS_ANO', 'DESCRIÇÃO'])['VALOR'].sum().abs().reset_index()
            # Ordena os meses corretamente
            meses_ordem = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            evolucao['MÊS'] = evolucao['MÊS_ANO'].str[:3]
            evolucao['ANO'] = evolucao['MÊS_ANO'].str[-4:]
            evolucao['MÊS_NUM'] = evolucao['MÊS'].apply(lambda x: meses_ordem.index(x) if x in meses_ordem else -1)
            evolucao['ANO_NUM'] = evolucao['ANO'].astype(int)
            evolucao = evolucao.sort_values(['ANO_NUM', 'MÊS_NUM'])
            # Gera lista completa de meses/anos entre o menor e o maior registro
            if not evolucao.empty:
                min_ano = evolucao['ANO_NUM'].min()
                max_ano = evolucao['ANO_NUM'].max()
                min_mes = evolucao[evolucao['ANO_NUM'] == min_ano]['MÊS_NUM'].min()
                max_mes = evolucao[evolucao['ANO_NUM'] == max_ano]['MÊS_NUM'].max()
                meses_ordem = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                labels_x = []
                for ano in range(min_ano, max_ano+1):
                    for i, mes in enumerate(meses_ordem):
                        if (ano == min_ano and i < min_mes) or (ano == max_ano and i > max_mes):
                            continue
                        labels_x.append(f'{mes}/{ano}')
            else:
                labels_x = []
            # Gráfico de linha
            fig = go.Figure()
            for subcat in subcats_plot:
                dados = evolucao[evolucao['DESCRIÇÃO'] == subcat]
                # Garante que todos os meses apareçam, mesmo se não houver valor
                dados = dados.set_index('MÊS_ANO').reindex(labels_x, fill_value=0).reset_index()
                fig.add_trace(go.Scatter(
                    x=dados['MÊS_ANO'],
                    y=dados['VALOR'],
                    mode='lines+markers',
                    name=subcat,
                    text=[f"R$ {v:,.2f}".replace(",", ".") for v in dados['VALOR']],
                    textposition='top center',
                ))
            # Linha de média
            if not evolucao.empty:
                media = evolucao.groupby('MÊS_ANO')['VALOR'].sum().mean()
                fig.add_trace(go.Scatter(
                    x=labels_x,
                    y=[media]*len(labels_x),
                    mode='lines',
                    name='Média',
                ))
            fig.update_layout(
                title=f'Evolução Mensal das Subcategorias em {categoria_selecionada}',
                xaxis_title='Mês/Ano',
                yaxis_title='Valor Gasto (R$)',
                height=480,
                margin=dict(l=30, r=30, t=50, b=120),
                xaxis=dict(
                    tickangle=-35,
                    tickfont=dict(size=13),
                    categoryorder='array',
                    categoryarray=labels_x,
                    type='category'
                ),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('Não há despesas para exibir por subcategoria com os filtros selecionados.')

# --- GRUPO DE ANÁLISE DE VENDAS ---
if selected == "Vendas":
    st.markdown('## 📈 Análise de Vendas')
    
    # Carrega e processa os dados de vendas
    df_vendas = pd.read_excel(xls, sheet_name='Vendas')
    df_vendas['DATA'] = pd.to_datetime(df_vendas['DATA'], errors='coerce')
    df_vendas = df_vendas.dropna(subset=['DATA'])
    df_vendas['Ano'] = df_vendas['DATA'].dt.year.astype(str)
    df_vendas['Mês'] = df_vendas['DATA'].dt.strftime('%b').str.capitalize().replace({'Feb': 'Fev', 'Apr': 'Abr', 'May': 'Mai', 'Aug': 'Ago', 'Sep': 'Set', 'Oct': 'Out', 'Dec': 'Dez'})
    
    # Garante que as chaves de filtro de vendas existam no session_state
    for key in ['ano_vendas', 'mes_vendas', 'conta_vendas', 'tipo_receb_vendas', 'pago_vendas']:
        if key not in st.session_state:
            if 'ano' in key or 'mes' in key:
                st.session_state[key] = []
            else:
                st.session_state[key] = 'Todos'
    
    # Recupera os filtros definidos na sidebar
    vendas_filtradas = df_vendas[
        (df_vendas['Ano'].isin(st.session_state['ano_vendas']) if st.session_state['ano_vendas'] else True) &
        (df_vendas['Mês'].isin(st.session_state['mes_vendas']) if st.session_state['mes_vendas'] else True) &
        ((df_vendas['CONTA'] == st.session_state['conta_vendas']) | (st.session_state['conta_vendas'] == 'Todas')) &
        ((df_vendas['TIPO DE RECEBIMENTO'] == st.session_state['tipo_receb_vendas']) | (st.session_state['tipo_receb_vendas'] == 'Todos')) &
        ((df_vendas['PAGO'].astype(str).str.lower() == st.session_state['pago_vendas'].lower()) | (st.session_state['pago_vendas'] == 'Todos'))
    ]

    # Indicadores
    total_vendido = vendas_filtradas['VALOR'].sum()
    num_vendas = len(vendas_filtradas)
    ticket_medio = total_vendido / num_vendas if num_vendas > 0 else 0
    total_recebido = vendas_filtradas[vendas_filtradas['PAGO'].astype(str).str.lower() == 'sim']['VALOR'].sum()
    total_a_receber = vendas_filtradas[vendas_filtradas['PAGO'].astype(str).str.lower() == 'não']['VALOR'].sum()

    st.markdown('---')
    # Indicadores de vendas com cartões escuros padronizados
    colv1, colv2, colv3, colv4, colv5 = st.columns(5)
    with colv1:
        st.metric("Total Vendido", format_brl(total_vendido))
    with colv2:
        st.metric("Nº de Vendas", num_vendas)
    with colv3:
        st.metric("Ticket Médio", format_brl(ticket_medio))
    with colv4:
        st.metric("Total Recebido", format_brl(total_recebido))
    with colv5:
        st.metric("Total a Receber", format_brl(total_a_receber))

    # Gráficos de rosca lado a lado
    st.markdown('---')
    colg1, colg2 = st.columns(2)
    with colg1:
        # Vendas por cliente (top 5 em valor)
        if not vendas_filtradas.empty:
            top_clientes = vendas_filtradas.groupby('DESCRIÇÃO')['VALOR'].sum().sort_values(ascending=False).head(5)
            fig_cli = px.pie(names=top_clientes.index, values=top_clientes.values, hole=0.5, title='Top 5 Clientes (Valor)')
            fig_cli.update_traces(textinfo='percent', textposition='outside', pull=[0.05]*5, textfont=dict(family='Arial', size=16, color='white'), textfont_weight='bold')
            fig_cli.update_layout(
                title_font_size=22,
                legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5, font=dict(size=13))
            )
            st.plotly_chart(fig_cli, use_container_width=True)
            # Top 5 clientes em quantidade de vendas
            top_clientes_qtd = vendas_filtradas['DESCRIÇÃO'].value_counts().head(5)
            fig_cli_qtd = px.pie(names=top_clientes_qtd.index, values=top_clientes_qtd.values, hole=0.5, title='Top 5 Clientes (Qtd. Vendas)')
            fig_cli_qtd.update_traces(textinfo='percent', textposition='outside', pull=[0.05]*5, textfont=dict(family='Arial', size=16, color='white'), textfont_weight='bold')
            fig_cli_qtd.update_layout(
                title_font_size=22,
                legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5, font=dict(size=13))
            )
            st.plotly_chart(fig_cli_qtd, use_container_width=True)
        else:
            st.info('Não há vendas para exibir por cliente.')
    with colg2:
        # Vendas por tipo de recebimento
        if not vendas_filtradas.empty:
            tipo_receb = vendas_filtradas.groupby('TIPO DE RECEBIMENTO')['VALOR'].sum().sort_values(ascending=False)
            fig_tipo = px.pie(names=tipo_receb.index, values=tipo_receb.values, hole=0.5, title='Por Tipo de Recebimento')
            fig_tipo.update_traces(textinfo='percent', textposition='outside', textfont=dict(family='Arial', size=16, color='white'), textfont_weight='bold')
            fig_tipo.update_layout(
                title_font_size=22,
                legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5, font=dict(size=13))
            )
            st.plotly_chart(fig_tipo, use_container_width=True)
        else:
            st.info('Não há vendas para exibir por tipo de recebimento.')

    # Gráfico de evolução das vendas (abaixo dos roscas)
    st.markdown('---')
    st.markdown('#### Evolução Mensal das Vendas')
    if not vendas_filtradas.empty:
        evol = vendas_filtradas.groupby(['Ano', 'Mês'])['VALOR'].sum().reset_index()
        evol['MÊS_NUM'] = evol['Mês'].apply(lambda x: meses_ordem.index(x) if x in meses_ordem else -1)
        evol = evol.sort_values(['Ano', 'MÊS_NUM'])
        evol['MêsAno'] = evol['Mês'] + '/' + evol['Ano']
        fig_evol = px.bar(
            evol,
            x='MêsAno',
            y='VALOR',
            labels={'MêsAno':'Mês/Ano','VALOR':'Total Vendido'},
            text=evol['VALOR'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "."))
        )
        fig_evol.update_traces(textposition='auto', textfont_size=14)
        fig_evol.update_layout(xaxis_tickangle=-35, height=320, margin=dict(t=60, b=40, l=0, r=0))
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info('Não há vendas para exibir evolução.')

    # Tabela detalhada
    st.markdown('---')
    st.markdown('### Tabela Detalhada de Vendas')
    if not vendas_filtradas.empty:
        df_tab = vendas_filtradas.copy()
        df_tab['DATA'] = df_tab['DATA'].dt.strftime('%d/%m/%Y')
        df_tab = df_tab.rename(columns={'DATA':'Data','DESCRIÇÃO':'Cliente','CONTA':'Conta','TIPO DE RECEBIMENTO':'Tipo de Recebimento','VALOR':'Valor','PAGO':'Pago'})
        df_tab['Valor'] = df_tab['Valor'].apply(format_brl)
        st.dataframe(df_tab[['Data','Cliente','Conta','Tipo de Recebimento','Valor','Pago']], use_container_width=True, hide_index=True)
    else:
        st.info('Não há vendas para exibir na tabela.')

# --- GRUPO DE ANÁLISE DE INVESTIMENTOS ---
if selected == "Investimentos":
    st.markdown('## 💰 Análise de Investimentos')
    
    # Carrega dados de investimentos e metas
    df_investimentos = pd.read_excel(xls, sheet_name='Investimentos')
    df_metas = pd.read_excel(xls, sheet_name='Metas')
    
    # Processa dados de investimentos
    df_investimentos['DATA'] = pd.to_datetime(df_investimentos['DATA'], errors='coerce')
    df_investimentos = df_investimentos.dropna(subset=['DATA'])
    df_investimentos['Ano'] = df_investimentos['DATA'].dt.year.astype(str)
    df_investimentos['Mês'] = df_investimentos['DATA'].dt.strftime('%b').str.capitalize().replace({'Feb': 'Fev', 'Apr': 'Abr', 'May': 'Mai', 'Aug': 'Ago', 'Sep': 'Set', 'Oct': 'Out', 'Dec': 'Dez'})
    
    # Aplica filtros
    investimentos_filtrados = df_investimentos[
        (df_investimentos['Ano'].isin(st.session_state.get('ano_invest', [])) if st.session_state.get('ano_invest') else True) &
        (df_investimentos['Mês'].isin(st.session_state.get('mes_invest', [])) if st.session_state.get('mes_invest') else True) &
        ((df_investimentos['TIPO'] == st.session_state.get('tipo_invest', 'Todos')) | (st.session_state.get('tipo_invest', 'Todos') == 'Todos')) &
        ((df_investimentos['OBJETIVO'] == st.session_state.get('objetivo_invest', 'Todos')) | (st.session_state.get('objetivo_invest', 'Todos') == 'Todos')) &
        ((df_investimentos['ATIVO'] == st.session_state.get('ativo_invest', 'Todos')) | (st.session_state.get('ativo_invest', 'Todos') == 'Todos'))
    ]
    
    # Calcula indicadores
    total_investido = investimentos_filtrados['VALOR_APORTE'].sum()
    num_aportes = len(investimentos_filtrados)
    valor_medio_aporte = total_investido / num_aportes if num_aportes > 0 else 0
    
    # Calcula progresso das metas
    ano_atual = datetime.now().year
    meta_atual = df_metas[df_metas['ANO'] == ano_atual]['META_TOTAL'].sum()
    progresso_meta = (total_investido / meta_atual * 100) if meta_atual > 0 else 0
    falta_para_meta = meta_atual - total_investido if meta_atual > total_investido else 0
    
    # Exibe indicadores principais
    st.markdown('---')
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Investido", format_brl(total_investido))
    with col2:
        st.metric("Nº de Aportes", num_aportes)
    with col3:
        st.metric("Valor Médio", format_brl(valor_medio_aporte))
    with col4:
        st.metric("Meta Anual", format_brl(meta_atual))
    with col5:
        st.metric("Progresso", f"{progresso_meta:.1f}%")
    
    # Barra de progresso da meta
    st.markdown('---')
    st.markdown('### 📊 Progresso da Meta Anual')
    col_prog1, col_prog2 = st.columns([3, 1])
    with col_prog1:
        st.progress(progresso_meta / 100)
    with col_prog2:
        if falta_para_meta > 0:
            st.metric("Falta", format_brl(falta_para_meta), delta="Para meta")
        else:
            st.metric("Meta Atingida! 🎉", format_brl(0), delta="Parabéns!")
    
    # Gráficos de análise
    st.markdown('---')
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        # Distribuição por tipo de investimento
        if not investimentos_filtrados.empty:
            tipo_dist = investimentos_filtrados.groupby('TIPO')['VALOR_APORTE'].sum().sort_values(ascending=False)
            fig_tipo = px.pie(
                names=tipo_dist.index, 
                values=tipo_dist.values, 
                hole=0.5, 
                title='Distribuição por Tipo de Investimento',
            )
            fig_tipo.update_traces(
                textinfo='percent+label', 
                textposition='outside',
                textfont=dict(family='Arial', size=14, color='white')
            )
            fig_tipo.update_layout(
                title_font_size=20,
                legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
            )
            st.plotly_chart(fig_tipo, use_container_width=True)
        else:
            st.info('Não há investimentos para exibir.')
    
    with col_graf2:
        # Distribuição por objetivo
        if not investimentos_filtrados.empty:
            obj_dist = investimentos_filtrados.groupby('OBJETIVO')['VALOR_APORTE'].sum().sort_values(ascending=False)
            fig_obj = px.pie(
                names=obj_dist.index, 
                values=obj_dist.values, 
                hole=0.5, 
                title='Distribuição por Objetivo',
            )
            fig_obj.update_traces(
                textinfo='percent+label', 
                textposition='outside',
                textfont=dict(family='Arial', size=14, color='white')
            )
            fig_obj.update_layout(
                title_font_size=20,
                legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
            )
            st.plotly_chart(fig_obj, use_container_width=True)
        else:
            st.info('Não há investimentos para exibir.')
    
    # Gráfico de evolução mensal
    st.markdown('---')
    st.markdown('### 📈 Evolução Mensal dos Aportes')
    if not investimentos_filtrados.empty:
        evol_mensal = investimentos_filtrados.groupby(['Ano', 'Mês'])['VALOR_APORTE'].sum().reset_index()
        evol_mensal['MÊS_NUM'] = evol_mensal['Mês'].apply(lambda x: meses_ordem.index(x) if x in meses_ordem else -1)
        evol_mensal = evol_mensal.sort_values(['Ano', 'MÊS_NUM'])
        evol_mensal['MêsAno'] = evol_mensal['Mês'] + '/' + evol_mensal['Ano']
        
        fig_evol = px.bar(
            evol_mensal,
            x='MêsAno',
            y='VALOR_APORTE',
            labels={'MêsAno':'Mês/Ano','VALOR_APORTE':'Total Aportado'},
            text=evol_mensal['VALOR_APORTE'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "."))
        )
        fig_evol.update_traces(textposition='auto', textfont_size=12)
        fig_evol.update_layout(
            xaxis_tickangle=-35, 
            height=400, 
            margin=dict(t=60, b=40, l=0, r=0),
            title='Evolução dos Aportes por Mês'
        )
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info('Não há dados suficientes para exibir a evolução mensal.')
    
    # Top 10 ativos mais investidos
    st.markdown('---')
    st.markdown('### 🏆 Top 10 Ativos Mais Investidos')
    if not investimentos_filtrados.empty:
        top_ativos = investimentos_filtrados.groupby('ATIVO')['VALOR_APORTE'].sum().sort_values(ascending=False).head(10)
        fig_top = px.bar(
            x=top_ativos.values,
            y=top_ativos.index,
            orientation='h',
            labels={'x':'Valor Investido (R$)', 'y':'Ativo'},
            text=[f"R$ {x:,.2f}".replace(",", ".") for x in top_ativos.values]
        )
        fig_top.update_traces(textposition='auto', textfont_size=11)
        fig_top.update_layout(
            height=500,
            margin=dict(t=40, b=40, l=0, r=0),
            title='Top 10 Ativos por Valor Investido'
        )
        st.plotly_chart(fig_top, use_container_width=True)
    else:
        st.info('Não há dados suficientes para exibir o ranking de ativos.')
    
    # Tabela detalhada de investimentos
    st.markdown('---')
    st.markdown('### 📋 Tabela Detalhada de Investimentos')
    if not investimentos_filtrados.empty:
        df_tab = investimentos_filtrados.copy()
        df_tab['DATA'] = df_tab['DATA'].dt.strftime('%d/%m/%Y')
        df_tab = df_tab.rename(columns={
            'DATA':'Data',
            'TIPO':'Tipo',
            'ATIVO':'Ativo',
            'VALOR_APORTE':'Valor Aportado',
            'QUANTIDADE':'Quantidade',
            'PRECO_MEDIO':'Preço Médio',
            'OBJETIVO':'Objetivo'
        })
        df_tab['Valor Aportado'] = df_tab['Valor Aportado'].apply(format_brl)
        df_tab['Preço Médio'] = df_tab['Preço Médio'].apply(format_brl)
        st.dataframe(
            df_tab[['Data','Tipo','Ativo','Valor Aportado','Quantidade','Preço Médio','Objetivo']], 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info('Não há investimentos para exibir na tabela.') 

# --- GRUPO DE ANÁLISE DE CARTÃO DE CRÉDITO ---
elif selected == "Cartão de Crédito":
    st.markdown('## 💳 Análise de Cartão de Crédito')
    
    st.markdown("---")
    
    # Carregar dados
    df_cc = pd.read_excel(xls, sheet_name='Div_CC')
    df_cc['Data'] = pd.to_datetime(df_cc['Data'], errors='coerce')
    df_cc.dropna(subset=['Data'], inplace=True)
    df_cc['Ano'] = df_cc['Data'].dt.year.astype(str)
    df_cc['Mês'] = df_cc['Data'].dt.strftime('%b').str.capitalize().replace({'Feb': 'Fev', 'Apr': 'Abr', 'May': 'Mai', 'Aug': 'Ago', 'Sep': 'Set', 'Oct': 'Out', 'Dec': 'Dez'})
    
    # Aplicar filtros usando as variáveis da sidebar
    cc_filtrado = df_cc[
        (df_cc['Ano'].isin(anos_cc_sel) if anos_cc_sel else True) &
        (df_cc['Mês'].isin(meses_cc_sel) if meses_cc_sel else True) &
        ((df_cc['Cartão'] == cartao_cc_sel) | (cartao_cc_sel == 'Todos')) &
        ((df_cc['Situação'] == situacao_cc_sel) | (situacao_cc_sel == 'Todas')) &
        ((df_cc['Tipo de Compra'] == tipo_compra_sel) | (tipo_compra_sel == 'Todos')) &
        ((df_cc['Quantidade de parcelas'].astype(str) == parcelas_sel) | (parcelas_sel == 'Todas'))
    ]

    # Exibir KPIs
    if cc_filtrado.empty:
        st.info("Não há dados para exibir com os filtros selecionados.")
    else:
        st.markdown("---")
        total_compras = cc_filtrado['valor total da compra'].sum()
        total_parcelas = cc_filtrado['Valor das parcelas'].sum()
        qtd_compras = len(cc_filtrado)
        media_compra = total_compras / qtd_compras if qtd_compras > 0 else 0
        total_pago = cc_filtrado[cc_filtrado['Situação'] == 'Pago']['valor total da compra'].sum()
        total_pendente = cc_filtrado[cc_filtrado['Situação'] == 'Pendente']['valor total da compra'].sum()

        # Calcular próximas faturas
        hoje = datetime.now()
        
        # Filtra compras pendentes com vencimento futuro
        proximas_faturas = cc_filtrado[
            (cc_filtrado['Situação'] == 'Pendente') & 
            (pd.to_datetime(cc_filtrado['Vencimento da Fatura']) > hoje)
        ]
        
        # Agrupa por vencimento e soma os valores
        if not proximas_faturas.empty:
            proximas_faturas['Vencimento da Fatura'] = pd.to_datetime(proximas_faturas['Vencimento da Fatura'])
            faturas_por_vencimento = proximas_faturas.groupby('Vencimento da Fatura')['valor total da compra'].sum().sort_index()
            
            # Pega as próximas 3 faturas
            proximas_3_faturas = faturas_por_vencimento.head(3)
            total_proximas_faturas = proximas_3_faturas.sum()
            
            # Formata as próximas faturas para exibição
            proximas_faturas_texto = []
            for vencimento, valor in proximas_3_faturas.items():
                data_str = vencimento.strftime('%d/%m/%Y')
                valor_str = format_brl(valor)
                proximas_faturas_texto.append(f"{data_str}: {valor_str}")
            
            proximas_faturas_display = "<br>".join(proximas_faturas_texto) if proximas_faturas_texto else "Nenhuma fatura pendente"
        else:
            total_proximas_faturas = 0
            proximas_faturas_display = "Nenhuma fatura pendente"

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Total das Compras", format_brl(total_compras))
        col2.metric("Total Pago", format_brl(total_pago))
        col3.metric("Total Pendente", format_brl(total_pendente))
        col4.metric("Qtd. Compras", qtd_compras)
        col5.metric("Valor Médio", format_brl(media_compra))
        
        # Card especial para próximas faturas
        with col6:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(to right, #ff6b6b, #ee5a24);">
                <h4>Próximas Faturas</h4>
                <h2>{format_brl(total_proximas_faturas)}</h2>
                <div style="font-size: 0.8rem; margin-top: 8px; opacity: 0.9;">
                    {proximas_faturas_display}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Exibir Gráficos
        st.markdown("---")
        colg1, colg2 = st.columns(2)

        with colg1:
            st.markdown('#### Gastos por Cartão')
            gastos_cartao = cc_filtrado.groupby('Cartão')['valor total da compra'].sum().sort_values(ascending=False)
            if not gastos_cartao.empty:
                fig_cartao = px.bar(
                    gastos_cartao,
                    x=gastos_cartao.index,
                    y=gastos_cartao.values,
                    title='Gastos Totais por Cartão',
                    labels={'y': 'Valor Total (R$)', 'index': 'Cartão'},
                    text=gastos_cartao.apply(lambda x: format_brl(x))
                )
                fig_cartao.update_layout(showlegend=False, xaxis_title="", yaxis_title="Valor (R$)", title_x=0.2)
                st.plotly_chart(fig_cartao, use_container_width=True)
            else:
                st.info("Sem dados para o gráfico de cartões.")

        with colg2:
            st.markdown('#### Gastos por Tipo de Compra')
            gastos_tipo = cc_filtrado.groupby('Tipo de Compra')['valor total da compra'].sum().sort_values(ascending=False)
            if not gastos_tipo.empty:
                fig_tipo = px.pie(
                    names=gastos_tipo.index,
                    values=gastos_tipo.values,
                    title='Distribuição por Tipo de Compra',
                    hole=0.4
                )
                fig_tipo.update_traces(textposition='inside', textinfo='percent+label')
                fig_tipo.update_layout(showlegend=False, title_x=0.2)
                st.plotly_chart(fig_tipo, use_container_width=True)
            else:
                st.info("Sem dados para o gráfico de tipos de compra.")

        # Segunda linha de gráficos
        st.markdown("---")
        colg3, colg4 = st.columns(2)

        with colg3:
            st.markdown('#### Distribuição por Situação')
            situacao_dist = cc_filtrado.groupby('Situação')['valor total da compra'].sum()
            if not situacao_dist.empty:
                fig_sit = px.pie(
                    names=situacao_dist.index,
                    values=situacao_dist.values,
                    title='Distribuição por Situação',
                    hole=0.4
                )
                fig_sit.update_traces(textposition='inside', textinfo='percent+label')
                fig_sit.update_layout(showlegend=False, title_x=0.2)
                st.plotly_chart(fig_sit, use_container_width=True)
            else:
                st.info("Sem dados para o gráfico de situação.")

        with colg4:
            st.markdown('#### Distribuição por Parcelas')
            parcelas_dist = cc_filtrado.groupby('Quantidade de parcelas')['valor total da compra'].sum().sort_values(ascending=False)
            if not parcelas_dist.empty:
                fig_parc = px.bar(
                    x=parcelas_dist.index.astype(str),
                    y=parcelas_dist.values,
                    title='Gastos por Quantidade de Parcelas',
                    labels={'x': 'Quantidade de Parcelas', 'y': 'Valor Total (R$)'},
                    text=parcelas_dist.apply(lambda x: format_brl(x))
                )
                fig_parc.update_layout(showlegend=False, xaxis_title="", yaxis_title="Valor (R$)", title_x=0.2)
                st.plotly_chart(fig_parc, use_container_width=True)
            else:
                st.info("Sem dados para o gráfico de parcelas.")

        st.markdown("---")
        st.markdown('#### Evolução dos Gastos no Cartão')
        evolucao_gastos = cc_filtrado.groupby(['Ano', 'Mês'])['valor total da compra'].sum().reset_index()
        meses_ordem = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        evolucao_gastos['MêsNum'] = pd.Categorical(evolucao_gastos['Mês'], categories=meses_ordem, ordered=True)
        evolucao_gastos = evolucao_gastos.sort_values(['Ano', 'MêsNum'])
        evolucao_gastos['MêsAno'] = evolucao_gastos['Mês'] + '/' + evolucao_gastos['Ano'].astype(str)

        if not evolucao_gastos.empty:
            fig_evol = px.line(
                evolucao_gastos,
                x='MêsAno',
                y='valor total da compra',
                title='Evolução Mensal dos Gastos',
                labels={'valor total da compra': 'Valor Total (R$)', 'MêsAno': 'Mês/Ano'},
                markers=True
            )
            fig_evol.update_traces(text=evolucao_gastos['valor total da compra'].apply(lambda x: format_brl(x)), textposition="top center")
            fig_evol.update_layout(xaxis_title="", yaxis_title="Valor (R$)", title_x=0.1)
            st.plotly_chart(fig_evol, use_container_width=True)
        else:
            st.info("Sem dados para o gráfico de evolução.")

        # Gráfico de próximas faturas por cartão
        st.markdown("---")
        st.markdown('#### Próximas Faturas por Cartão')
        if not proximas_faturas.empty:
            proximas_por_cartao = proximas_faturas.groupby('Cartão')['valor total da compra'].sum().sort_values(ascending=False)
            fig_proximas = px.bar(
                proximas_por_cartao,
                x=proximas_por_cartao.index,
                y=proximas_por_cartao.values,
                title='Valor das Próximas Faturas por Cartão',
                labels={'y': 'Valor da Fatura (R$)', 'index': 'Cartão'},
                text=proximas_por_cartao.apply(lambda x: format_brl(x))
            )
            fig_proximas.update_layout(showlegend=False, xaxis_title="", yaxis_title="Valor (R$)", title_x=0.2)
            st.plotly_chart(fig_proximas, use_container_width=True)
        else:
            st.info("Não há faturas pendentes para exibir.")

        # Exibir Tabela detalhada
        st.markdown("---")
        st.markdown('#### Detalhes das Compras')
        df_tabela_cc = cc_filtrado.copy()
        df_tabela_cc['Data'] = df_tabela_cc['Data'].dt.strftime('%d/%m/%Y')
        df_tabela_cc['Vencimento da Fatura'] = pd.to_datetime(df_tabela_cc['Vencimento da Fatura']).dt.strftime('%d/%m/%Y')
        df_tabela_cc['valor total da compra'] = df_tabela_cc['valor total da compra'].apply(format_brl)
        df_tabela_cc['Valor das parcelas'] = df_tabela_cc['Valor das parcelas'].apply(format_brl)
        st.dataframe(
            df_tabela_cc[['Data', 'Descrição', 'Tipo de Compra', 'Cartão', 'Quantidade de parcelas', 'Valor das parcelas', 'valor total da compra', 'Situação', 'Vencimento da Fatura']],
            use_container_width=True,
            hide_index=True,
        )
        
        # Botão de exportação de relatório (movido para o final)
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📄 Exportar Relatório PDF", type="primary", use_container_width=True):
                # Criar instância do gerador de relatórios
                relatorio = RelatorioPDF()
                
                # Preparar dados para o relatório
                dados_relatorio = {
                    'total_compras': total_compras,
                    'total_pago': total_pago,
                    'total_pendente': total_pendente,
                    'qtd_compras': qtd_compras,
                    'media_compra': media_compra,
                    'proximas_faturas': total_proximas_faturas,
                    'graficos': [],
                    'tabela_compras': cc_filtrado[['Data', 'Cartão', 'Descrição', 'valor total da compra', 'Situação', 'Tipo de Compra', 'Quantidade de parcelas']].copy()
                }
                
                # Adicionar gráficos se existirem dados
                if not cc_filtrado.empty:
                    # Gráfico de gastos por cartão
                    gastos_cartao = cc_filtrado.groupby('Cartão')['valor total da compra'].sum().sort_values(ascending=False)
                    if not gastos_cartao.empty:
                        fig_cartao = px.bar(
                            gastos_cartao,
                            x=gastos_cartao.index,
                            y=gastos_cartao.values,
                            title='Gastos Totais por Cartão',
                            labels={'y': 'Valor Total (R$)', 'index': 'Cartão'},
                            text=gastos_cartao.apply(lambda x: format_brl(x))
                        )
                        dados_relatorio['graficos'].append({
                            'titulo': 'Gastos Totais por Cartão',
                            'fig': fig_cartao,
                            'descricao': 'Distribuição dos gastos por cartão de crédito'
                        })
                    
                    # Gráfico de evolução mensal
                    evolucao_gastos = cc_filtrado.groupby(['Ano', 'Mês'])['valor total da compra'].sum().reset_index()
                    meses_ordem = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                    evolucao_gastos['MêsNum'] = pd.Categorical(evolucao_gastos['Mês'], categories=meses_ordem, ordered=True)
                    evolucao_gastos = evolucao_gastos.sort_values(['Ano', 'MêsNum'])
                    evolucao_gastos['MêsAno'] = evolucao_gastos['Mês'] + '/' + evolucao_gastos['Ano'].astype(str)
                    
                    if not evolucao_gastos.empty:
                        fig_evol = px.line(
                            evolucao_gastos,
                            x='MêsAno',
                            y='valor total da compra',
                            title='Evolução Mensal dos Gastos',
                            labels={'valor total da compra': 'Valor Total (R$)', 'MêsAno': 'Mês/Ano'},
                            markers=True
                        )
                        dados_relatorio['graficos'].append({
                            'titulo': 'Evolução Mensal dos Gastos',
                            'fig': fig_evol,
                            'descricao': 'Análise da evolução dos gastos no cartão de crédito ao longo do tempo'
                        })
                
                # Gerar relatório
                try:
                    filename = relatorio.generate_credit_card_report(dados_relatorio, "relatorio_cartao_credito.pdf")
                    st.success("✅ Relatório gerado com sucesso!")
                    create_download_button(filename, "📥 Download Relatório Cartão de Crédito")
                except Exception as e:
                    st.error(f"❌ Erro ao gerar relatório: {e}")

# --- GRUPO DE ANÁLISE DE ORÇAMENTO ---
elif selected == "Orçamento":
    st.header("📊 Módulo de Orçamento Mensal")
    st.markdown("---")
    
    # Carregar configuração de orçamento
    try:
        df_orcamento = pd.read_excel(xls, sheet_name='Orcamento')
    except:
        st.error("Aba 'Orcamento' não encontrada. Execute o script 'criar_aba_orcamento.py' primeiro.")
        st.stop()
    
    # Calcular renda líquida (receitas - despesas "Confeitaria")
    receitas_mes = receitas_filtradas['VALOR'].sum()
    despesas_confeitaria = despesas_filtradas[despesas_filtradas['CATEGORIA'] == 'Confeitaria']['VALOR'].sum()
    renda_liquida = receitas_mes - abs(despesas_confeitaria)
    
    # Cards de resumo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Receitas do Mês", f"R$ {receitas_mes:,.2f}")
    with col2:
        st.metric("🍰 Despesas Confeitaria", f"R$ {abs(despesas_confeitaria):,.2f}")
    with col3:
        st.metric("💵 Renda Líquida", f"R$ {renda_liquida:,.2f}")
    
    st.markdown("---")
    
    # Título da seção de orçamento
    st.subheader("🎯 Orçamento por Categoria")
    st.markdown(f"*Baseado em {renda_liquida:,.2f} de renda líquida*")
    
    # Criar colunas para o layout
    col_orc, col_prog = st.columns([1, 2])
    
    with col_orc:
        st.markdown("**📋 Configuração do Orçamento**")
        
        # Tabela com as porcentagens
        df_orc_display = df_orcamento.copy()
        df_orc_display['Valor Orçado'] = (df_orc_display['Porcentagem'] / 100) * renda_liquida
        df_orc_display['Valor Orçado'] = df_orc_display['Valor Orçado'].round(2)
        
        st.dataframe(
            df_orc_display[['Categoria', 'Porcentagem', 'Valor Orçado']],
            use_container_width=True,
            hide_index=True
        )
    
    with col_prog:
        st.markdown("**📈 Progresso Real vs Orçado**")
        
        # Calcular gastos reais por categoria
        gastos_por_categoria = despesas_filtradas.groupby('CATEGORIA')['VALOR'].sum().abs()
        
        # Criar gráfico de barras de progresso
        fig_orcamento = go.Figure()
        
        for _, row in df_orcamento.iterrows():
            categoria = row['Categoria']
            valor_orcado = (row['Porcentagem'] / 100) * renda_liquida
            valor_gasto = gastos_por_categoria.get(categoria, 0)
            percentual_gasto = (valor_gasto / valor_orcado * 100) if valor_orcado > 0 else 0
            
            # Definir cor baseada no percentual
            if percentual_gasto >= 100:
                cor = '#FF4444'  # Vermelho - ultrapassou
            elif percentual_gasto >= 80:
                cor = '#FFAA00'  # Laranja - próximo do limite
            else:
                cor = '#44AA44'  # Verde - dentro do limite
            
            # Barra de progresso
            fig_orcamento.add_trace(go.Bar(
                name=categoria,
                x=[categoria],
                y=[valor_gasto],
                width=0.6,
                marker_color=cor,
                hovertemplate=f'<b>{categoria}</b><br>' +
                             f'Orçado: R$ {valor_orcado:,.2f}<br>' +
                             f'Gasto: R$ {valor_gasto:,.2f}<br>' +
                             f'Progresso: {percentual_gasto:.1f}%<br>' +
                             f'Restante: R$ {max(0, valor_orcado - valor_gasto):,.2f}<extra></extra>'
            ))
            
            # Linha do limite orçado
            fig_orcamento.add_trace(go.Scatter(
                name=f'{categoria} (Limite)',
                x=[categoria],
                y=[valor_orcado],
                mode='markers',
                marker=dict(symbol='diamond', size=12, color='#333333'),
                showlegend=False,
                hovertemplate=f'Limite: R$ {valor_orcado:,.2f}<extra></extra>'
            ))
        
        fig_orcamento.update_layout(
            title="Gastos Reais vs Orçado por Categoria",
            xaxis_title="Categoria",
            yaxis_title="Valor (R$)",
            height=400,
            showlegend=False,
            barmode='group'
        )
        
        st.plotly_chart(fig_orcamento, use_container_width=True)
    
    # Seção de alertas
    st.markdown("---")
    st.subheader("⚠️ Alertas de Orçamento")
    
    alertas = []
    for _, row in df_orcamento.iterrows():
        categoria = row['Categoria']
        valor_orcado = (row['Porcentagem'] / 100) * renda_liquida
        valor_gasto = gastos_por_categoria.get(categoria, 0)
        percentual_gasto = (valor_gasto / valor_orcado * 100) if valor_orcado > 0 else 0
        
        if percentual_gasto >= 100:
            alertas.append(f"🔴 **{categoria}**: Ultrapassou o orçamento em R$ {valor_gasto - valor_orcado:,.2f}")
        elif percentual_gasto >= 80:
            alertas.append(f"🟡 **{categoria}**: {percentual_gasto:.1f}% do orçamento usado (R$ {valor_orcado - valor_gasto:,.2f} restantes)")
    
    if alertas:
        for alerta in alertas:
            st.warning(alerta)
    else:
        st.success("✅ Todas as categorias estão dentro do orçamento!")
    
    # Resumo final
    st.markdown("---")
    st.subheader("📊 Resumo Geral")
    
    total_orcado = renda_liquida
    total_gasto = gastos_por_categoria.sum()
    percentual_total = (total_gasto / total_orcado * 100) if total_orcado > 0 else 0
    
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric("Total Orçado", f"R$ {total_orcado:,.2f}")
    with col_res2:
        st.metric("Total Gasto", f"R$ {total_gasto:,.2f}")
    with col_res3:
        st.metric("Percentual Utilizado", f"{percentual_total:.1f}%")
    
    # Barra de progresso geral
    st.progress(min(percentual_total / 100, 1.0))
    if percentual_total > 100:
        st.error(f"⚠️ Orçamento total ultrapassado em {percentual_total - 100:.1f}%")
    elif percentual_total > 90:
        st.warning(f"⚠️ {percentual_total:.1f}% do orçamento total utilizado")
    else:
        st.success(f"✅ {percentual_total:.1f}% do orçamento total utilizado")
    
    # Botão de exportação de relatório (movido para o final)
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📄 Exportar Relatório PDF", type="primary", use_container_width=True):
            # Criar instância do gerador de relatórios
            relatorio = RelatorioPDF()
            
            # Preparar dados para o relatório
            dados_relatorio = {
                'renda_liquida': renda_liquida,
                'total_orcado': total_orcado,
                'total_gasto': total_gasto,
                'percentual_total': percentual_total,
                'config_orcamento': df_orc_display[['Categoria', 'Porcentagem', 'Valor Orçado']],
                'grafico_progresso': fig_orcamento,
                'alertas': alertas
            }
            
            # Gerar relatório
            try:
                filename = relatorio.generate_budget_report(dados_relatorio, "relatorio_orcamento.pdf")
                st.success("✅ Relatório gerado com sucesso!")
                create_download_button(filename, "📥 Download Relatório Orçamento")
            except Exception as e:
                st.error(f"❌ Erro ao gerar relatório: {e}")

# --- LÓGICA DOS MODAIS DE LANÇAMENTO ---

# Função genérica para salvar dados no Excel
def save_transaction(df_new, sheet_name):
    try:
        with st.spinner(f"Salvando em {sheet_name}..."):
            # Usar um lock para evitar concorrência no futuro
            from threading import Lock
            excel_lock = Lock()
            with excel_lock:
                dfs = pd.read_excel(excel_path, sheet_name=None)
                
                sheet_df = dfs.get(sheet_name)
                
                # Garante a consistência dos tipos de dados antes de concatenar
                for col in sheet_df.columns:
                    if col in df_new.columns:
                        if pd.api.types.is_datetime64_any_dtype(sheet_df[col]):
                            df_new[col] = pd.to_datetime(df_new[col])
                        else:
                            df_new[col] = df_new[col].astype(sheet_df[col].dtype, errors='ignore')
                
                updated_df = pd.concat([sheet_df, df_new], ignore_index=True)
                dfs[sheet_name] = updated_df

                with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                    for name, df_sheet in dfs.items():
                        df_sheet.to_excel(writer, sheet_name=name, index=False)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar no Excel: {e}")
        return False

# Modal para Nova Despesa
if st.session_state.get("show_despesa_form", False):
    st.subheader("📝 Lançar Nova Despesa")
    with st.container():
        with st.form("despesa_form", clear_on_submit=True):
            st.subheader("Preencha os dados da despesa:")
            # Ler dados para os selects
            df_conta = pd.read_excel(xls, sheet_name='Conta')
            contas = df_conta['Contas'].dropna().unique().tolist()
            df_cat_desp = pd.read_excel(xls, sheet_name='Despesas Categoria')
            categorias_desp = df_cat_desp.columns.tolist()

            c1, c2 = st.columns(2)
            data_despesa = c1.date_input("Data", datetime.now(), key="data_despesa")
            valor_despesa = c2.number_input("Valor (negativo)", value=0.0, format="%.2f", key="valor_despesa")
            
            c3, c4 = st.columns(2)
            categoria_despesa = c3.selectbox("Categoria", sorted(categorias_desp), key="cat_despesa")
            conta_despesa = c4.selectbox("Conta de Origem", sorted(contas), key="conta_despesa")
            
            # Carregar itens da categoria selecionada para validação
            itens_despesas, _ = carregar_itens_categoria()
            itens_categoria = itens_despesas.get(categoria_despesa, [])
            
            # Campo de descrição com validação
            st.write("**Descrição**")
            
            # Permitir seleção de item existente ou digitação livre
            opcao_descricao = st.selectbox(
                "Selecione um item da categoria ou digite livremente:",
                ["Digite livremente"] + sorted(itens_categoria),
                key="opcao_desc_despesa"
            )
            
            if opcao_descricao == "Digite livremente":
                descricao_despesa = st.text_input("Digite a descrição:", key="desc_despesa_livre")
            else:
                descricao_despesa = opcao_descricao
                st.success(f"✅ Item selecionado: {descricao_despesa}")
            
            # Campos FAVORECIDO e PAGO
            c5, c6 = st.columns(2)
            favorecido_despesa = c5.text_input("Favorecido", key="fav_despesa")
            pago_despesa = c6.selectbox("Status do Pagamento", ["Pago", "Pendente"], key="pago_despesa")
            
            # Converter para valor numérico (1 = Pago, 0 = Pendente)
            pago_valor = 1.0 if pago_despesa == "Pago" else 0.0

            col_submit, col_cancel = st.columns(2)
            submitted = col_submit.form_submit_button("✔️ Salvar Despesa", use_container_width=True, type="primary")
            if col_cancel.form_submit_button("✖️ Cancelar", use_container_width=True):
                st.session_state.show_despesa_form = False
                st.rerun()

            if submitted:
                if not descricao_despesa or valor_despesa == 0:
                    st.warning("Descrição e Valor são obrigatórios.")
                elif valor_despesa > 0:
                    st.warning("O valor da despesa deve ser negativo.")
                else:
                    new_data = pd.DataFrame([{
                        'DATA': pd.to_datetime(data_despesa), 
                        'FAVORECIDO': favorecido_despesa if favorecido_despesa else 'N/A',
                        'DESCRIÇÃO': descricao_despesa, 
                        'CATEGORIA': categoria_despesa, 
                        'CONTA': conta_despesa,
                        'FORMA DE PAGAMENTO': 'N/A', 
                        'VALOR': valor_despesa,
                        'PAGO': pago_valor
                    }])
                    if save_transaction(new_data, "Despesas"):
                        st.success("Despesa salva com sucesso!")
                        st.session_state.show_despesa_form = False
                        st.rerun()

# Modal para Nova Receita
if st.session_state.get("show_receita_form", False):
    st.subheader("💰 Lançar Nova Receita")
    with st.container():
        with st.form("receita_form", clear_on_submit=True):
            st.subheader("Preencha os dados da receita:")
            df_conta = pd.read_excel(xls, sheet_name='Conta')
            contas = df_conta['Contas'].dropna().unique().tolist()
            df_cat_rec = pd.read_excel(xls, sheet_name='Receitas Categoria')
            categorias_rec = df_cat_rec['SUBCATEGORIA'].dropna().unique().tolist()
            
            c1, c2 = st.columns(2)
            data_receita = c1.date_input("Data", datetime.now(), key="data_receita")
            valor_receita = c2.number_input("Valor (positivo)", value=0.00, format="%.2f", min_value=0.0, key="valor_receita")
            
            c3, c4 = st.columns(2)
            categoria_receita = c3.selectbox("Categoria", sorted(categorias_rec), key="cat_receita")
            conta_receita = c4.selectbox("Conta de Destino", sorted(contas), key="conta_receita")
            
            # Campo de descrição com validação para receitas
            _, itens_receitas = carregar_itens_categoria()
            
            st.write("**Descrição**")
            
            # Permitir seleção de item existente ou digitação livre
            opcao_descricao_rec = st.selectbox(
                "Selecione um item da categoria ou digite livremente:",
                ["Digite livremente"] + sorted(itens_receitas),
                key="opcao_desc_receita"
            )
            
            if opcao_descricao_rec == "Digite livremente":
                descricao_receita = st.text_input("Digite a descrição:", key="desc_receita_livre")
            else:
                descricao_receita = opcao_descricao_rec
                st.success(f"✅ Item selecionado: {descricao_receita}")
            
            col_submit, col_cancel = st.columns(2)
            submitted = col_submit.form_submit_button("✔️ Salvar Receita", use_container_width=True, type="primary")
            if col_cancel.form_submit_button("✖️ Cancelar", use_container_width=True):
                st.session_state.show_receita_form = False
                st.rerun()

            if submitted:
                if not descricao_receita or valor_receita == 0:
                    st.warning("Descrição e Valor são obrigatórios.")
                else:
                    new_data = pd.DataFrame([{
                        'DATA': pd.to_datetime(data_receita), 'CATEGORIA': categoria_receita,
                        'DESCRIÇÃO': descricao_receita, 'CONTA': conta_receita, 'VALOR': valor_receita
                    }])
                    if save_transaction(new_data, "Receitas"):
                        st.success("Receita salva com sucesso!")
                        st.session_state.show_receita_form = False
                        st.rerun()

# Modal para Nova Compra no Cartão
if st.session_state.get("show_cc_form", False):
    st.subheader("💳 Lançar Nova Compra no Cartão")
    with st.container():
        with st.form("cc_form", clear_on_submit=True):
            st.subheader("Preencha os dados da compra:")
            df_cc_base = pd.read_excel(xls, sheet_name='Div_CC')
            cartoes = df_cc_base['Cartão'].dropna().unique().tolist()
            tipos_compra = df_cc_base['Tipo de Compra'].dropna().unique().tolist()

            c1, c2 = st.columns(2)
            data_cc = c1.date_input("Data da Compra", datetime.now(), key="data_cc")
            descricao_cc = c2.text_input("Descrição da Compra", key="desc_cc")
            
            c3, c4 = st.columns(2)
            tipo_compra_cc = c3.selectbox("Tipo de Compra", sorted(tipos_compra), key="tipo_compra_cc")
            cartao_cc = c4.selectbox("Cartão Utilizado", sorted(cartoes), key="cartao_cc")
            
            c5, c6, c7 = st.columns(3)
            qtd_parcelas = c5.number_input("Qtd. Parcelas", min_value=1, value=1, step=1, key="qtd_parcelas")
            valor_total_cc = c6.number_input("Valor Total", min_value=0.0, value=0.0, format="%.2f", key="valor_total_cc")
            valor_parcela = valor_total_cc / qtd_parcelas if qtd_parcelas > 0 else 0
            c7.metric("Valor da Parcela", f"{valor_parcela:.2f}")

            def calcular_vencimento(data_compra):
                if data_compra.month == 12: return datetime(data_compra.year + 1, 1, 15)
                return datetime(data_compra.year, data_compra.month + 1, 15)

            col_submit, col_cancel = st.columns(2)
            submitted = col_submit.form_submit_button("✔️ Salvar Compra", use_container_width=True, type="primary")
            if col_cancel.form_submit_button("✖️ Cancelar", use_container_width=True):
                st.session_state.show_cc_form = False
                st.rerun()
            
            if submitted:
                if not descricao_cc or valor_total_cc == 0:
                    st.warning("Descrição e Valor Total são obrigatórios.")
                else:
                    new_data = pd.DataFrame([{
                        'Data': pd.to_datetime(data_cc), 'Descrição': descricao_cc, 'Tipo de Compra': tipo_compra_cc,
                        'Cartão': cartao_cc, 'Quantidade de parcelas': qtd_parcelas, 'Valor das parcelas': valor_parcela,
                        'valor total da compra': valor_total_cc, 'Situação': 'Pendente',
                        'Vencimento da Fatura': calcular_vencimento(data_cc)
                    }])
                    if save_transaction(new_data, "Div_CC"):
                        st.success("Compra salva com sucesso!")
                        st.session_state.show_cc_form = False
                        st.rerun()