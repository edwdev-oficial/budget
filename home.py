import utils
import pandas as pd
import streamlit as st
from datetime import datetime
from database import get_database
from bson import ObjectId

def show_home(df):

    db = get_database()
    collection_recurso = db['recurso']
    doc_recurso = list(collection_recurso.find())

    if doc_recurso:
        saldo = doc_recurso[0]['Valor Programado'] * -1
        st.title(f'Saldo {doc_recurso[0]["Descrição"]}')
        st.title(f'R$ {utils.format_currency(saldo)}')

        st.divider()
        
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
            ]

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