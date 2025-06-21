import streamlit as st
import pandas as pd
from datetime import datetime
from crud_system import CRUDSystem, format_dataframe_for_display
from backup_system import safe_backup

def render_crud_forms(crud_system, sheet_name, df_filtrado, contas=None, tipos_recebimento=None):
    """Renderiza formulários CRUD para uma aba específica"""
    
    # Formulário de edição
    if st.session_state.get(f"show_edit_{sheet_name}", False):
        st.markdown(f'### ✏️ Editar {sheet_name}')
        
        if not df_filtrado.empty:
            # Cria opções para seleção
            if sheet_name == 'Vendas':
                opcoes = [f"{row['DATA'].strftime('%d/%m/%Y')} - {row['Cliente']} - R$ {row['VALOR']:,.2f}" 
                         for idx, row in df_filtrado.iterrows()]
            elif sheet_name == 'Investimentos':
                opcoes = [f"{row['DATA'].strftime('%d/%m/%Y')} - {row['ATIVO']} - R$ {row['VALOR_APORTE']:,.2f}" 
                         for idx, row in df_filtrado.iterrows()]
            elif sheet_name == 'Div_CC':
                opcoes = [f"{row['Data'].strftime('%d/%m/%Y')} - {row['Descrição']} - R$ {row['valor total da compra']:,.2f}" 
                         for idx, row in df_filtrado.iterrows()]
            else:  # Despesas e Receitas
                opcoes = [f"{row['DATA'].strftime('%d/%m/%Y')} - {row['DESCRIÇÃO']} - R$ {row['VALOR']:,.2f}" 
                         for idx, row in df_filtrado.iterrows()]
            
            registro_selecionado = st.selectbox(f"Selecionar {sheet_name.lower()} para editar:", opcoes, key=f"edit_{sheet_name}_select")
            
            if registro_selecionado:
                idx_selecionado = opcoes.index(registro_selecionado)
                row_to_edit = df_filtrado.iloc[idx_selecionado]
                
                with st.form(f"edit_{sheet_name}_form"):
                    st.write(f"**Editar dados da {sheet_name.lower()}:**")
                    
                    # Campos específicos por aba
                    if sheet_name == 'Vendas':
                        col1, col2 = st.columns(2)
                        with col1:
                            nova_data = col1.date_input("Data", value=pd.to_datetime(row_to_edit['DATA']).date(), key=f"edit_data_{sheet_name}")
                            novo_cliente = col1.text_input("Cliente", value=row_to_edit['Cliente'], key=f"edit_cliente_{sheet_name}")
                        with col2:
                            nova_descricao = col2.text_input("Descrição", value=row_to_edit['DESCRIÇÃO'], key=f"edit_descricao_{sheet_name}")
                            novo_valor = col2.number_input("Valor", value=float(row_to_edit['VALOR']), format="%.2f", key=f"edit_valor_{sheet_name}")
                        
                        col3, col4, col5 = st.columns(3)
                        with col3:
                            nova_conta = col3.selectbox("Conta", sorted(contas), index=contas.index(row_to_edit['CONTA']) if row_to_edit['CONTA'] in contas else 0, key=f"edit_conta_{sheet_name}")
                        with col4:
                            novo_tipo_receb = col4.selectbox("Tipo de Recebimento", sorted(tipos_recebimento), index=tipos_recebimento.index(row_to_edit['TIPO DE RECEBIMENTO']) if row_to_edit['TIPO DE RECEBIMENTO'] in tipos_recebimento else 0, key=f"edit_tipo_receb_{sheet_name}")
                        with col5:
                            novo_status = col5.selectbox("Status", ["Sim", "Não"], index=0 if row_to_edit['Status'] == "Sim" else 1, key=f"edit_status_{sheet_name}")
                        
                        updated_data = {
                            'DATA': pd.to_datetime(nova_data),
                            'Cliente': novo_cliente,
                            'DESCRIÇÃO': nova_descricao,
                            'CONTA': nova_conta,
                            'TIPO DE RECEBIMENTO': novo_tipo_receb,
                            'VALOR': novo_valor,
                            'Status': novo_status
                        }
                    
                    elif sheet_name == 'Investimentos':
                        col1, col2 = st.columns(2)
                        with col1:
                            nova_data = col1.date_input("Data", value=pd.to_datetime(row_to_edit['DATA']).date(), key=f"edit_data_{sheet_name}")
                            novo_tipo = col1.text_input("Tipo", value=row_to_edit['TIPO'], key=f"edit_tipo_{sheet_name}")
                        with col2:
                            novo_ativo = col2.text_input("Ativo", value=row_to_edit['ATIVO'], key=f"edit_ativo_{sheet_name}")
                            novo_valor = col2.number_input("Valor Aportado", value=float(row_to_edit['VALOR_APORTE']), format="%.2f", key=f"edit_valor_{sheet_name}")
                        
                        col3, col4 = st.columns(2)
                        with col3:
                            nova_quantidade = col3.number_input("Quantidade", value=float(row_to_edit['QUANTIDADE']) if pd.notna(row_to_edit['QUANTIDADE']) else 0.0, format="%.2f", key=f"edit_quantidade_{sheet_name}")
                            novo_preco_medio = col3.number_input("Preço Médio", value=float(row_to_edit['PRECO_MEDIO']) if pd.notna(row_to_edit['PRECO_MEDIO']) else 0.0, format="%.2f", key=f"edit_preco_medio_{sheet_name}")
                        with col4:
                            novo_objetivo = col4.text_input("Objetivo", value=row_to_edit['OBJETIVO'], key=f"edit_objetivo_{sheet_name}")
                        
                        updated_data = {
                            'DATA': pd.to_datetime(nova_data),
                            'TIPO': novo_tipo,
                            'ATIVO': novo_ativo,
                            'VALOR_APORTE': novo_valor,
                            'QUANTIDADE': nova_quantidade,
                            'PRECO_MEDIO': novo_preco_medio,
                            'OBJETIVO': novo_objetivo
                        }
                    
                    elif sheet_name == 'Div_CC':
                        col1, col2 = st.columns(2)
                        with col1:
                            nova_data = col1.date_input("Data", value=pd.to_datetime(row_to_edit['Data']).date(), key=f"edit_data_{sheet_name}")
                            nova_descricao = col1.text_input("Descrição", value=row_to_edit['Descrição'], key=f"edit_descricao_{sheet_name}")
                        with col2:
                            novo_tipo_compra = col2.text_input("Tipo de Compra", value=row_to_edit['Tipo de Compra'], key=f"edit_tipo_compra_{sheet_name}")
                            novo_cartao = col2.text_input("Cartão", value=row_to_edit['Cartão'], key=f"edit_cartao_{sheet_name}")
                        
                        col3, col4 = st.columns(2)
                        with col3:
                            nova_qtd_parcelas = col3.number_input("Qtd. Parcelas", value=int(row_to_edit['Quantidade de parcelas']), key=f"edit_qtd_parcelas_{sheet_name}")
                            novo_valor_total = col3.number_input("Valor Total", value=float(row_to_edit['valor total da compra']), format="%.2f", key=f"edit_valor_total_{sheet_name}")
                        with col4:
                            nova_situacao = col4.selectbox("Situação", ["Pendente", "Pago"], index=0 if row_to_edit['Situação'] == "Pendente" else 1, key=f"edit_situacao_{sheet_name}")
                        
                        updated_data = {
                            'Data': pd.to_datetime(nova_data),
                            'Descrição': nova_descricao,
                            'Tipo de Compra': novo_tipo_compra,
                            'Cartão': novo_cartao,
                            'Quantidade de parcelas': nova_qtd_parcelas,
                            'valor total da compra': novo_valor_total,
                            'Situação': nova_situacao
                        }
                    
                    else:  # Despesas e Receitas
                        col1, col2 = st.columns(2)
                        with col1:
                            nova_data = col1.date_input("Data", value=pd.to_datetime(row_to_edit['DATA']).date(), key=f"edit_data_{sheet_name}")
                            nova_descricao = col1.text_input("Descrição", value=row_to_edit['DESCRIÇÃO'], key=f"edit_descricao_{sheet_name}")
                        with col2:
                            nova_categoria = col2.text_input("Categoria", value=row_to_edit['CATEGORIA'], key=f"edit_categoria_{sheet_name}")
                            novo_valor = col2.number_input("Valor", value=float(row_to_edit['VALOR']), format="%.2f", key=f"edit_valor_{sheet_name}")
                        
                        nova_conta = st.selectbox("Conta", sorted(contas), index=contas.index(row_to_edit['CONTA']) if row_to_edit['CONTA'] in contas else 0, key=f"edit_conta_{sheet_name}")
                        
                        if 'FAVORECIDO' in row_to_edit.index:
                            novo_favorecido = st.text_input("Favorecido", value=row_to_edit['FAVORECIDO'] if pd.notna(row_to_edit['FAVORECIDO']) else "", key=f"edit_favorecido_{sheet_name}")
                        
                        updated_data = {
                            'DATA': pd.to_datetime(nova_data),
                            'DESCRIÇÃO': nova_descricao,
                            'CATEGORIA': nova_categoria,
                            'CONTA': nova_conta,
                            'VALOR': novo_valor
                        }
                        
                        if 'FAVORECIDO' in row_to_edit.index:
                            updated_data['FAVORECIDO'] = novo_favorecido
                    
                    col_submit, col_cancel = st.columns(2)
                    submitted = col_submit.form_submit_button("💾 Salvar Alterações", use_container_width=True, type="primary")
                    if col_cancel.form_submit_button("✖️ Cancelar", use_container_width=True):
                        st.session_state[f"show_edit_{sheet_name}"] = False
                        st.rerun()
                    
                    if submitted:
                        # Encontra o índice original no dataframe completo
                        original_idx = df_filtrado.index[idx_selecionado]
                        success, message = crud_system.update_record(sheet_name, original_idx, updated_data)
                        
                        if success:
                            st.success(f"{sheet_name} atualizada com sucesso!")
                            st.session_state[f"show_edit_{sheet_name}"] = False
                            st.rerun()
                        else:
                            st.error(f"Erro ao atualizar {sheet_name.lower()}: {message}")
        else:
            st.info(f"Nenhuma {sheet_name.lower()} encontrada com os filtros selecionados.")
    
    # Formulário de exclusão
    if st.session_state.get(f"show_delete_{sheet_name}", False):
        st.markdown(f'### 🗑️ Excluir {sheet_name}')
        
        if not df_filtrado.empty:
            # Cria opções para seleção
            if sheet_name == 'Vendas':
                opcoes = [f"{row['DATA'].strftime('%d/%m/%Y')} - {row['Cliente']} - R$ {row['VALOR']:,.2f}" 
                         for idx, row in df_filtrado.iterrows()]
            elif sheet_name == 'Investimentos':
                opcoes = [f"{row['DATA'].strftime('%d/%m/%Y')} - {row['ATIVO']} - R$ {row['VALOR_APORTE']:,.2f}" 
                         for idx, row in df_filtrado.iterrows()]
            elif sheet_name == 'Div_CC':
                opcoes = [f"{row['Data'].strftime('%d/%m/%Y')} - {row['Descrição']} - R$ {row['valor total da compra']:,.2f}" 
                         for idx, row in df_filtrado.iterrows()]
            else:  # Despesas e Receitas
                opcoes = [f"{row['DATA'].strftime('%d/%m/%Y')} - {row['DESCRIÇÃO']} - R$ {row['VALOR']:,.2f}" 
                         for idx, row in df_filtrado.iterrows()]
            
            registro_selecionado = st.selectbox(f"Selecionar {sheet_name.lower()} para excluir:", opcoes, key=f"delete_{sheet_name}_select")
            
            if st.button("🗑️ Confirmar Exclusão", key=f"confirm_delete_{sheet_name}"):
                if registro_selecionado:
                    idx_selecionado = opcoes.index(registro_selecionado)
                    original_idx = df_filtrado.index[idx_selecionado]
                    success, message = crud_system.delete_record(sheet_name, original_idx)
                    
                    if success:
                        st.success(f"{sheet_name} excluída com sucesso!")
                        st.session_state[f"show_delete_{sheet_name}"] = False
                        st.rerun()
                    else:
                        st.error(f"Erro ao excluir {sheet_name.lower()}: {message}")
        else:
            st.info(f"Nenhuma {sheet_name.lower()} encontrada com os filtros selecionados.")

def add_crud_buttons(sheet_name):
    """Adiciona botões CRUD para uma aba"""
    st.markdown('---')
    col_crud1, col_crud2, col_crud3 = st.columns([1, 1, 2])
    
    with col_crud1:
        if st.button(f"✏️ Editar {sheet_name}", key=f"edit_{sheet_name}"):
            st.session_state[f"show_edit_{sheet_name}"] = True
    
    with col_crud2:
        if st.button(f"🗑️ Excluir {sheet_name}", key=f"delete_{sheet_name}"):
            st.session_state[f"show_delete_{sheet_name}"] = True
    
    with col_crud3:
        if st.button(f"🗑️ Exclusão em Lote", key=f"bulk_delete_{sheet_name}"):
            st.session_state[f"show_bulk_delete_{sheet_name}"] = True 