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
import uuid

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

    def _get_dynamic_descriptions(self, categoria):
        """Carrega descrições da aba 'Despesas Categoria' para a categoria selecionada."""
        try:
            df = pd.read_excel(self.excel_file, sheet_name="Despesas Categoria")
            if categoria in df.columns:
                return [d for d in df[categoria].dropna().unique() if str(d).strip() != ""]
            return []
        except Exception:
            return []

    def create_expense_form(self):
        """Cria formulário de despesa com categorias e descrições em cascata."""
        st.write("Entrou no formulário de despesa")  # Debug 1
        st.markdown("### 💸 Nova Despesa")

        categorias = self._get_dynamic_options("Despesas", "CATEGORIA")
        selected_categoria = st.selectbox("Categoria", options=categorias, key="categoria_selectbox")
        st.write("Categoria selecionada:", selected_categoria)  # Debug 2
        
        # Carregar descrições dinâmicas da aba 'Despesas Categoria' conforme a categoria
        descricoes_teste = []
        if selected_categoria and selected_categoria.strip():
            try:
                df_cat = pd.read_excel(self.excel_file, sheet_name="Despesas Categoria")
                if selected_categoria in df_cat.columns:
                    descricoes_teste = [d for d in df_cat[selected_categoria].dropna().unique() if str(d).strip() != ""]
            except Exception as e:
                st.warning(f"Erro ao carregar descrições da planilha: {e}")
        if not descricoes_teste:
            descricoes_teste = ["Nenhuma descrição disponível para esta categoria"]
        # Adiciona opção para digitar nova descrição
        descricoes_teste.append("--- Digitar Nova Descrição ---")

        # Selectbox de descrição fora do formulário
        descricao = st.selectbox("Descrição", options=descricoes_teste, key="descricao_selectbox")
        nova_descricao = None
        if descricao == "--- Digitar Nova Descrição ---":
            st.markdown("### ✏️ Nova Descrição")
            nova_descricao = st.text_input("Digite a nova descrição:", key="nova_descricao_text", placeholder="Ex: Supermercado Extra")

        with st.form(key=f"form_despesa_{selected_categoria}"):
            col1, col2 = st.columns(2)
            with col1:
                data = st.date_input("Data", value=date.today(), key=f"data_{selected_categoria}")
                favorecidos = self._get_dynamic_options("Despesas", "FAVORECIDO")
                favorecidos.append("--- Digitar Novo Favorecido ---")
                favorecido = st.selectbox("Favorecido", options=favorecidos, key=f"favorecido_{selected_categoria}")
                novo_favorecido_input = None
                if favorecido == "--- Digitar Novo Favorecido ---":
                    novo_favorecido_input = st.text_input("Digite o novo favorecido", key=f"novo_favorecido_{selected_categoria}")
                conta = st.selectbox("Conta", options=self._get_dynamic_options("Conta", "Contas"), key=f"conta_{selected_categoria}")
            with col2:
                forma_pagamento = st.selectbox("Forma de Pagamento", options=self._get_dynamic_options("Forma de Pagamento", "Forma de Pagamento"), key=f"forma_pagamento_{selected_categoria}")
                valor = st.number_input("Valor", min_value=0.01, value=0.01, step=0.01, key=f"valor_{selected_categoria}")
                pago = st.checkbox("Pago", value=True, key=f"pago_{selected_categoria}")
            submitted = st.form_submit_button("Salvar")

            if submitted:
                descricao_final = nova_descricao if descricao == "--- Digitar Nova Descrição ---" else descricao
                final_favorecido = novo_favorecido_input if favorecido == "--- Digitar Novo Favorecido ---" and novo_favorecido_input else favorecido
                if not selected_categoria or selected_categoria == "":
                    st.error("❌ Categoria é obrigatória!")
                elif not descricao_final or descricao_final.strip() == "" or descricao_final == "Nenhuma descrição disponível para esta categoria":
                    st.error("❌ Descrição é obrigatória!")
                elif valor <= 0:
                    st.error("❌ Valor deve ser maior que zero!")
                elif favorecido == "--- Digitar Novo Favorecido ---" and (not novo_favorecido_input or novo_favorecido_input.strip() == ""):
                    st.error("❌ Digite o nome do novo favorecido!")
                else:
                    nova_despesa_dados = {
                        "DATA": data, "CATEGORIA": selected_categoria, "DESCRIÇÃO": descricao_final,
                        "FAVORECIDO": final_favorecido, "CONTA": conta, "FORMA DE PAGAMENTO": forma_pagamento,
                        "VALOR": -abs(valor), "PAGO": 1 if pago else 0
                    }
                    st.success(f"Descrição salva: {descricao_final}")
    
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
            selected_index = df_despesas[df_despesas['display'] == selected_display].index[0]
            record_to_edit = df_despesas.loc[selected_index]

            # Destaque visual na tabela (ajustado para tema escuro)
            st.markdown(f"""
            <div style='background-color:#cce5ff;padding:12px 18px;border-radius:8px;margin-bottom:10px;border:1px solid #339af0;'>
                <b style='color:#003366;'>Em edição:</b> <span style='color:#003366;'>{selected_display}</span>
            </div>
            """, unsafe_allow_html=True)

            with st.form("edit_expense_form"):
                st.info(f"Editando: {selected_display}")

                categorias = self._get_dynamic_options("Despesas", "CATEGORIA")
                contas = self._get_dynamic_options("Conta", "Contas")
                formas_pagamento = self._get_dynamic_options("Forma de Pagamento", "Forma de Pagamento")

                cat_index = categorias.index(record_to_edit['CATEGORIA']) if record_to_edit['CATEGORIA'] in categorias else 0
                descricoes = self._get_dynamic_descriptions(record_to_edit['CATEGORIA'])
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
                    if not categoria or not descricao or valor <= 0:
                        st.error("Preencha todos os campos obrigatórios corretamente!")
                    else:
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

    def render_edit_sale_form(self, df_vendas, crud_system):
        st.markdown("### ✏️ Editar Venda")
        if df_vendas.empty:
            st.info("Nenhuma venda disponível para editar.")
            return
        
        df_vendas = df_vendas.reset_index(drop=True)
        idx = st.selectbox("Selecione a venda para editar:", df_vendas.index, format_func=lambda i: f"{df_vendas.at[i, 'DATA']} - {df_vendas.at[i, 'Cliente']} - {format_currency(df_vendas.at[i, 'VALOR'])}")
        venda = df_vendas.loc[idx]
        
        with st.form("edit_sale_form", clear_on_submit=True):
            data = st.date_input("Data", value=pd.to_datetime(venda["DATA"]))
            cliente = st.text_input("Cliente", value=venda.get("Cliente", ""))
            produto = st.text_input("Produto/Serviço", value=venda.get("Produto", ""))
            valor = st.number_input("Valor (R$)", min_value=0.01, value=float(venda["VALOR"]), step=0.01)
            forma_pagamento = st.text_input("Forma de Pagamento", value=venda.get("Forma_Pagamento", ""))
            observacoes = st.text_area("Observações", value=venda.get("Observações", ""))
            submitted = st.form_submit_button("Salvar Alterações", type="primary")
            if submitted:
                novos_dados = {
                    "DATA": data,
                    "Cliente": cliente,
                    "Produto": produto,
                    "VALOR": valor,
                    "Forma_Pagamento": forma_pagamento,
                    "Observações": observacoes
                }
                sucesso = crud_system.update_record("Vendas", idx, novos_dados)
                if sucesso:
                    st.success("Venda atualizada com sucesso!")
                    data_manager.clear_cache()
                    st.rerun()
                else:
                    st.error("Erro ao atualizar venda.")

    def render_delete_sale_form(self, df_vendas, crud_system):
        st.markdown("### 🗑️ Excluir Venda")
        if df_vendas.empty:
            st.info("Nenhuma venda disponível para excluir.")
            return
        
        df_vendas = df_vendas.reset_index(drop=True)
        idx = st.selectbox("Selecione a venda para excluir:", df_vendas.index, format_func=lambda i: f"{df_vendas.at[i, 'DATA']} - {df_vendas.at[i, 'Cliente']} - {format_currency(df_vendas.at[i, 'VALOR'])}")
        venda = df_vendas.loc[idx]
        st.write(f"**Cliente:** {venda.get('Cliente', '')}")
        st.write(f"**Produto:** {venda.get('Produto', '')}")
        st.write(f"**Valor:** {format_currency(venda.get('VALOR', 0))}")
        if st.button("Confirmar Exclusão", type="primary"):
            sucesso = crud_system.delete_record("Vendas", idx)
            if sucesso:
                st.success("Venda excluída com sucesso!")
                data_manager.clear_cache()
                st.rerun()
            else:
                st.error("Erro ao excluir venda.")

    def render_bulk_delete_sale_form(self, df_vendas, crud_system):
        st.markdown("### 🗑️ Exclusão em Lote de Vendas")
        if df_vendas.empty:
            st.info("Nenhuma venda disponível para exclusão em lote.")
            return
        
        df_vendas = df_vendas.reset_index(drop=True)
        indices = st.multiselect("Selecione as vendas para excluir:", df_vendas.index, format_func=lambda i: f"{df_vendas.at[i, 'DATA']} - {df_vendas.at[i, 'Cliente']} - {format_currency(df_vendas.at[i, 'VALOR'])}")
        if st.button("Excluir Selecionadas", type="primary") and indices:
            sucesso = True
            for idx in sorted(indices, reverse=True):
                if not crud_system.delete_record("Vendas", idx):
                    sucesso = False
            if sucesso:
                st.success("Vendas excluídas com sucesso!")
                data_manager.clear_cache()
                st.rerun()
            else:
                st.error("Erro ao excluir uma ou mais vendas.")

    def render_edit_revenue_form(self, df_receitas, crud_system):
        st.markdown("### ✏️ Editar Receita")
        if df_receitas.empty:
            st.info("Nenhuma receita disponível para editar.")
            return
        
        df_receitas = df_receitas.reset_index(drop=True)
        idx = st.selectbox("Selecione a receita para editar:", df_receitas.index, format_func=lambda i: f"{df_receitas.at[i, 'DATA']} - {df_receitas.at[i, 'DESCRIÇÃO']} - {format_currency(df_receitas.at[i, 'VALOR'])}")
        receita = df_receitas.loc[idx]
        
        with st.form("edit_revenue_form", clear_on_submit=True):
            data = st.date_input("Data", value=pd.to_datetime(receita["DATA"]))
            descricao = st.text_input("Descrição", value=receita.get("DESCRIÇÃO", ""))
            categoria = st.selectbox("Categoria", options=["Salário", "Freelance", "Investimentos", "Outros"], index=0)
            valor = st.number_input("Valor (R$)", min_value=0.01, value=float(receita["VALOR"]), step=0.01)
            submitted = st.form_submit_button("Salvar Alterações", type="primary")
            if submitted:
                novos_dados = {
                    "DATA": data,
                    "DESCRIÇÃO": descricao,
                    "CATEGORIA": categoria,
                    "VALOR": valor
                }
                sucesso = crud_system.update_record("Receitas", idx, novos_dados)
                if sucesso:
                    st.success("Receita atualizada com sucesso!")
                    data_manager.clear_cache()
                    st.rerun()
                else:
                    st.error("Erro ao atualizar receita.")

    def render_delete_revenue_form(self, df_receitas, crud_system):
        st.markdown("### 🗑️ Excluir Receita")
        if df_receitas.empty:
            st.info("Nenhuma receita disponível para excluir.")
            return
        
        df_receitas = df_receitas.reset_index(drop=True)
        idx = st.selectbox("Selecione a receita para excluir:", df_receitas.index, format_func=lambda i: f"{df_receitas.at[i, 'DATA']} - {df_receitas.at[i, 'DESCRIÇÃO']} - {format_currency(df_receitas.at[i, 'VALOR'])}")
        receita = df_receitas.loc[idx]
        st.write(f"**Descrição:** {receita.get('DESCRIÇÃO', '')}")
        st.write(f"**Categoria:** {receita.get('CATEGORIA', '')}")
        st.write(f"**Valor:** {format_currency(receita.get('VALOR', 0))}")
        if st.button("Confirmar Exclusão", type="primary"):
            sucesso = crud_system.delete_record("Receitas", idx)
            if sucesso:
                st.success("Receita excluída com sucesso!")
                data_manager.clear_cache()
                st.rerun()
            else:
                st.error("Erro ao excluir receita.")

    def render_bulk_delete_revenue_form(self, df_receitas, crud_system):
        st.markdown("### 🗑️ Exclusão em Lote de Receitas")
        if df_receitas.empty:
            st.info("Nenhuma receita disponível para exclusão em lote.")
            return
        
        df_receitas = df_receitas.reset_index(drop=True)
        indices = st.multiselect("Selecione as receitas para excluir:", df_receitas.index, format_func=lambda i: f"{df_receitas.at[i, 'DATA']} - {df_receitas.at[i, 'DESCRIÇÃO']} - {format_currency(df_receitas.at[i, 'VALOR'])}")
        if st.button("Excluir Selecionadas", type="primary") and indices:
            sucesso = True
            for idx in sorted(indices, reverse=True):
                if not crud_system.delete_record("Receitas", idx):
                    sucesso = False
            if sucesso:
                st.success("Receitas excluídas com sucesso!")
                data_manager.clear_cache()
                st.rerun()
            else:
                st.error("Erro ao excluir uma ou mais receitas.")

    def render_edit_credit_card_form(self, df_cc, crud_system):
        st.markdown("### ✏️ Editar Despesa no Cartão")
        if df_cc.empty:
            st.info("Nenhuma despesa no cartão disponível para editar.")
            return
        
        df_cc = df_cc.reset_index(drop=True)
        idx = st.selectbox("Selecione a despesa para editar:", df_cc.index, format_func=lambda i: f"{df_cc.at[i, 'DATA']} - {df_cc.at[i, 'DESCRIÇÃO']} - {format_currency(df_cc.at[i, 'VALOR'])}")
        cc_item = df_cc.loc[idx]
        
        with st.form("edit_credit_card_form", clear_on_submit=True):
            data = st.date_input("Data", value=pd.to_datetime(cc_item["DATA"]))
            descricao = st.text_input("Descrição", value=cc_item.get("DESCRIÇÃO", ""))
            categoria = st.text_input("Categoria", value=cc_item.get("CATEGORIA", ""))
            valor = st.number_input("Valor (R$)", min_value=0.01, value=float(cc_item["VALOR"]), step=0.01)
            cartao = st.text_input("Cartão", value=cc_item.get("CARTAO", ""))
            submitted = st.form_submit_button("Salvar Alterações", type="primary")
            if submitted:
                novos_dados = {
                    "DATA": data,
                    "DESCRIÇÃO": descricao,
                    "CATEGORIA": categoria,
                    "VALOR": valor,
                    "CARTAO": cartao
                }
                sucesso = crud_system.update_record("Div_CC", idx, novos_dados)
                if sucesso:
                    st.success("Despesa no cartão atualizada com sucesso!")
                    data_manager.clear_cache()
                    st.rerun()
                else:
                    st.error("Erro ao atualizar despesa no cartão.")

    def render_delete_credit_card_form(self, df_cc, crud_system):
        st.markdown("### 🗑️ Excluir Despesa no Cartão")
        if df_cc.empty:
            st.info("Nenhuma despesa no cartão disponível para excluir.")
            return
        
        df_cc = df_cc.reset_index(drop=True)
        idx = st.selectbox("Selecione a despesa para excluir:", df_cc.index, format_func=lambda i: f"{df_cc.at[i, 'DATA']} - {df_cc.at[i, 'DESCRIÇÃO']} - {format_currency(df_cc.at[i, 'VALOR'])}")
        cc_item = df_cc.loc[idx]
        st.write(f"**Descrição:** {cc_item.get('DESCRIÇÃO', '')}")
        st.write(f"**Categoria:** {cc_item.get('CATEGORIA', '')}")
        st.write(f"**Cartão:** {cc_item.get('CARTAO', '')}")
        st.write(f"**Valor:** {format_currency(cc_item.get('VALOR', 0))}")
        if st.button("Confirmar Exclusão", type="primary"):
            sucesso = crud_system.delete_record("Div_CC", idx)
            if sucesso:
                st.success("Despesa no cartão excluída com sucesso!")
                data_manager.clear_cache()
                st.rerun()
            else:
                st.error("Erro ao excluir despesa no cartão.")

    def render_bulk_delete_credit_card_form(self, df_cc, crud_system):
        st.markdown("### 🗑️ Exclusão em Lote de Despesas no Cartão")
        if df_cc.empty:
            st.info("Nenhuma despesa no cartão disponível para exclusão em lote.")
            return
        
        df_cc = df_cc.reset_index(drop=True)
        indices = st.multiselect("Selecione as despesas para excluir:", df_cc.index, format_func=lambda i: f"{df_cc.at[i, 'DATA']} - {df_cc.at[i, 'DESCRIÇÃO']} - {format_currency(df_cc.at[i, 'VALOR'])}")
        if st.button("Excluir Selecionadas", type="primary") and indices:
            sucesso = True
            for idx in sorted(indices, reverse=True):
                if not crud_system.delete_record("Div_CC", idx):
                    sucesso = False
            if sucesso:
                st.success("Despesas no cartão excluídas com sucesso!")
                data_manager.clear_cache()
                st.rerun()
            else:
                st.error("Erro ao excluir uma ou mais despesas no cartão.")

    def render_edit_investment_form(self, df_investimentos, crud_system):
        st.markdown("### ✏️ Editar Investimento")
        if df_investimentos.empty:
            st.info("Nenhum investimento disponível para editar.")
            return
        
        df_investimentos = df_investimentos.reset_index(drop=True)
        idx = st.selectbox("Selecione o investimento para editar:", df_investimentos.index, format_func=lambda i: f"{df_investimentos.at[i, 'DATA']} - {df_investimentos.at[i, 'ATIVO']} - {format_currency(df_investimentos.at[i, 'VALOR_APORTE'])}")
        investimento = df_investimentos.loc[idx]
        
        with st.form("edit_investment_form", clear_on_submit=True):
            data = st.date_input("Data", value=pd.to_datetime(investimento["DATA"]))
            ativo = st.text_input("Ativo", value=investimento.get("ATIVO", ""))
            valor_aporte = st.number_input("Valor do Aporte (R$)", min_value=0.01, value=float(investimento["VALOR_APORTE"]), step=0.01)
            tipo_investimento = st.selectbox("Tipo de Investimento", options=["Ações", "Fundos", "Renda Fixa", "Criptomoedas", "Outros"], index=0)
            observacoes = st.text_area("Observações", value=investimento.get("OBSERVACOES", ""))
            submitted = st.form_submit_button("Salvar Alterações", type="primary")
            if submitted:
                novos_dados = {
                    "DATA": data,
                    "ATIVO": ativo,
                    "VALOR_APORTE": valor_aporte,
                    "TIPO_INVESTIMENTO": tipo_investimento,
                    "OBSERVACOES": observacoes
                }
                sucesso = crud_system.update_record("Investimentos", idx, novos_dados)
                if sucesso:
                    st.success("Investimento atualizado com sucesso!")
                    data_manager.clear_cache()
                    st.rerun()
                else:
                    st.error("Erro ao atualizar investimento.")

    def render_delete_investment_form(self, df_investimentos, crud_system):
        st.markdown("### 🗑️ Excluir Investimento")
        if df_investimentos.empty:
            st.info("Nenhum investimento disponível para excluir.")
            return
        
        df_investimentos = df_investimentos.reset_index(drop=True)
        idx = st.selectbox("Selecione o investimento para excluir:", df_investimentos.index, format_func=lambda i: f"{df_investimentos.at[i, 'DATA']} - {df_investimentos.at[i, 'ATIVO']} - {format_currency(df_investimentos.at[i, 'VALOR_APORTE'])}")
        investimento = df_investimentos.loc[idx]
        st.write(f"**Ativo:** {investimento.get('ATIVO', '')}")
        st.write(f"**Tipo:** {investimento.get('TIPO_INVESTIMENTO', '')}")
        st.write(f"**Valor:** {format_currency(investimento.get('VALOR_APORTE', 0))}")
        if st.button("Confirmar Exclusão", type="primary"):
            sucesso = crud_system.delete_record("Investimentos", idx)
            if sucesso:
                st.success("Investimento excluído com sucesso!")
                data_manager.clear_cache()
                st.rerun()
            else:
                st.error("Erro ao excluir investimento.")

    def render_bulk_delete_investment_form(self, df_investimentos, crud_system):
        st.markdown("### 🗑️ Exclusão em Lote de Investimentos")
        if df_investimentos.empty:
            st.info("Nenhum investimento disponível para exclusão em lote.")
            return
        
        df_investimentos = df_investimentos.reset_index(drop=True)
        indices = st.multiselect("Selecione os investimentos para excluir:", df_investimentos.index, format_func=lambda i: f"{df_investimentos.at[i, 'DATA']} - {df_investimentos.at[i, 'ATIVO']} - {format_currency(df_investimentos.at[i, 'VALOR_APORTE'])}")
        if st.button("Excluir Selecionados", type="primary") and indices:
            sucesso = True
            for idx in sorted(indices, reverse=True):
                if not crud_system.delete_record("Investimentos", idx):
                    sucesso = False
            if sucesso:
                st.success("Investimentos excluídos com sucesso!")
                data_manager.clear_cache()
                st.rerun()
            else:
                st.error("Erro ao excluir um ou mais investimentos.")

    def consultar_despesas(self, storage):
        st.header("Consulta de Despesas")
        if storage.empty:
            st.info("Nenhuma despesa cadastrada.")
            return

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

        st.dataframe(df_filtrado.reset_index(drop=True))
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button("Exportar para CSV", csv, "despesas_filtradas.csv", "text/csv")

# Instância global
forms_manager = FormsManager() 

# Inicialização do método de armazenamento (exemplo: DataFrame vazio)
def init_storage():
    """Inicializa o armazenamento das despesas (ex: DataFrame, planilha, banco de dados)."""
    # Exemplo: DataFrame vazio com colunas padrão
    columns = ["Data", "Categoria", "Descrição", "Favorecido", "Valor", "Forma de Pagamento", "Conta", "Pago?"]
    return pd.DataFrame(columns=columns)

def consultar_despesas(storage):
    st.header("Consulta de Despesas")
    if storage.empty:
        st.info("Nenhuma despesa cadastrada.")
        return

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

    st.dataframe(df_filtrado.reset_index(drop=True))
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button("Exportar para CSV", csv, "despesas_filtradas.csv", "text/csv")


def incluir_despesa(storage, dados):
    """Inclui uma nova despesa no armazenamento."""
    pass


def editar_despesa(storage, id_despesa, novos_dados):
    """Edita uma despesa existente no armazenamento."""
    pass


def excluir_despesa(storage, id_despesa):
    """Exclui uma despesa do armazenamento."""
    pass 