from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st

user = st.secrets['mongo_atlas']['user']
password = st.secrets['mongo_atlas']['password']
uri = f'mongodb+srv://{user}:{password}@sandbox.bfpzo.mongodb.net/'
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['cont_fin']
def collection():
    # collection = db['budget']
    collection = db['budget_test']
    return collection

def get_database():
    return db
# if __name__ == '__main__':
#     connect()
