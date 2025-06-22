# -*- coding: utf-8 -*-
"""
Módulo de Gerenciamento de Gráficos
Responsável por criar e configurar gráficos no dashboard
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st

class ChartsManager:
    def __init__(self):
        self.colors = px.colors.qualitative.Set3
    
    def create_pie_chart(self, data, values_col, names_col, title, height=400, hole: float = 0.5, color_sequence=None, showlegend=True):
        """Gráfico de rosca/pizza customizado com rótulos externos e cores suaves."""
        if data.empty:
            return go.Figure().add_annotation(text="Sem dados para exibir", x=0.5, y=0.5, showarrow=False)

        # Usa uma paleta de cores 'Pastel' para um visual mais suave, por padrão.
        if color_sequence is None:
            color_sequence = px.colors.qualitative.Pastel
        
        fig = px.pie(
            data,
            values=values_col,
            names=names_col,
            title=title,
            height=height,
            color_discrete_sequence=color_sequence,
            hole=hole
        )
        # Rótulos de porcentagem para fora, com fonte mais leve
        fig.update_traces(
            textposition='outside',
            textinfo='percent',
            textfont_size=16,
            textfont_family='Arial',
            pull=0.03
        )
        # Título centralizado, grande e negrito
        fig.update_layout(
            title=dict(
                text=f"<b>{title}</b>",
                x=0.5,
                xanchor='center',
                font=dict(size=22, family='Arial Black') # Cor se adapta ao tema
            ),
            showlegend=showlegend,
            legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5, font=dict(size=15)),
            uniformtext_minsize=10,
            uniformtext_mode='hide',
            margin=dict(t=60, b=120, l=40, r=40), # Adiciona margem lateral para os rótulos
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    def create_bar_chart(self, data, x_col, y_col, title, orientation="v", height=400):
        """Cria um gráfico de barras"""
        if data.empty:
            return go.Figure().add_annotation(text="Sem dados para exibir", x=0.5, y=0.5, showarrow=False)
        
        if orientation == "h":
            fig = px.bar(
                data, 
                x=y_col, 
                y=x_col,
                title=title,
                height=height,
                orientation='h',
                color_discrete_sequence=self.colors
            )
        else:
            fig = px.bar(
                data, 
                x=x_col, 
                y=y_col,
                title=title,
                height=height,
                color_discrete_sequence=self.colors
            )
        
        fig.update_layout(
            title_x=0.5,
            title_font_size=16,
            xaxis_title="",
            yaxis_title="",
            showlegend=False
        )
        
        return fig
    
    def create_line_chart(self, data, x_col, y_col, title, height=400):
        """Cria um gráfico de linha"""
        if data.empty:
            return go.Figure().add_annotation(text="Sem dados para exibir", x=0.5, y=0.5, showarrow=False)
        
        fig = px.line(
            data, 
            x=x_col, 
            y=y_col,
            title=title,
            height=height,
            color_discrete_sequence=self.colors
        )
        
        fig.update_layout(
            title_x=0.5,
            title_font_size=16,
            xaxis_title="",
            yaxis_title="",
            showlegend=False
        )
        
        return fig
    
    def create_comparison_chart(self, data, x_col, y_cols, title, height=400):
        """Cria um gráfico de comparação (barras agrupadas)"""
        if data.empty:
            return go.Figure().add_annotation(text="Sem dados para exibir", x=0.5, y=0.5, showarrow=False)
        
        fig = go.Figure()
        
        for i, col in enumerate(y_cols):
            fig.add_trace(go.Bar(
                name=col,
                x=data[x_col],
                y=data[col],
                marker_color=self.colors[i % len(self.colors)]
            ))
        
        fig.update_layout(
            title=title,
            title_x=0.5,
            title_font_size=16,
            barmode='group',
            height=height,
            xaxis_title="",
            yaxis_title="",
            showlegend=True
        )
        
        return fig
    
    def create_metric_card(self, value, title, delta=None, delta_color="normal"):
        """Cria um card de métrica"""
        fig = go.Figure()
        
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=value,
            title={"text": title},
            delta={"reference": delta} if delta else None,
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        
        fig.update_layout(
            height=150,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        return fig

    def create_top_products_chart(self, data, x_col, y_col, title, height=400):
        """Cria um gráfico de barras horizontais para Top 5 Produtos/Serviços."""
        if data.empty:
            return go.Figure().add_annotation(text="Sem dados para exibir", x=0.5, y=0.5, showarrow=False)
        
        fig = px.bar(
            data, 
            x=x_col, 
            y=y_col,
            title=f"<b>{title}</b>",
            height=height,
            orientation='h',
            text=x_col, # Adiciona o valor como texto na barra
            color=y_col,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig.update_layout(
            title=dict(x=0.5, xanchor='center', font=dict(size=22, family='Arial Black')),
            xaxis_title="",
            yaxis_title="",
            showlegend=False,
            yaxis={'categoryorder':'total ascending'}, # Garante que o maior valor fique no topo
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=60, b=20, l=10, r=40),
        )
        
        # Formata o texto para ser exibido como moeda
        fig.update_traces(
            texttemplate='R$ %{text:,.2f}', 
            textposition='inside',
            insidetextanchor='middle'
        )

        return fig

# Instância global
charts_manager = ChartsManager() 