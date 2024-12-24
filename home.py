import utils
import pandas as pd
import streamlit as st
from datetime import datetime
from database import get_database
from bson import ObjectId


def show_home(collection, df):

    db = get_database()
    collection_recurso = db['recurso']
    doc_recurso = list(collection_recurso.find())

    # now_date = datetime.now()
    # month = now_date.month
    # year = now_date.year

    if doc_recurso:
        saldo = doc_recurso[0]['Valor Programado'] * -1
        st.title(f'Saldo {doc_recurso[0]['Descrição']}')
        st.title(f'R$ {utils.format_currency(saldo)}')

        st.divider()
        
        # st.write(doc_recurso[0])

        # st.write(doc_recurso[0]['id_recurso'])
        

        df = df.drop(columns=[
            '_id',
            'Vencimento',
            'Programação',
            'Valor Programado',
            'Categoria'
        ])

        if 'id_recurso' in df.columns:
            df = df[
                (df['id_recurso'] == doc_recurso[0]['id_recurso']) 
                # &
                # (df['percent_unbudget'] < 1)
            ]

            # df['Total Acumulado'] = (df['Valor'] - df['Valor'] * df['percent_unbudget']).cumsum()
            df['Total Acumulado'] = df['Valor'].cumsum()

            if len(df): 
                st.dataframe(df)
                df_unbudget = df[df['percent_unbudget'] > 0]
                if len(df_unbudget):
                    df_unbudget['valor_unbudget'] = df_unbudget['Valor'] * df['percent_unbudget'] 
                    total_unbudget = df_unbudget['valor_unbudget'].sum() * -1
                    # st.write(f'Sua verba está estourada em: R$ {utils.format_currency(total_unbudget)}')
                    st.write(f'<h1 style="color:red">Sua verba está estourada em: R$ {utils.format_currency(total_unbudget)}</h1>', unsafe_allow_html=True)



    else:
        st.title('Nenhum recurso selecionado para os lançamentos')        

    # docs = list(collection.aggregate([
    #     {
    #         "$match": {
    #             "$expr": {
    #                 "$and": [
    #                     {"$eq": ["$Categoria", "Despesas Mensais"]},
    #                     {"$eq": [{"$year": "$Vencimento"}, year]},
    #                     {"$eq": [{"$month": "$Vencimento"}, month]}
    #                 ]
    #             }
    #         }
    #     }
    # ]))


    # if docs:
    #     saldo = docs[0]['Valor Programado'] * -1
    #     st.title(f'Saldo Despesas Mensais R$ {utils.format_currency(saldo)}')
    # else:
    #     st.title('Sem budget para despesas mensais')

    # mes_atual = pd.Timestamp.now().month
    # ano_atual = pd.Timestamp.now().year    

    # df = df.drop(columns=[
    #     '_id',
    #     'Vencimento',
    #     'Programação',
    #     'Valor Programado',
    #     'Categoria'
    # ])

    # df = df[
    #     (df['Data de Lançamento'].dt.month == mes_atual) 
    #     & 
    #     (df['Data de Lançamento'].dt.year == ano_atual)
    #     &
    #     (df['percent_unbudget'] < 1)
    # ]

    # df['Total Acumulado'] = (df['Valor'] - df['Valor'] * df['percent_unbudget']).cumsum()
    # # df['Total Acumulado'] = df['Valor'].cumsum()

    # st.dataframe(df)

