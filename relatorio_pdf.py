import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st

class RelatorioPDF:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configura estilos customizados para o relatório"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=colors.darkblue
        ))
        
        # Título de seção
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            alignment=TA_LEFT,
            textColor=colors.darkblue
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12
        ))
        
        # KPIs
        self.styles.add(ParagraphStyle(
            name='KPIText',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            alignment=TA_CENTER,
            textColor=colors.darkgreen
        ))
    
    def format_currency(self, value):
        """Formata valores monetários"""
        return f"R$ {value:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    
    def create_header(self, title):
        """Cria cabeçalho do relatório"""
        elements = []
        
        # Título principal
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        elements.append(Spacer(1, 20))
        
        # Data e hora de geração
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
        elements.append(Paragraph(f"Relatório gerado em: {data_geracao}", self.styles['NormalText']))
        elements.append(Spacer(1, 30))
        
        return elements
    
    def create_kpi_section(self, kpis_data):
        """Cria seção de KPIs"""
        elements = []
        
        elements.append(Paragraph("Indicadores Principais", self.styles['SectionTitle']))
        elements.append(Spacer(1, 15))
        
        # Criar tabela de KPIs
        kpi_table_data = []
        for kpi in kpis_data:
            kpi_table_data.append([
                Paragraph(kpi['title'], self.styles['NormalText']),
                Paragraph(kpi['value'], self.styles['KPIText'])
            ])
        
        kpi_table = Table(kpi_table_data, colWidths=[3*inch, 2*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(kpi_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def get_plot_as_image_stream(self, fig):
        """Converte um gráfico plotly em um stream de bytes de imagem"""
        try:
            img_bytes = fig.to_image(format="png", width=800, height=600, engine="kaleido")
            return io.BytesIO(img_bytes)
        except Exception as e:
            st.error(f"Erro ao converter gráfico para imagem: {e}")
            return None

    def create_chart_section(self, title, fig, description=""):
        """Cria seção com gráfico a partir de um stream de imagem"""
        elements = []
        
        elements.append(Paragraph(title, self.styles['SectionTitle']))
        if description:
            elements.append(Paragraph(description, self.styles['NormalText']))
        elements.append(Spacer(1, 15))
        
        # Converte gráfico para stream de imagem em memória
        image_stream = self.get_plot_as_image_stream(fig)
        
        if image_stream:
            img = Image(image_stream, width=6*inch, height=4*inch)
            elements.append(img)
        
        elements.append(Spacer(1, 20))
        return elements
    
    def create_table_section(self, title, df, description=""):
        """Cria seção com tabela"""
        elements = []
        
        elements.append(Paragraph(title, self.styles['SectionTitle']))
        if description:
            elements.append(Paragraph(description, self.styles['NormalText']))
        elements.append(Spacer(1, 15))
        
        # Preparar dados da tabela
        table_data = [df.columns.tolist()]  # Cabeçalho
        for _, row in df.head(20).iterrows():  # Limitar a 20 linhas
            table_data.append(row.tolist())
        
        # Criar tabela
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def generate_dashboard_report(self, data, filename="relatorio_dashboard.pdf"):
        """Gera relatório completo do dashboard"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        
        # Cabeçalho
        elements.extend(self.create_header("Relatório Financeiro - Dashboard"))
        
        # KPIs principais
        kpis = [
            {'title': 'Saldo Atual', 'value': self.format_currency(data.get('saldo', 0))},
            {'title': 'Receitas', 'value': self.format_currency(data.get('receitas', 0))},
            {'title': 'Despesas', 'value': self.format_currency(data.get('despesas', 0))},
            {'title': 'Percentual Despesas/Receitas', 'value': f"{data.get('percentual', 0):.1f}%"}
        ]
        elements.extend(self.create_kpi_section(kpis))
        
        # Gráficos (se disponíveis)
        if 'graficos' in data:
            for grafico in data['graficos']:
                if 'fig' in grafico:
                    elements.extend(self.create_chart_section(
                        grafico['titulo'], 
                        grafico['fig'], 
                        grafico.get('descricao', '')
                    ))
        
        # Tabelas (se disponíveis)
        if 'tabelas' in data:
            for tabela in data['tabelas']:
                if 'df' in tabela:
                    elements.extend(self.create_table_section(
                        tabela['titulo'], 
                        tabela['df'], 
                        tabela.get('descricao', '')
                    ))
        
        # Rodapé
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("--- Fim do Relatório ---", self.styles['NormalText']))
        
        # Gerar PDF
        doc.build(elements)
        return filename
    
    def gerar_pdf_compras(self, df_compras, total_gasto, proxima_fatura, media_mensal):
        """Gera um relatório em PDF para a tabela de compras do cartão de crédito."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=inch/2, leftMargin=inch/2, topMargin=inch/2, bottomMargin=inch/2)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        title_style = styles['h1']
        title_style.alignment = TA_CENTER
        header_style = ParagraphStyle(name='Header', fontSize=8, alignment=TA_CENTER)

        # Cabeçalho
        elements.append(Paragraph("Relatório de Compras - Cartão de Crédito", title_style))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", header_style))
        elements.append(Spacer(1, 0.3*inch))

        # Métricas
        kpis_data = [
            ["Total Gasto (Filtrado):", self.format_currency(total_gasto)],
            ["Próxima Fatura (Pendente):", self.format_currency(proxima_fatura)],
            ["Média Mensal (Filtrado):", self.format_currency(media_mensal)]
        ]
        kpi_table = Table(kpis_data, colWidths=[2.5*inch, 1.5*inch])
        kpi_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 0.3*inch))

        # Tabela de Compras
        elements.append(Paragraph("Detalhes das Compras", styles['h2']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Prepara os dados para a tabela - converte tudo para string para evitar erros
        data = [df_compras.columns.values.tolist()] + df_compras.astype(str).values.tolist()
        
        # Ajusta a largura das colunas
        col_widths = [1*inch, 2.5*inch, 1*inch, 1*inch, 1.2*inch, 1.2*inch, 0.8*inch, 0.8*inch]

        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def generate_credit_card_report(self, data, filename="relatorio_cartao_credito.pdf"):
        """Gera relatório específico do cartão de crédito"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        
        # Cabeçalho
        elements.extend(self.create_header("Relatório de Cartão de Crédito"))
        
        # KPIs do cartão
        kpis = [
            {'title': 'Total das Compras', 'value': self.format_currency(data.get('total_compras', 0))},
            {'title': 'Total Pago', 'value': self.format_currency(data.get('total_pago', 0))},
            {'title': 'Total Pendente', 'value': self.format_currency(data.get('total_pendente', 0))},
            {'title': 'Quantidade de Compras', 'value': str(data.get('qtd_compras', 0))},
            {'title': 'Valor Médio', 'value': self.format_currency(data.get('media_compra', 0))},
            {'title': 'Próximas Faturas', 'value': self.format_currency(data.get('proximas_faturas', 0))}
        ]
        elements.extend(self.create_kpi_section(kpis))
        
        # Gráficos
        if 'graficos' in data:
            for grafico in data['graficos']:
                if 'fig' in grafico:
                    elements.extend(self.create_chart_section(
                        grafico['titulo'], 
                        grafico['fig'], 
                        grafico.get('descricao', '')
                    ))
        
        # Tabela de compras
        if 'tabela_compras' in data:
            elements.extend(self.create_table_section(
                "Detalhes das Compras", 
                data['tabela_compras'], 
                "Lista detalhada de todas as compras no cartão de crédito"
            ))
        
        # Rodapé
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("--- Fim do Relatório ---", self.styles['NormalText']))
        
        # Gerar PDF
        doc.build(elements)
        return filename
    
    def generate_budget_report(self, data, filename="relatorio_orcamento.pdf"):
        """Gera relatório específico do orçamento"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        
        # Cabeçalho
        elements.extend(self.create_header("Relatório de Orçamento Mensal"))
        
        # KPIs do orçamento
        kpis = [
            {'title': 'Renda Líquida', 'value': self.format_currency(data.get('renda_liquida', 0))},
            {'title': 'Total Orçado', 'value': self.format_currency(data.get('total_orcado', 0))},
            {'title': 'Total Gasto', 'value': self.format_currency(data.get('total_gasto', 0))},
            {'title': 'Percentual Utilizado', 'value': f"{data.get('percentual_total', 0):.1f}%"}
        ]
        elements.extend(self.create_kpi_section(kpis))
        
        # Gráfico de progresso
        if 'grafico_progresso' in data:
            elements.extend(self.create_chart_section(
                "Progresso Real vs Orçado", 
                data['grafico_progresso'], 
                "Comparação entre gastos reais e limites orçados por categoria"
            ))
        
        # Tabela de configuração
        if 'config_orcamento' in data:
            elements.extend(self.create_table_section(
                "Configuração do Orçamento", 
                data['config_orcamento'], 
                "Porcentagens e valores orçados por categoria"
            ))
        
        # Alertas
        if 'alertas' in data and data['alertas']:
            elements.append(Paragraph("Alertas de Orçamento", self.styles['SectionTitle']))
            elements.append(Spacer(1, 15))
            
            for alerta in data['alertas']:
                elements.append(Paragraph(f"• {alerta}", self.styles['NormalText']))
            
            elements.append(Spacer(1, 20))
        
        # Rodapé
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("--- Fim do Relatório ---", self.styles['NormalText']))
        
        # Gerar PDF
        doc.build(elements)
        return filename

def create_download_button(pdf_path, button_text="📄 Download PDF"):
    """Cria botão de download para o PDF"""
    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
    
    st.download_button(
        label=button_text,
        data=pdf_bytes,
        file_name=os.path.basename(pdf_path),
        mime="application/pdf"
    ) 