import utils
import pandas as pd
import streamlit as st
from datetime import datetime

def show_home(collection, df):

    now_date = datetime.now()
    month = now_date.month
    year = now_date.year
    
    docs = list(collection.aggregate([
        {
            "$match": {
                "$expr": {
                    "$and": [
                        {"$eq": ["$Categoria", "Despesas Mensais"]},
                        {"$eq": [{"$year": "$Vencimento"}, year]},
                        {"$eq": [{"$month": "$Vencimento"}, month]}
                    ]
                }
            }
        }
    ]))


    if docs:
        saldo = docs[0]['Valor Programado'] * -1
        st.title(f'Saldo Despesas Mensais R$ {utils.format_currency(saldo)}')
    else:
        st.title('Sem budget para despesas mensais')

    mes_atual = pd.Timestamp.now().month
    ano_atual = pd.Timestamp.now().year    

    df = df.drop(columns=[
        '_id',
        'Vencimento',
        'Programação',
        'Valor Programado',
        'Categoria'
    ])

    df = df[
        (df['Data de Lançamento'].dt.month == mes_atual) 
        & 
        (df['Data de Lançamento'].dt.year == ano_atual)
        &
        (df['percent_unbudget'] < 1)
    ]

    df['Total Acumulado'] = (df['Valor'] - df['Valor'] * df['percent_unbudget']).cumsum()
    # df['Total Acumulado'] = df['Valor'].cumsum()

    st.dataframe(df)

