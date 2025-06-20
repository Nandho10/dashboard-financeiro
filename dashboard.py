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

st.set_page_config(page_title="DashBoard", layout="wide")

# Ícone de finanças (exemplo: 💰)
st.markdown("## 💰 Análise Descritiva de Finanças Pessoais")

# ... logo após o subheader ...
st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem;}
    div[data-testid="stHorizontalBlock"] > div:first-child {
        padding-left: 0 !important;
        padding-right: 0 !important;
        margin-bottom: 0 !important;
    }
    .css-1b7j0c5 {padding-left: 0 !important; padding-right: 0 !important;}
    .st-emotion-cache-1v0mbdj {margin-top: 0 !important; margin-bottom: 0 !important;}
    .stHorizontalBlock + div {margin-top: 0 !important;}
    </style>
""", unsafe_allow_html=True)

# --- SISTEMA DE NAVEGAÇÃO ---
selected = option_menu(
    menu_title=None,
    options=["Visão Geral", "Transações", "Para onde vai", "Pra quem vai", "Classificação ABC", "Fluxo de Caixa", "Despesas por Categoria", "Vendas"],
    icons=["bar-chart", "table", "graph-up", "people-fill", "list-ol", "graph-up-arrow", "bar-chart-fill", "cart-fill"],
    orientation="horizontal",
    default_index=0,
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa", "margin-left": "0", "margin-right": "0"},
        "icon": {"color": "#185a9d", "font-size": "18px"},
        "nav-link": {"font-size": "16px", "margin": "0 10px", "color": "#185a9d"},
        "nav-link-selected": {"background-color": "#185a9d", "color": "#fff"},
    }
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
    st.header('Filtros')
    st.write('Selecione os filtros desejados abaixo:')
    
    # Botão para redefinir filtros
    if 'reset_filtros' not in st.session_state:
        st.session_state['reset_filtros'] = False
    if st.button('Redefinir Filtros'):
        st.session_state['reset_filtros'] = True
    else:
        st.session_state['reset_filtros'] = False

    # Lê a aba 'Conta' para obter as opções de contas
    df_conta = pd.read_excel(xls, sheet_name='Conta')
    contas = df_conta['Contas'].dropna().unique().tolist()

    # Filtro de tipo de análise com multiselect
    tipos_opcoes = ['Receitas', 'Despesas']
    if st.session_state['reset_filtros']:
        tipos_selecionados = st.multiselect('Tipo de análise', tipos_opcoes, default=tipos_opcoes, key='tipo_filtro_reset')
    else:
        tipos_selecionados = st.multiselect('Tipo de análise', tipos_opcoes, default=tipos_opcoes, key='tipo_filtro')

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
percentual = (abs(valor_despesas) / valor_recebidos * 100) if valor_recebidos > 0 else 0

def format_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

# --- EXIBIÇÃO DOS CARDS ---
# CSS para altura fixa dos cards, centralização do valor e título à esquerda no topo
st.markdown("""
    <style>
    .card-fixo {
        min-height: 140px;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: flex-start;
        text-align: left;
        padding: 18px 20px 20px 20px;
    }
    .card-fixo h4 {
        margin: 0 0 12px 2px;
        font-weight: 500;
        font-size: 1.05rem;
        letter-spacing: 0.5px;
    }
    .card-fixo h2 {
        margin: 0 auto;
        font-size: 2.1rem;
        font-weight: 700;
        align-self: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('---')
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"<div class='card-fixo' style='background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%); border-radius:10px; color:white;'><h4>Saldo</h4><h2>{format_brl(saldo)}</h2></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='card-fixo' style='background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%); border-radius:10px; color:white;'><h4>Recebidos</h4><h2>{format_brl(valor_recebidos)}</h2></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='card-fixo' style='background: linear-gradient(90deg, #fc6076 0%, #ff9a44 100%); border-radius:10px; color:white;'><h4>Despesas</h4><h2>{format_brl(abs(valor_despesas))}</h2></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='card-fixo' style='background: linear-gradient(90deg, #f7971e 0%, #ffd200 100%); border-radius:10px; color:white;'><h4>% Desp/Receb</h4><h2>{percentual:.1f}%</h2></div>", unsafe_allow_html=True)

if selected == "Visão Geral":
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
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig.update_traces(
                textinfo='percent',
                textposition='outside',
                pull=[0.05]*5,
                textfont_size=16,
                textfont_color='black',
                textfont_family='Arial',
                textfont=dict(family='Arial', size=16, color='black')
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
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig_desc.update_traces(
                textinfo='percent',
                textposition='outside',
                pull=[0.05]*5,
                textfont_size=16,
                textfont_color='black',
                textfont_family='Arial',
                textfont=dict(family='Arial', size=16, color='black')
            )
            fig_desc.update_layout(
                legend=dict(orientation='h', yanchor='bottom', y=-0.35, xanchor='center', x=0.5, font=dict(size=11))
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
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig_fav.update_traces(
                textinfo='percent',
                textposition='outside',
                pull=[0.05]*5,
                textfont_size=16,
                textfont_color='black',
                textfont_family='Arial',
                textfont=dict(family='Arial', size=16, color='black')
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
            color_discrete_sequence=['#fc6076']
        )
        fig_evol.update_layout(
            xaxis=dict(dtick=1),
            yaxis_tickformat = ',.2f',
            yaxis_title='Despesas (R$)',
            xaxis_title='Dia do Mês',
            plot_bgcolor='rgba(0,0,0,0)',
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

    # Monta tabela HTML
    st.markdown('### Transações Detalhadas')
    table_html = """
    <style>
    .trans-table {width:100%; border-collapse:collapse;}
    .trans-table th, .trans-table td {border:1px solid #eee; padding:6px 8px; text-align:center; font-size:15px;}
    .trans-table th {background:#185a9d; color:#fff;}
    .recebido {color:green; font-weight:bold;}
    .pagamento {color:red; font-weight:bold;}
    .seta-verde {color:green; font-size:18px; font-weight:bold;}
    .seta-vermelha {color:red; font-size:18px; font-weight:bold;}
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
        table_html += f"""
        <tr>
            <td>{row['Data']}</td>
            <td>{row['Favorecido']}</td>
            <td>{row['Descrição']}</td>
            <td>{row['Categoria']}</td>
            <td class='recebido'>{row['Recebidos']}</td>
            <td class='pagamento'>{row['Pagamentos']}</td>
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
        cores = pareto['Classe'].map({'A': '#fc6076', 'B': '#ffd200', 'C': '#b0b0b0'}).tolist()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=pareto['CATEGORIA'],
            y=pareto['VALOR'],
            marker_color=cores,
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
            line=dict(color='#FFD700', width=3, dash='solid'),
            marker=dict(color='#FFD700', size=8),
            yaxis='y2'
        ))
        fig.add_trace(go.Scatter(
            x=pareto['CATEGORIA'],
            y=[80]*len(pareto),
            mode='lines',
            name='80%',
            line=dict(color='#FFD700', width=2, dash='dash'),
            yaxis='y2',
            showlegend=True
        ))
        fig.update_layout(
            yaxis=dict(title='Despesas (R$)', showgrid=False),
            yaxis2=dict(title='% Acumulado', overlaying='y', side='right', range=[0, 110], showgrid=False),
            xaxis=dict(title='Categoria', automargin=True, tickangle=-45, tickfont=dict(size=12)),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            bargap=0.2,
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, b=120),
            height=500
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
        cores = pareto['Classe'].map({'A': '#fc6076', 'B': '#ffd200', 'C': '#b0b0b0'}).tolist()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=pareto['DESCRIÇÃO'],
            y=pareto['VALOR'],
            marker_color=cores,
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
            line=dict(color='#FFD700', width=3, dash='solid'),
            marker=dict(color='#FFD700', size=8),
            yaxis='y2'
        ))
        fig.add_trace(go.Scatter(
            x=pareto['DESCRIÇÃO'],
            y=[80]*len(pareto),
            mode='lines',
            name='80%',
            line=dict(color='#FFD700', width=2, dash='dash'),
            yaxis='y2',
            showlegend=True
        ))
        fig.update_layout(
            yaxis=dict(title='Despesas (R$)', showgrid=False),
            yaxis2=dict(title='% Acumulado', overlaying='y', side='right', range=[0, 110], showgrid=False),
            xaxis=dict(title='Descrição', automargin=True, tickangle=-45, tickfont=dict(size=12)),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            bargap=0.2,
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, b=120),
            height=500
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
        .abc-table {width:100%; border-collapse:collapse;}
        .abc-table th, .abc-table td {border:1px solid #eee; padding:6px 8px; text-align:center; font-size:15px;}
        .abc-table th {background:#185a9d; color:#fff;}
        .cat-a {color: #fc6076; font-weight: bold;}
        .cat-b {color: #ffd200; font-weight: bold;}
        .seta-verde {color:green; font-size:18px; font-weight:bold;}
        .seta-vermelha {color:red; font-size:18px; font-weight:bold;}
        .seta-cinza {color:#888; font-size:18px; font-weight:bold;}
        .classe-b-icone {color:#ffd200; font-size:18px; font-weight:bold;}
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
            line=dict(color='#4fc3f7', width=3, shape='spline'),
            fill='tozeroy',
            fillcolor='rgba(33, 150, 243, 0.25)',
            marker=dict(size=8, color='red', line=dict(width=2, color='#fff')),
            text=[f"R$ {v:,.0f}".replace(",", ".") for v in df_fluxo['Saldo Acumulado']],
            textposition='top center',
            textfont=dict(color='#fff', size=13),
            hovertemplate='Data: %{x}<br>Saldo: R$ %{y:,.2f}<extra></extra>',
            name='Saldo Acumulado'
        ))
        fig_fluxo.update_layout(
            title='Análise do Saldo Acumulado (YTD)',
            plot_bgcolor='#181c2f',
            paper_bgcolor='#181c2f',
            font=dict(color='#e0e0e0'),
            xaxis=dict(
                title='Data',
                showgrid=True,
                gridcolor='rgba(255,255,255,0.07)',
                zeroline=False,
                showline=False,
                tickfont=dict(color='#b0b0b0'),
                ticks='outside',
                tickangle=-15
            ),
            yaxis=dict(
                title='Saldo Acumulado (R$)',
                showgrid=True,
                gridcolor='rgba(255,255,255,0.07)',
                zeroline=False,
                showline=False,
                tickfont=dict(color='#b0b0b0')
            ),
            margin=dict(l=30, r=30, t=50, b=40),
            height=420,
            showlegend=False,
        )
        st.markdown('<div style="background:#181c2f; border-radius:18px; padding:18px 10px 0 10px;">', unsafe_allow_html=True)
        st.plotly_chart(fig_fluxo, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
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
                    line=dict(color='#FFD700', width=3, dash='dash'),
                ))
            fig.update_layout(
                title=f'Evolução Mensal das Subcategorias em {categoria_selecionada}',
                xaxis_title='Mês/Ano',
                yaxis_title='Valor Gasto (R$)',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#222'),
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
    df_vendas = pd.read_excel(xls, sheet_name='Vendas')
    df_vendas['DATA'] = pd.to_datetime(df_vendas['DATA'], errors='coerce')
    df_vendas = df_vendas.dropna(subset=['DATA'])
    df_vendas['Ano'] = df_vendas['DATA'].dt.year.astype(str)
    df_vendas['Mês'] = df_vendas['DATA'].dt.strftime('%b').str.capitalize().replace({'Feb': 'Fev', 'Apr': 'Abr', 'May': 'Mai', 'Aug': 'Ago', 'Sep': 'Set', 'Oct': 'Out', 'Dec': 'Dez'})

    # Filtros (ano, mês, conta, tipo de recebimento, pago)
    with st.sidebar:
        st.markdown('---')
        st.header('Filtros de Vendas')
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

    # Aplica filtros
    vendas_filtradas = df_vendas[
        (df_vendas['Ano'].isin(anos_vendas_sel) if anos_vendas_sel else True) &
        (df_vendas['Mês'].isin(meses_vendas_sel) if meses_vendas_sel else True) &
        ((df_vendas['CONTA'] == conta_vendas_sel) | (conta_vendas_sel == 'Todas')) &
        ((df_vendas['TIPO DE RECEBIMENTO'] == tipo_receb_sel) | (tipo_receb_sel == 'Todos')) &
        ((df_vendas['PAGO'].astype(str).str.lower() == pago_sel.lower()) | (pago_sel == 'Todos'))
    ]

    # Indicadores
    total_vendido = vendas_filtradas['VALOR'].sum()
    num_vendas = len(vendas_filtradas)
    ticket_medio = total_vendido / num_vendas if num_vendas > 0 else 0
    total_recebido = vendas_filtradas[vendas_filtradas['PAGO'].astype(str).str.lower() == 'sim']['VALOR'].sum()
    total_a_receber = vendas_filtradas[vendas_filtradas['PAGO'].astype(str).str.lower() == 'não']['VALOR'].sum()

    st.markdown('---')
    colv1, colv2, colv3, colv4, colv5 = st.columns(5)
    with colv1:
        st.markdown(f"<div class='card-fixo' style='background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%); border-radius:10px; color:white;'><h4>Total Vendido</h4><h2>{format_brl(total_vendido)}</h2></div>", unsafe_allow_html=True)
    with colv2:
        st.markdown(f"<div class='card-fixo' style='background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%); border-radius:10px; color:white;'><h4>Nº de Vendas</h4><h2>{num_vendas}</h2></div>", unsafe_allow_html=True)
    with colv3:
        st.markdown(f"<div class='card-fixo' style='background: linear-gradient(90deg, #fc6076 0%, #ff9a44 100%); border-radius:10px; color:white;'><h4>Ticket Médio</h4><h2>{format_brl(ticket_medio)}</h2></div>", unsafe_allow_html=True)
    with colv4:
        st.markdown(f"<div class='card-fixo' style='background: linear-gradient(90deg, #f7971e 0%, #ffd200 100%); border-radius:10px; color:white;'><h4>Total Recebido</h4><h2>{format_brl(total_recebido)}</h2></div>", unsafe_allow_html=True)
    with colv5:
        st.markdown(f"<div class='card-fixo' style='background: linear-gradient(90deg, #b06ab3 0%, #4568dc 100%); border-radius:10px; color:white;'><h4>Total a Receber</h4><h2>{format_brl(total_a_receber)}</h2></div>", unsafe_allow_html=True)

    # Gráficos de rosca lado a lado
    st.markdown('---')
    colg1, colg2 = st.columns(2)
    with colg1:
        # Vendas por cliente (top 5)
        if not vendas_filtradas.empty:
            top_clientes = vendas_filtradas.groupby('DESCRIÇÃO')['VALOR'].sum().sort_values(ascending=False).head(5)
            fig_cli = px.pie(names=top_clientes.index, values=top_clientes.values, hole=0.5, title='Top 5 Clientes', color_discrete_sequence=px.colors.sequential.RdBu)
            fig_cli.update_traces(textinfo='percent', textposition='outside', pull=[0.05]*5)
            st.plotly_chart(fig_cli, use_container_width=True)
        else:
            st.info('Não há vendas para exibir por cliente.')
    with colg2:
        # Vendas por tipo de recebimento
        if not vendas_filtradas.empty:
            tipo_receb = vendas_filtradas.groupby('TIPO DE RECEBIMENTO')['VALOR'].sum().sort_values(ascending=False)
            fig_tipo = px.pie(names=tipo_receb.index, values=tipo_receb.values, hole=0.5, title='Por Tipo de Recebimento', color_discrete_sequence=px.colors.sequential.RdBu)
            fig_tipo.update_traces(textinfo='percent', textposition='outside')
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
        fig_evol = px.bar(evol, x='MêsAno', y='VALOR', labels={'MêsAno':'Mês/Ano','VALOR':'Total Vendido'}, color_discrete_sequence=['#43cea2'])
        fig_evol.update_layout(xaxis_tickangle=-35, height=320)
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

# ... rest of the file remains unchanged ... 