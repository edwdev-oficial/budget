import pandas as pd
import streamlit as st
from bson import ObjectId
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from database import get_database
from utils import format_currency

db = get_database()
collection_recursos = db['recurso']
collection_budget = db['budget_test']
collection_novos_lancamentos = db['novos_lancamentos']
collection_sdo_anterior = db['sdo_anteior']

def calc_saldo(date_saldo):
    df = pd.DataFrame(list(collection_budget.find()))
    df.sort_values(['Programação', 'Valor Programado'], ascending=[True, False], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['saldo'] = df['Valor Programado'].cumsum()
    saldo = round(df.loc[df['Programação'] == pd.to_datetime(date_saldo)].iloc[-1]['saldo'], 2)
    return saldo

def show_impact(abater_recurso, valor_recurso, valor, date_saldo):
    if abater_recurso and valor_recurso:
        if valor > 0:
            if valor > valor_recurso:
                valor_impacto = valor_recurso - valor
                st.error(f'Impacto negativo {format_currency(valor_impacto)}')
                calc_saldo(date_saldo)
            elif valor < valor_recurso:
                st.info('Sem impacto')
            else:
                st.info('Sem impacto')
        else:
            st.success(f'Impacto positivo: {format_currency(valor * -1)}')
    else:
        if valor > 0:
            st.error(f'Impacto negativo: {format_currency(valor * -1)}')
        else:
            st.success(f'Impacto positivo: {format_currency(valor * -1)}')
        saldo = calc_saldo(date_saldo)
        novo_saldo = saldo - valor
        st.write(f'''
            O saldo em {date_saldo} era {format_currency(saldo)}
            e ficará {format_currency(novo_saldo)}
        ''')

def lancamentos(df, collection):

    date_saldo = st.sidebar.date_input(
        'Saldo em:',
        value=pd.to_datetime('2026-12-31')
    )

    global category_customized, g_df, g_collection, id_recurso
    g_df = df
    g_collection = collection
    id_recurso = None

    st.title('Lançamentos')
    st.divider()

    st.toggle('Abater recurso', True, key='abater_recurso')

    abater_recurso = st.session_state.abater_recurso

    valor_recurso = None

    doc_recursos = list(collection_recursos.find())
    if abater_recurso and doc_recursos:
        valor_recurso = doc_recursos[0]['Valor Programado'] * -1
        if valor_recurso == -0.00:
            valor_recurso = 0.00
        data_recursos = []
        for doc in doc_recursos:
            doc['_id'] = str(doc['_id'])
            data_recursos.append(doc)
        df_recursos = pd.DataFrame(data_recursos)
        st.write(
            f"O lançamento será abatido de: {df_recursos.iloc[0]['Descrição']} "
            f"programado para {df_recursos.iloc[0]['Programação'].strftime('%d/%m/%Y')} "
            F"no valor de R$ {format_currency(valor_recurso)}"
        )
        id_recurso = df_recursos.iloc[0]['id_recurso']

    fonte = st.selectbox('Fonte',
        ['', 'Conta Corrente Itaú', 'Flash', 'Visa Platinum','Visa Signature', 'Nubank', 'Mercado Pago', 'Salário'],
        key='fonte'
    )
    lancamento = st.date_input('Data', format='DD/MM/YYYY', key='lancamento')
    descricao = st.text_input("Descrição", key="descricao")
    vencimento = st.date_input("Vencimento", format="DD/MM/YYYY", key="vencimento")
    col1, col2 = st.columns(2)
    with col1:
        parcelas = st.number_input("Parcelamento", min_value=1, step=1, key="parcelas")
    with col2:
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

    if valor != 0.00 and valor != -0.00:
        show_impact(abater_recurso, valor_recurso, valor, date_saldo)

    if categoria == 'Outra':
        category_customized = st.text_input('Especifique a categoria...', key='new_option')
        st.write('Categoria selecionada: ', category_customized)
    else:
        if categoria:
            category_customized = categoria
            st.write('Categoria selecionada: ', categoria)

    st.write('Clique no botão abaixo para salvar a inclusão no banco de dados')

    st.button('Salvar', on_click=salvar)

    #%% Mostra resultado com os ultimos lançamentos
    saldo_anterior = list(collection_sdo_anterior.find())[0]['saldo_anterior']
    ultimos_lancamentos = list(collection_novos_lancamentos.aggregate([
        {
            "$group": {
                "_id": {},
                # "total_lancamentos": { "$sum": '$Valor Programado' }
                "total_lancamentos": { "$sum": {"$multiply": ["$Valor Programado", "$percent_unbudget"]} }
            }
        },

    ]))
    if ultimos_lancamentos:
        saldo_anterior_calculado = calc_saldo(date_saldo)
        ultimos_lancamentos = ultimos_lancamentos[0]['total_lancamentos']
        if ultimos_lancamentos:
            st.divider()
            st.subheader('Análise dos resultados com os últimos lançamentos acumulados', divider='red')
            st.write(f'Lançamentos acumulados: {format_currency(ultimos_lancamentos)}')    
            st.write(f'''
                O saldo anterior era {format_currency(saldo_anterior)}
                e com os últimos lançamentos ficou {format_currency(saldo_anterior + ultimos_lancamentos)}
            ''')
            if st.button('Reset Ultimos Laçamentos'):
                collection_novos_lancamentos.delete_many({})
                collection_sdo_anterior.update_one({}, {'$set': {'saldo_anterior': saldo_anterior_calculado}})
                st.success('Ultimos lançamentos resetados com sucesso!')

def salvar( ):

    collection = g_collection
    valor = st.session_state.valor
    parcelas = st.session_state.parcelas
    valor_parcela = valor / parcelas

    lancamento_date = st.session_state.lancamento
    month = lancamento_date.month
    year = lancamento_date.year

    abater_recurso = st.session_state.abater_recurso

    if abater_recurso and id_recurso:

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

            if despesas_programadas == 0:
                percent_unbudget = 1

            elif valor * -1 > despesas_programadas:
                collection.update_one({"_id": _id}, {'$set': {'Valor Programado': despesas_programadas - valor * -1}})
                collection_recursos.update_one({}, {'$set': {'Valor Programado': despesas_programadas - valor * -1}})
                
            elif valor * -1 == despesas_programadas:
                collection.update_one({"_id": _id}, {'$set': {'Valor Programado': 0}})
                collection_recursos.update_one({}, {'$set': {'Valor Programado': 0}})

            elif valor * -1 < despesas_programadas:
                collection_recursos.update_one({}, {'$set': {'Valor Programado': 0}})
                collection.update_one({"_id": _id}, {'$set': {'Valor Programado': 0}})
                percent_unbudget = (valor * -1 - despesas_programadas) / valor * -1

        else:
            percent_unbudget = 1

    else:
        percent_unbudget = 1

    createdAt = datetime.now()
    for parcela in range(parcelas):

        data = {}
        if id_recurso:
            data['id_recurso'] = id_recurso
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
        collection_novos_lancamentos.insert_one(data)

    st.session_state.fonte = ""
    st.session_state['data'] = date.today()
    st.session_state['descricao'] = ""
    st.session_state['vencimento'] = date.today()
    st.session_state['parcelas'] = 1
    st.session_state['valor'] = 0.00
    st.session_state.categoria = ""
