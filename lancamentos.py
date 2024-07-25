import streamlit as st
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

def lancamentos(df, client):
    global g_client, category_customized
    g_client = client
    st.title('Lançamentos')
    st.divider()
    cartao = st.selectbox('Fonte',
        ['', 'Conta Corrente Itaú', 'Flash', 'Visa Platinum','Visa Signature', 'Nubank'],
        key='cartao'
    )
    lancamento = st.date_input('Data', format='DD/MM/YYYY', key='lancamento')
    descricao = st.text_input("Descrição", key="descricao")
    vencimento = st.date_input("Vencimento", format="DD/MM/YYYY", key="vencimento")
    col1, col2 = st.columns(2)
    with col1:
        parcelas = st.number_input("Parcelamento", min_value=1, step=1, key="parcelas")
    with col2:
        valor = st.text_input("Valor", key="valor")

    df_sort = df.sort_values(by='Categoria', ascending=True).reset_index()
    df_unique = pd.DataFrame(df_sort['Categoria'].unique(), columns=['Categoria'])
    df_blank = pd.DataFrame([{'Categoria': ''}])
    df_sort = pd.concat([df_blank, df_unique], ignore_index=True)

    df_outra = pd.DataFrame(([{'Categoria': 'Outra'}]))
    df_sort = pd.concat([df_sort, df_outra])

    categoria = st.selectbox(
        'Categoria',
        df_sort['Categoria'],
        index=None,
        placeholder='Selecionar categoria...',
        key='categoria'
    )

    if categoria == 'Outra':
        category_customized = st.text_input('Especifique a categoria...', key='new_option')
        st.write('Categoria selecionada: ', category_customized)
    else:
        category_customized = categoria
        st.write('Categoria selecionada: ', categoria)

    st.button('Salvar', on_click=salvar)

def salvar():
    
    db = g_client["cont_fin"]
    collection = db['budget']

    parcelas = st.session_state.parcelas
    for parcela in range(parcelas):
        valor = float(st.session_state.valor.replace(',', '.'))
        valor_parcela = valor / parcelas

        data = {}
        data['Data de Lançamento'] = datetime.combine(st.session_state.lancamento, datetime.min.time())
        data['Fonte'] = st.session_state.cartao
        data['Descrição'] = st.session_state.descricao
        vencimento =  st.session_state.vencimento + relativedelta(months=parcela)
        data['Vencimento'] = datetime.combine(vencimento, datetime.min.time())
        data['Valor'] = valor_parcela * -1
        data['Programação'] = datetime.combine(vencimento, datetime.min.time())
        data['Valor Programado'] = valor_parcela * -1
        data['Categoria'] = category_customized

        collection.insert_one(data)

    st.session_state.cartao = ""
    st.session_state['data'] = date.today()
    st.session_state['descricao'] = ""
    st.session_state['vencimento'] = date.today()
    st.session_state['parcelas'] = 1
    st.session_state['valor'] = ""
    st.session_state.categoria = ""
