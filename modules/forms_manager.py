# -*- coding: utf-8 -*-
"""
Módulo de Gerenciamento de Formulários
Responsável por criar e gerenciar formulários de CRUD no dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from modules.data_manager import data_manager
from utils.formatters import format_currency, format_date

class FormsManager:
    """Classe para gerenciar formulários de CRUD"""
    
    def __init__(self):
        self.excel_file = "Base_financas.xlsx"
    
    def _get_dynamic_options(self, sheet_name, column_name):
        """Carrega opções dinamicamente de uma aba específica da planilha."""
        try:
            df = data_manager.load_excel_data(sheet_name)
            if df is not None and column_name in df.columns:
                return [""] + sorted(df[column_name].dropna().unique().tolist())
            return [""]
        except Exception:
            return [""]

    def _get_categories_from_headers(self):
        """Carrega as categorias a partir dos cabeçalhos da aba 'Despesas Categoria'."""
        try:
            df = data_manager.load_excel_data("Despesas Categoria")
            return [""] + df.columns.tolist()
        except Exception:
            return [""]

    def _get_descriptions_for_category(self, category):
        """Carrega as descrições para uma categoria específica."""
        if not category:
            return ["--- Selecione uma Categoria ---"]
        try:
            df = data_manager.load_excel_data("Despesas Categoria")
            if category in df.columns:
                return [""] + sorted(df[category].dropna().unique().tolist())
            return [""]
        except Exception:
            return [""]

    def create_expense_form(self):
        """Cria formulário de despesa com categorias e descrições em cascata."""
        st.markdown("### 💸 Nova Despesa")

        # --- Parte 1: Seleção da Categoria (fora do formulário) ---
        categorias = self._get_categories_from_headers()
        selected_categoria = st.selectbox(
            "1. Selecione a Categoria",
            options=categorias,
            key="categoria_selector" # Chave única para este widget
        )

        # O formulário só aparece depois que uma categoria é selecionada
        if selected_categoria:
            with st.form("expense_details_form", clear_on_submit=True):
                
                # --- Parte 2: Restante do Formulário ---
                st.info(f"Categoria selecionada: **{selected_categoria}**")

                # Carrega opções dependentes
                descricoes = self._get_descriptions_for_category(selected_categoria)
                descricoes.append("--- Digitar Nova Descrição ---")
                favorecidos = self._get_dynamic_options("Despesas", "FAVORECIDO")
                contas = self._get_dynamic_options("Conta", "Contas")
                formas_pagamento = self._get_dynamic_options("Forma de Pagamento", "Forma de Pagamento")

                col1, col2 = st.columns(2)
                with col1:
                    data = st.date_input("Data", value=date.today())
                    
                    selected_descricao = st.selectbox("2. Descrição", options=descricoes)
                    nova_descricao_input = ""
                    if selected_descricao == "--- Digitar Nova Descrição ---":
                        nova_descricao_input = st.text_input("Nova Descrição:", placeholder="Digite a nova descrição")

                    favorecido = st.selectbox("Favorecido", options=favorecidos)

                with col2:
                    conta = st.selectbox("Conta", options=contas)
                    forma_pagamento = st.selectbox("Forma de Pagamento", options=formas_pagamento)
                    valor = st.number_input("Valor (R$)", min_value=0.01, step=50.0, format="%.2f")
                    pago = st.checkbox("Pago?", value=True)

                submitted = st.form_submit_button("💾 Salvar Despesa", type="primary", use_container_width=True)
                
                if submitted:
                    final_descricao = nova_descricao_input if selected_descricao == "--- Digitar Nova Descrição ---" else selected_descricao
                    
                    nova_despesa_dados = {
                        "DATA": data, "CATEGORIA": selected_categoria, "DESCRIÇÃO": final_descricao,
                        "FAVORECIDO": favorecido, "CONTA": conta, "FORMA DE PAGAMENTO": forma_pagamento,
                        "VALOR": -abs(valor), "PAGO": 1 if pago else 0
                    }
                    if self._save_expense(nova_despesa_dados):
                        st.success("✅ Despesa salva com sucesso!")
                        data_manager.clear_cache()
                        st.rerun()
                    else:
                        st.error("❌ Erro ao salvar. Verifique se Categoria e Descrição foram preenchidas.")
    
    def create_revenue_form(self):
        """Cria formulário para adicionar receita"""
        with st.form("revenue_form", clear_on_submit=True):
            st.markdown("### 💰 Nova Receita")
            
            data = st.date_input("Data", value=date.today())
            descricao = st.text_input("Descrição", placeholder="Ex: Salário")
            categoria = st.selectbox("Categoria", options=["Salário", "Freelance", "Investimentos", "Outros"])
            valor = st.number_input("Valor (R$)", min_value=0.01, value=0.01, step=0.01)
            
            submitted = st.form_submit_button("💾 Salvar Receita", type="primary")
            
            if submitted:
                if self._save_revenue(data, descricao, categoria, valor):
                    st.success("✅ Receita salva com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao salvar receita!")
    
    def create_sale_form(self):
        """Cria formulário para adicionar/editar venda"""
        with st.form("sale_form", clear_on_submit=True):
            st.markdown("### 🛒 Nova Venda")
            
            # Campos do formulário
            data = st.date_input("Data", value=date.today())
            cliente = st.text_input("Cliente", placeholder="Nome do cliente")
            produto = st.text_input("Produto/Serviço", placeholder="Descrição do produto")
            
            valor = st.number_input("Valor (R$)", min_value=0.01, value=0.01, step=0.01)
            forma_pagamento = st.selectbox("Forma de Pagamento", 
                                         options=["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro", "Transferência"])
            
            observacoes = st.text_area("Observações", placeholder="Observações adicionais...")
            
            submitted = st.form_submit_button("💾 Salvar Venda", type="primary")
            
            if submitted:
                if self._validate_sale_form(data, cliente, produto, valor):
                    success = self._save_sale(data, cliente, produto, valor, forma_pagamento, observacoes)
                    if success:
                        st.success("✅ Venda salva com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao salvar venda!")
                else:
                    st.error("❌ Por favor, preencha todos os campos obrigatórios!")
    
    def create_investment_form(self):
        """Cria formulário para adicionar/editar investimento"""
        with st.form("investment_form", clear_on_submit=True):
            st.markdown("### 💰 Novo Investimento")
            
            # Campos do formulário
            data = st.date_input("Data", value=date.today())
            ativo = st.text_input("Ativo", placeholder="Ex: PETR4, CDB, Tesouro Direto")
            
            valor_aporte = st.number_input("Valor do Aporte (R$)", min_value=0.01, value=0.01, step=0.01)
            tipo_investimento = st.selectbox("Tipo de Investimento", 
                                           options=["Ações", "Fundos", "Renda Fixa", "Criptomoedas", "Outros"])
            
            observacoes = st.text_area("Observações", placeholder="Observações adicionais...")
            
            submitted = st.form_submit_button("💾 Salvar Investimento", type="primary")
            
            if submitted:
                if self._validate_investment_form(data, ativo, valor_aporte):
                    success = self._save_investment(data, ativo, valor_aporte, tipo_investimento, observacoes)
                    if success:
                        st.success("✅ Investimento salvo com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao salvar investimento!")
                else:
                    st.error("❌ Por favor, preencha todos os campos obrigatórios!")
    
    def create_credit_card_form(self):
        """Cria formulário para adicionar/editar despesa no cartão de crédito"""
        with st.form("credit_card_form", clear_on_submit=True):
            st.markdown("### 💳 Nova Despesa no Cartão")
            
            # Campos do formulário
            data = st.date_input("Data", value=date.today())
            descricao = st.text_input("Descrição", placeholder="Ex: Compras online")
            
            # Categorias disponíveis
            categorias = self._get_categories("Despesas")
            categoria = st.selectbox("Categoria", options=categorias)
            
            valor = st.number_input("Valor (R$)", min_value=0.01, value=0.01, step=0.01)
            cartao = st.text_input("Cartão", placeholder="Ex: Nubank, Itaú, etc.")
            
            parcelas = st.number_input("Número de Parcelas", min_value=1, value=1, step=1)
            observacoes = st.text_area("Observações", placeholder="Observações adicionais...")
            
            submitted = st.form_submit_button("💾 Salvar Despesa no Cartão", type="primary")
            
            if submitted:
                if self._validate_credit_card_form(data, descricao, categoria, valor, cartao):
                    success = self._save_credit_card(data, descricao, categoria, valor, cartao, parcelas, observacoes)
                    if success:
                        st.success("✅ Despesa no cartão salva com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao salvar despesa no cartão!")
                else:
                    st.error("❌ Por favor, preencha todos os campos obrigatórios!")
    
    def _get_categories(self, sheet_name):
        """Obtém categorias disponíveis de uma aba"""
        try:
            df = data_manager.load_excel_data(sheet_name)
            if not df.empty and "CATEGORIA" in df.columns:
                categorias = df["CATEGORIA"].dropna().unique().tolist()
                return sorted(categorias) if categorias else ["Outros"]
            return ["Outros"]
        except:
            return ["Outros"]
    
    def _validate_expense_form(self, data, descricao, categoria, valor):
        """Valida formulário de despesa"""
        return data and descricao.strip() and categoria and valor > 0
    
    def _validate_revenue_form(self, data, descricao, categoria, valor):
        """Valida formulário de receita"""
        return data and descricao.strip() and categoria and valor > 0
    
    def _validate_sale_form(self, data, cliente, produto, valor):
        """Valida formulário de venda"""
        return data and cliente.strip() and produto.strip() and valor > 0
    
    def _validate_investment_form(self, data, ativo, valor_aporte):
        """Valida formulário de investimento"""
        return data and ativo.strip() and valor_aporte > 0
    
    def _validate_credit_card_form(self, data, descricao, categoria, valor, cartao):
        """Valida formulário de cartão de crédito"""
        return data and descricao.strip() and categoria and valor > 0 and cartao.strip()
    
    def _save_expense(self, data_dict):
        """Salva nova despesa a partir de um dicionário."""
        try:
            # Validação simples
            if not all([data_dict["DESCRIÇÃO"], data_dict["CATEGORIA"], data_dict["VALOR"] != 0]):
                return False
                
            df = data_manager.load_excel_data("Despesas")
            
            # Garante que todas as colunas do dicionário existam no DataFrame
            for col in data_dict.keys():
                if col not in df.columns:
                    # Adiciona a coluna com um valor padrão se não existir
                    df[col] = pd.NA 

            new_row = pd.DataFrame([data_dict])
            df = pd.concat([df, new_row], ignore_index=True)
            
            return data_manager.save_data(df, "Despesas")
            
        except Exception as e:
            st.error(f"Erro técnico ao salvar despesa: {e}")
            return False
    
    def _save_revenue(self, data, descricao, categoria, valor):
        """Salva nova receita"""
        try:
            df = data_manager.load_excel_data("Receitas")
            
            nova_receita = {
                "DATA": data,
                "DESCRICAO": descricao,
                "CATEGORIA": categoria,
                "VALOR": abs(valor)
            }
            
            df = pd.concat([df, pd.DataFrame([nova_receita])], ignore_index=True)
            return data_manager.save_data(df, "Receitas")
            
        except Exception as e:
            st.error(f"Erro ao salvar receita: {e}")
            return False
    
    def _save_sale(self, data, cliente, produto, valor, forma_pagamento, observacoes):
        """Salva nova venda"""
        try:
            df = data_manager.load_excel_data("Vendas")
            
            nova_venda = {
                "DATA": data,
                "Cliente": cliente,
                "Produto": produto,
                "VALOR": valor,
                "FORMA_PAGAMENTO": forma_pagamento,
                "OBSERVACOES": observacoes
            }
            
            df = pd.concat([df, pd.DataFrame([nova_venda])], ignore_index=True)
            return data_manager.save_data(df, "Vendas")
            
        except Exception as e:
            st.error(f"Erro ao salvar venda: {e}")
            return False
    
    def _save_investment(self, data, ativo, valor_aporte, tipo_investimento, observacoes):
        """Salva novo investimento"""
        try:
            df = data_manager.load_excel_data("Investimentos")
            
            novo_investimento = {
                "DATA": data,
                "ATIVO": ativo,
                "VALOR_APORTE": valor_aporte,
                "TIPO_INVESTIMENTO": tipo_investimento,
                "OBSERVACOES": observacoes
            }
            
            df = pd.concat([df, pd.DataFrame([novo_investimento])], ignore_index=True)
            return data_manager.save_data(df, "Investimentos")
            
        except Exception as e:
            st.error(f"Erro ao salvar investimento: {e}")
            return False
    
    def _save_credit_card(self, data, descricao, categoria, valor, cartao, parcelas, observacoes):
        """Salva nova despesa no cartão de crédito"""
        try:
            df = data_manager.load_excel_data("Div_CC")
            
            nova_despesa_cc = {
                "DATA": data,
                "DESCRICAO": descricao,
                "CATEGORIA": categoria,
                "VALOR": -abs(valor),  # Despesas são negativas
                "CARTAO": cartao,
                "PARCELAS": parcelas,
                "OBSERVACOES": observacoes
            }
            
            df = pd.concat([df, pd.DataFrame([nova_despesa_cc])], ignore_index=True)
            return data_manager.save_data(df, "Div_CC")
            
        except Exception as e:
            st.error(f"Erro ao salvar despesa no cartão: {e}")
            return False

    def render_edit_expense_form(self, df_despesas, crud_system):
        """Renderiza o formulário completo de edição de despesas."""
        st.markdown("### ✏️ Editar Despesa")

        if df_despesas.empty:
            st.warning("Não há despesas para editar.")
            return

        # Criar uma representação legível para cada despesa no selectbox
        df_despesas['display'] = df_despesas.apply(
            lambda row: f"{row['DATA'].strftime('%d/%m/%y')} - {row['DESCRIÇÃO']} - R$ {-row['VALOR']:.2f}",
            axis=1
        )
        options = ["Selecione uma despesa para editar"] + df_despesas['display'].tolist()
        
        selected_display = st.selectbox("Selecione a Despesa", options=options, index=0)

        if selected_display != "Selecione uma despesa para editar":
            # Encontrar o índice da linha selecionada
            selected_index = df_despesas[df_despesas['display'] == selected_display].index[0]
            record_to_edit = df_despesas.loc[selected_index]

            with st.form("edit_expense_form"):
                st.info(f"Editando: {selected_display}")

                categorias = self._get_categories_from_headers()
                contas = self._get_dynamic_options("Conta", "Contas")
                formas_pagamento = self._get_dynamic_options("Forma de Pagamento", "Forma de Pagamento")
                
                # Encontra o índice da opção atual para pré-selecionar
                cat_index = categorias.index(record_to_edit['CATEGORIA']) if record_to_edit['CATEGORIA'] in categorias else 0
                descricoes = self._get_descriptions_for_category(record_to_edit['CATEGORIA'])
                desc_index = descricoes.index(record_to_edit['DESCRIÇÃO']) if record_to_edit['DESCRIÇÃO'] in descricoes else 0
                conta_index = contas.index(record_to_edit['CONTA']) if record_to_edit['CONTA'] in contas else 0
                fp_index = formas_pagamento.index(record_to_edit['FORMA DE PAGAMENTO']) if record_to_edit['FORMA DE PAGAMENTO'] in formas_pagamento else 0

                col1, col2 = st.columns(2)
                with col1:
                    data = st.date_input("Data", value=record_to_edit['DATA'])
                    categoria = st.selectbox("Categoria", options=categorias, index=cat_index)
                    descricao = st.selectbox("Descrição", options=descricoes, index=desc_index)
                    favorecido = st.text_input("Favorecido", value=record_to_edit['FAVORECIDO'])
                
                with col2:
                    conta = st.selectbox("Conta", options=contas, index=conta_index)
                    forma_pagamento = st.selectbox("Forma de Pagamento", options=formas_pagamento, index=fp_index)
                    valor = st.number_input("Valor (R$)", value=float(-record_to_edit['VALOR']), format="%.2f")
                    pago = st.checkbox("Pago?", value=(record_to_edit['PAGO'] == 1))

                submitted = st.form_submit_button("💾 Salvar Alterações")

                if submitted:
                    updated_data = {
                        "DATA": pd.to_datetime(data), "CATEGORIA": categoria, "DESCRIÇÃO": descricao,
                        "FAVORECIDO": favorecido, "CONTA": conta, "FORMA DE PAGAMENTO": forma_pagamento,
                        "VALOR": -abs(valor), "PAGO": 1 if pago else 0
                    }
                    success, message = crud_system.update_record("Despesas", selected_index, updated_data)
                    if success:
                        st.success("✅ Despesa atualizada com sucesso!")
                        st.session_state['show_edit_Despesas'] = False
                        data_manager.clear_cache()
                        st.rerun()
                    else:
                        st.error(f"❌ Erro ao atualizar: {message}")
        
        if st.button("❌ Cancelar Edição"):
            st.session_state['show_edit_Despesas'] = False
            st.rerun()

    def render_delete_expense_form(self, df_despesas, crud_system):
        """Renderiza o formulário para deletar uma despesa."""
        st.markdown("### 🗑️ Excluir Despesa")

        if df_despesas.empty:
            st.warning("Não há despesas para excluir.")
            return

        df_despesas['display'] = df_despesas.apply(
            lambda row: f"{row['DATA'].strftime('%d/%m/%y')} - {row['DESCRIÇÃO']} - R$ {-row['VALOR']:.2f}",
            axis=1
        )
        options = ["Selecione uma despesa para excluir"] + df_despesas['display'].tolist()
        
        selected_display = st.selectbox("Selecione a Despesa para Excluir", options=options, index=0)

        if selected_display != "Selecione uma despesa para excluir":
            selected_index = df_despesas[df_despesas['display'] == selected_display].index[0]
            
            st.warning(f"**Atenção!** Você tem certeza que deseja excluir permanentemente a despesa **'{selected_display}'**?")
            
            if st.button("🗑️ Sim, Excluir Permanentemente", type="primary"):
                success, message = crud_system.delete_record("Despesas", selected_index)
                if success:
                    st.success("✅ Despesa excluída com sucesso!")
                    st.session_state['show_delete_Despesas'] = False
                    data_manager.clear_cache()
                    st.rerun()
                else:
                    st.error(f"❌ Erro ao excluir: {message}")

        if st.button("❌ Cancelar Exclusão"):
            st.session_state['show_delete_Despesas'] = False
            st.rerun()

    def render_bulk_delete_expense_form(self, df_despesas, crud_system):
        """Renderiza o formulário para deletar múltiplas despesas."""
        st.markdown("### 🗑️ Exclusão em Lote")

        if df_despesas.empty:
            st.warning("Não há despesas para excluir.")
            return

        with st.form("bulk_delete_form"):
            df_display = df_despesas.copy()
            df_display["DATA"] = pd.to_datetime(df_display["DATA"]).dt.strftime('%d/%m/%Y')
            df_display["VALOR"] = df_display["VALOR"].apply(lambda x: f"R$ {-x:,.2f}")
            
            # Usando st.data_editor para adicionar checkboxes
            df_display['Selecionar'] = False
            edited_df = st.data_editor(
                df_display[['Selecionar', 'DATA', 'CATEGORIA', 'DESCRIÇÃO', 'VALOR']],
                hide_index=True,
                use_container_width=True,
                disabled=['DATA', 'CATEGORIA', 'DESCRIÇÃO', 'VALOR'] # Trava as colunas de dados
            )

            submitted = st.form_submit_button("🗑️ Excluir Itens Selecionados")

            if submitted:
                indices_to_delete = edited_df[edited_df['Selecionar']].index.tolist()
                
                if not indices_to_delete:
                    st.warning("Nenhuma despesa foi selecionada.")
                    return

                success, message = crud_system.delete_multiple_records("Despesas", indices_to_delete)

                if success:
                    st.success(f"✅ {len(indices_to_delete)} despesa(s) excluída(s) com sucesso!")
                    st.session_state['show_bulk_delete_Despesas'] = False
                    data_manager.clear_cache()
                    st.rerun()
                else:
                    st.error(f"❌ Erro ao excluir em lote: {message}")
        
        if st.button("❌ Cancelar Exclusão em Lote"):
            st.session_state['show_bulk_delete_Despesas'] = False
            st.rerun()

# Instância global
forms_manager = FormsManager() 