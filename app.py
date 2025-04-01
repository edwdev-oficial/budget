import pandas as pd
import analise_cenario
import streamlit as st
import ultimos_lancamentos
from home import show_home
from budget import show_budget
from database import collection
from lancamentos import lancamentos
from fonte_recurso import select_font
from controle_saldo import show_controle_saldo
from controle_cartoes import show_controle_cartoes

# Configuração da página
st.set_page_config(
    page_title='Budget',
    page_icon='💰',
    layout='wide'
)

# Seleção de estado
estado = st.sidebar.selectbox('Selecione', [
    'Home',
    'Análise de Cenário',
    'Lançamentos',
    'Budget',
    'Controle Cartões de Crédito',
    'Controle Saldo',
    'Fonte de Recurso',
    'Ultimos Lançamentos'
])
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
        show_home(df)
    elif estado == 'Análise de Cenário':
        analise_cenario.show_page(df)        
    elif estado == 'Lançamentos':
        lancamentos(df, collection)
    elif estado == 'Budget':
        show_budget(df)
    elif estado == 'Controle Cartões de Crédito':
        show_controle_cartoes(df)
    elif estado == 'Controle Saldo':
        show_controle_saldo(df)
    elif estado == 'Fonte de Recurso':
        select_font()
    elif estado == 'Ultimos Lançamentos':
        ultimos_lancamentos.show_page(df)        