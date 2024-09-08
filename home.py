import utils
import pandas as pd
import streamlit as st
from datetime import datetime

# st.set_page_config(layout='centered')

def show_home(collection):
    
    now_date = datetime.now()
    month = now_date.month
    year = now_date.year
    
    docs = collection.aggregate([
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
    ])

    # datas = []
    # for doc in docs:
    #     doc['_id'] = str(doc['_id'])
    #     datas.append(doc)

    saldo = list(docs)[0]['Valor Programado'] * -1
    
    # df = pd.DataFrame(datas)
    # st.dataframe(df)
    st.title(f'Saldo Despesas Mensais R$ {utils.format_currency(saldo)}')

