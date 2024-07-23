from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st
import pandas as pd
from budget import show_budget
from lancamentos import lancamentos
from controle_cartoes import show_controle_cartoes

# Configuração da página
st.set_page_config(layout='wide')

# Função para conectar ao MongoDB
def connect_to_mongo(uri):
    client = MongoClient(uri, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print('Pinged your deployment. You successfully connected to MongoDB!')
    except Exception as e:
        print(e)
    return client

# Função para obter dados do MongoDB
def get_data_from_mongo(client, estado):
    db = client["cont_fin"]
    if estado == 'Lançamentos':
        collection = db['budget']
        documents = collection.find()
        data = []
        for doc in documents:
            doc['_id'] = str(doc['_id'])
            data.append(doc)
        df = pd.DataFrame(data)
        return df
    elif estado == 'Budget':
        collection = db['budget']
        documents = collection.find()
        data = []
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
            data.append(doc)
        df = pd.DataFrame(data)
        return df
    else:
        collection = db['budget']
        documents = collection.find()
        data = []
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
            data.append(doc)
        df = pd.DataFrame(data)
        return df        
        

# Credenciais do MongoDB
user = st.secrets['mongo_atlas']['user']
password = st.secrets['mongo_atlas']['password']
uri = f'mongodb+srv://{user}:{password}@sandbox.bfpzo.mongodb.net/'

# Conexão ao MongoDB
client = connect_to_mongo(uri)

# Seleção de estado
estado = st.sidebar.selectbox('Selecione', ['Lançamentos', 'Budget', 'Controle Cartões de Crédito'])
st.sidebar.divider()

# Obtenção de dados e chamada da função apropriada
df = get_data_from_mongo(client, estado)
if df is not None:
    if estado == 'Budget':
        show_budget(df)
    elif estado == 'Lançamentos':
        lancamentos(df, client)
    else:
        show_controle_cartoes(df)
