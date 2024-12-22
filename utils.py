from datetime import datetime
import pandas as pd

def format_currency(valor):
    return f'{valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

def convert_to_serializable(obj):
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    raise TypeError(f'Type {type(obj)} not serializable')

def format_date(date):
    return date.strftime('%d/%m/%Y')

def handle_docs(documents):
    data = []
    for document in documents:
        document['_id'] = str(document['_id'])
        data.append(document)
    return data