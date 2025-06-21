import streamlit as st
import pandas as pd
from backup_system import BackupSystem, safe_backup
from crud_system import CRUDSystem

def test_crud_system():
    """Testa o sistema CRUD"""
    st.title("🧪 Teste do Sistema CRUD")
    
    # Inicializa sistemas
    crud_system = CRUDSystem('Base_financas.xlsx')
    backup_system = BackupSystem('Base_financas.xlsx')
    
    # Teste de backup
    st.header("📋 Teste de Backup")
    if st.button("Criar Backup de Teste"):
        success, message = safe_backup("teste")
        if success:
            st.success(f"Backup criado: {message}")
        else:
            st.error(f"Erro: {message}")
    
    # Lista backups
    backups = backup_system.list_backups()
    if backups:
        st.write("**Backups disponíveis:**")
        for backup in backups[:3]:
            st.write(f"📁 {backup['filename']} ({backup['date'].strftime('%d/%m/%Y %H:%M')})")
    
    # Teste de carregamento de dados
    st.header("📊 Teste de Carregamento")
    sheet_name = st.selectbox("Selecionar aba para testar:", ['Despesas', 'Receitas', 'Vendas', 'Investimentos', 'Div_CC'])
    
    if st.button("Carregar Dados"):
        df = crud_system.load_sheet_data(sheet_name)
        if not df.empty:
            st.success(f"Dados carregados: {len(df)} registros")
            st.dataframe(df.head(), use_container_width=True)
        else:
            st.warning("Nenhum dado encontrado")
    
    # Teste de edição
    st.header("✏️ Teste de Edição")
    if st.button("Testar Edição"):
        df = crud_system.load_sheet_data('Despesas')
        if not df.empty:
            # Simula edição do primeiro registro
            updated_data = {
                'DESCRIÇÃO': 'TESTE DE EDIÇÃO',
                'VALOR': 100.00
            }
            success, message = crud_system.update_record('Despesas', 0, updated_data)
            if success:
                st.success("Edição testada com sucesso!")
            else:
                st.error(f"Erro na edição: {message}")
        else:
            st.warning("Nenhum dado para testar")

if __name__ == "__main__":
    test_crud_system() 