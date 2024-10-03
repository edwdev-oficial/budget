import utils
import pandas as pd
import streamlit as st
from datetime import datetime

def show_home(collection):
    
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

