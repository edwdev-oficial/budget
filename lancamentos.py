import pandas as pd
import streamlit as st
from bson import ObjectId
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from database import get_database
from utils import format_currency

db = get_database()
collection_recursos = db['recurso']


def lancamentos(df, collection):

    global category_customized, g_df, g_collection, id_recurso
    g_df = df
    g_collection = collection
    id_recurso = None

    st.title('Lançamentos')
    st.divider()

    st.toggle('Abater recurso', True, key='abater_recurso')

    abater_recurso = st.session_state.abater_recurso

    doc_recursos = list(collection_recursos.find())
    if abater_recurso and doc_recursos:
        data_recursos = []
        for doc in doc_recursos:
            doc['_id'] = str(doc['_id'])
            data_recursos.append(doc)
        df_recursos = pd.DataFrame(data_recursos)
        # st.dataframe(df_recursos)
        # st.write(df_recursos.dtypes)
        st.write(
            f"O lançamento será abatido de: {df_recursos.iloc[0]['Descrição']} "
            f"programado para {df_recursos.iloc[0]['Programação'].strftime('%d/%m/%Y')} "
            F"no valor de R$ {format_currency(df_recursos.iloc[0]['Valor Programado'] * -1)}"
        )
        id_recurso = df_recursos.iloc[0]['id_recurso']

    fonte = st.selectbox('Fonte',
        ['', 'Conta Corrente Itaú', 'Flash', 'Visa Platinum','Visa Signature', 'Nubank'],
        key='fonte'
    )
    lancamento = st.date_input('Data', format='DD/MM/YYYY', key='lancamento')
    descricao = st.text_input("Descrição", key="descricao")
    vencimento = st.date_input("Vencimento", format="DD/MM/YYYY", key="vencimento")
    col1, col2 = st.columns(2)
    with col1:
        parcelas = st.number_input("Parcelamento", min_value=1, step=1, key="parcelas")
    with col2:
        # valor = st.text_input("Valor", key="valor")
        valor = st.number_input("Valor", step=0.01, key="valor")

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

def salvar( ):

    collection = g_collection
    # valor = float(st.session_state.valor.replace(',', '.'))
    valor = st.session_state.valor
    parcelas = st.session_state.parcelas
    valor_parcela = valor / parcelas

    lancamento_date = st.session_state.lancamento
    month = lancamento_date.month
    year = lancamento_date.year

    abater_recurso = st.session_state.abater_recurso

    if abater_recurso and id_recurso:

        # doc = collection.aggregate([
        #     {
        #         "$match": {
        #             "$expr": {
        #                 "$and" : [
        #                     {"$eq": ["$Categoria", "Despesas Mensais"]},
        #                     {"$eq": [{"$month": "$Vencimento"}, month]},
        #                     {"$eq": [{"$year": "$Vencimento"}, year]}
        #                 ]
        #             }
        #         }
        #     }
        # ])

        doc = collection.aggregate([
            {
                "$match": { "_id": ObjectId(id_recurso) }
            }
        ])

        doc_list = list(doc)

        if doc_list:
            despesas_programadas = doc_list[0]["Valor Programado"]
            _id = ObjectId(doc_list[0]['_id'])

            percent_unbudget = 0

            if valor * -1 > despesas_programadas:
                collection.update_one({"_id": _id}, {'$set': {'Valor Programado': despesas_programadas - valor * -1}})
                collection_recursos.update_one({}, {'$set': {'Valor Programado': despesas_programadas - valor * -1}})

            elif valor * -1 == despesas_programadas:
                collection.delete_one({"_id": _id})
                collection_recursos.delete_many({})

            elif valor * -1 < despesas_programadas:
                percent_unbudget = (valor * -1 - despesas_programadas) / valor * -1
                collection.delete_one({"_id": _id})
                collection_recursos.delete_many({})
        else:
            percent_unbudget = 1
    else:
        percent_unbudget = 1

    createdAt = datetime.now()
    for parcela in range(parcelas):

        data = {}
        data['Data de Lançamento'] = datetime.combine(st.session_state.lancamento, datetime.min.time())
        data['Fonte'] = st.session_state.fonte
        data['Descrição'] = st.session_state.descricao
        vencimento =  st.session_state.vencimento + relativedelta(months=parcela)
        data['Vencimento'] = datetime.combine(vencimento, datetime.min.time())
        data['Valor'] = valor_parcela * -1
        data['Programação'] = datetime.combine(vencimento, datetime.min.time())
        data['Valor Programado'] = valor_parcela * -1
        data['Categoria'] = category_customized
        data['percent_unbudget'] = percent_unbudget
        data['parcela'] = f'{parcela + 1} de {parcelas}'
        data['createdAt'] = createdAt

        collection.insert_one(data)

    st.session_state.fonte = ""
    st.session_state['data'] = date.today()
    st.session_state['descricao'] = ""
    st.session_state['vencimento'] = date.today()
    st.session_state['parcelas'] = 1
    st.session_state['valor'] = 0.00
    st.session_state.categoria = ""
    