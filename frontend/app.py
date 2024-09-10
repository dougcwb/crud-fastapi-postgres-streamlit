import streamlit as st
import requests
import pandas as pd
from datetime import date

st.set_page_config(
    layout="wide", 
    page_title="Gerenciamento de Produtos - Marketplace"
    )

#st.image("logo.png", width=200)

st.title("Gerenciamento de Produtos")
# Função auxiliar para exibir mensagens de erro detalhadas
def show_response_message(response):
    if response.status_code == 200:
        st.success("Operação realizada com sucesso!")
    else:
        try:
            data = response.json()
            if "detail" in data:
                # Se o erro for uma lista, extraia as mensagens de cada erro
                if isinstance(data["detail"], list):
                    errors = "\n".join([error["msg"] for error in data["detail"]])
                    st.error(f"Erro: {errors}")
                else:
                    # Caso contrário, mostre a mensagem de erro diretamente
                    st.error(f"Erro: {data['detail']}")
        except ValueError:
            st.error("Erro desconhecido. Não foi possível decodificar a resposta.")


add, list, details, delete, update = st.tabs(
    ["Adicionar", "Listar", "Detalhes", "Apagar", "Atualizar"]
    )
# Adicionar Produto
with add:
    with st.form("new_product"):
        name = st.text_input("Nome do Produto")
        description = st.text_area("Descrição do Produto")
        price = st.number_input("Preço", min_value=0.01, format="%f")
        categoria = st.selectbox(
            "Categoria",
            ["Eletrônico", "Eletrodoméstico", "Móveis", "Roupas", "Calçados", "Casa"],
        )
        email_fornecedor = st.text_input("Email do Fornecedor")
        submit_button = st.form_submit_button("Adicionar Produto")

        if submit_button:
            response = requests.post(
                "http://backend:8000/products/",
                json={
                    "name": name,
                    "description": description,
                    "price": price,
                    "categoria": categoria,
                    "email_fornecedor": email_fornecedor,
                },
            )
            show_response_message(response)

# Visualizar Produtos
with list:
    if st.button("Exibir Todos os Produtos"):
        response = requests.get("http://backend:8000/products/")
        if response.status_code == 200:
            product = response.json()
            df = pd.DataFrame(product)

            st.dataframe(
                df,
                column_config={
                    "id": "ID",
                    "name": "Nome",
                    "description": "Descrição",
                    "price": st.column_config.NumberColumn(
                        "Valor",
                        help="Valor do Produto",
                        format="R$%d",
                    ),
                    "categoria": "Categoria",
                    "email_fornecedor": st.column_config.LinkColumn("Email"),
                    "created_at": st.column_config.DateColumn(
                        "Data",
                        min_value=date(1901, 1, 1),
                        max_value=date(2105, 1, 1),
                        format="DD/MM/YYYY",
                        step=1,
                    ),
                },
                hide_index=True,
            )
        else:
            show_response_message(response)

# Obter Detalhes de um Produto
with details:
    get_id = st.number_input("ID do Produto", min_value=1, format="%d")
    if st.button("Buscar Produto"):
        response = requests.get(f"http://backend:8000/products/{get_id}")
        if response.status_code == 200:
            product = response.json()
            df = pd.DataFrame([product])

            df = df[
                [
                    "id",
                    "name",
                    "description",
                    "price",
                    "categoria",
                    "email_fornecedor",
                    "created_at",
                ]
            ]

            # Exibe o DataFrame sem o índice
            st.write(df.to_html(index=False), unsafe_allow_html=True)
        else:
            show_response_message(response)

# Deletar Produto
with delete:
    delete_id = st.number_input("ID do Produto para Deletar", min_value=1, format="%d")
    if st.button("Deletar Produto"):
        response = requests.delete(f"http://backend:8000/products/{delete_id}")
        show_response_message(response)

# Atualizar Produto
with update:
    with st.form("update_product"):
        update_id = st.number_input("ID do Produto", min_value=1, format="%d")
        new_name = st.text_input("Novo Nome do Produto")
        new_description = st.text_area("Nova Descrição do Produto")
        new_price = st.number_input(
            "Novo Preço",
            min_value=0.01,
            format="%f",
        )
        new_categoria = st.selectbox(
            "Nova Categoria",
            ["Eletrônico", "Eletrodoméstico", "Móveis", "Roupas", "Calçados", "Casa"],
        )
        new_email = st.text_input("Novo Email do Fornecedor")

        update_button = st.form_submit_button("Atualizar Produto")

        if update_button:
            update_data = {}
            if new_name:
                update_data["name"] = new_name
            if new_description:
                update_data["description"] = new_description
            if new_price > 0:
                update_data["price"] = new_price
            if new_email:
                update_data["email_fornecedor"] = new_email
            if new_categoria:
                update_data["categoria"] = new_categoria

            if update_data:
                response = requests.put(
                    f"http://backend:8000/products/{update_id}", json=update_data
                )
                show_response_message(response)
            else:
                st.error("Nenhuma informação fornecida para atualização")