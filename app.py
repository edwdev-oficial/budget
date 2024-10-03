import pandas as pd
import streamlit as st
from home import show_home
from budget import show_budget
from database import collection
from lancamentos import lancamentos
from controle_saldo import show_controle_saldo
from controle_cartoes import show_controle_cartoes

# Configuração da página
st.set_page_config(layout='wide')

# Seleção de estado
estado = st.sidebar.selectbox('Selecione', ['Home', 'Lançamentos', 'Budget', 'Controle Cartões de Crédito', 'Controle Saldo'])
st.sidebar.divider()

# Função para obter dados do MongoDB
def get_data_from_mongo(collection):
    documents = collection.find()
    data = []
    for doc in documents:
        doc['_id'] = str(doc['_id'])
        data.append(doc)
    df = pd.DataFrame(data)
    return df    

collection = collection()
# Obtenção de dados e chamada da função apropriada
df = get_data_from_mongo(collection)

if df is not None:
    if estado == 'Home':
        show_home(collection)
    elif estado == 'Lançamentos':
        lancamentos(df, collection)
    elif estado == 'Budget':
        show_budget(df)
    elif estado == 'Controle Cartões de Crédito':
        show_controle_cartoes(df)
    elif estado == 'Controle Saldo':
        show_controle_saldo(df)