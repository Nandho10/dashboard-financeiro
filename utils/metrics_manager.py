import streamlit as st

def render_metric_card(title, value, delta_text="", icon="💰"):
    """
    Renderiza um card de métrica customizado com HTML e CSS.
    
    Args:
        title (str): O título do card.
        value (str): O valor principal a ser exibido.
        delta_text (str): O texto para a variação (delta).
        icon (str): O emoji do ícone.
    """
    st.markdown(
        f"""
        <style>
            .metric-card {{
                background-color: #1a1a2e;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #2a2a4e;
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            }}
            .metric-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            }}
            .metric-title {{
                font-size: 16px;
                font-weight: 500;
                color: #a0a0b0;
                margin-bottom: 8px;
            }}
            .metric-value {{
                font-size: 32px;
                font-weight: 700;
                color: #ffffff;
            }}
            .metric-delta {{
                font-size: 14px;
                color: #4caf50; /* Verde para positivo por padrão */
            }}
            .metric-delta.negative {{
                color: #f44336; /* Vermelho para negativo */
            }}
        </style>
        
        <div class="metric-card">
            <div class="metric-title">{icon} {title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-delta">{delta_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    ) 