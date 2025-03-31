import pandas as pd
import streamlit as st
from database import get_database
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode

db = get_database()
collection_budget = db['budget_test']
collection_recurso = db['recurso']

def select_font():
    st.header('Fontes de Recurso')
    st.divider()

    documents = collection_budget.find()
    data = []
    for doc in documents:
        doc['_id'] = str(doc['_id'])
        data.append(doc)
    df = pd.DataFrame(data)
    # df = df[df['parcela'] == '1 de 1']
    df.drop([
        'percent_unbudget',
        'parcela',
        'createdAt'
    ],axis=1, inplace=True)
    not_include = ['Cartão Carrefour',
        'Visa Platinum',
        'Visa Signature',
        'Nubank',
        'Flash',
        'Credito Imobiliário',
        'Custo Fixo',
        'Salário',
        'Bitcoin',
        'Pgto Contas',
        'TV Assinatura',
        'Produto Itaú',
        'Pagamento de Juros',
        'Mercado Pago',
        'Conta Corrente Mercado Pago'
    ]

    min_date = df['Programação'].min()
    st.write(min_date)
    max_date = df['Programação'].max()
    init_date = pd.to_datetime(
        st.sidebar.date_input(
            'Programados a partir de',
            min_value=min_date,
            max_value=max_date
        )
    )

    df['id_recurso'] = df['id_recurso'].fillna('')

    df = df.loc[
        (~df['Fonte'].isin(not_include))
        &
        (df['Programação'] >= init_date)
        &
        (df['id_recurso'] == "")
    ]
    df.sort_values(['Programação'], inplace=True)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection('single')
    gb.configure_column('_id', hide=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions = grid_options,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode = GridUpdateMode.MODEL_CHANGED,
        theme = 'alpine',
        enable_enterprise_modules = False,
        height = 300,
        width ='100%',
        reload_data = True
    )

    selected_rows = grid_response['selected_rows']
    if selected_rows is not None and len(selected_rows) > 0:
        selected_row = selected_rows.iloc[0]
        collection_recurso.delete_many({})
        df=pd.DataFrame(selected_row)
        df=df.T
        st.dataframe(df)
        if 'id_recurso' in df.columns:
            df.drop(columns=['id_recurso'], inplace=True)
        df.rename(columns={'_id': 'id_recurso'}, inplace=True)
        df['Data de Lançamento'] = pd.to_datetime(df['Data de Lançamento'])
        df['Vencimento'] = pd.to_datetime(df['Vencimento'])
        df['Programação'] = pd.to_datetime(df['Programação'])
        df['Valor'] = df['Valor'].astype(float)
        df['Valor Programado'] = df['Valor Programado'].astype(float)
        st.write(f'Recurso: {df.iloc[0]["Descrição"]}')
        st.write(f'Valor Programado: {df.iloc[0]["Valor Programado"] * -1}')
        st.write(f'Programação: {df.iloc[0]["Programação"]}')
        data=df.to_dict('records')
        collection_recurso.insert_many(data)
    else:
        document_recurso = collection_recurso.find()
        data_recurso = []
        for doc in document_recurso:
            doc['_id'] = str(doc['_id'])
            data_recurso.append(doc)

        if len(data_recurso) > 0:
            df_recurso = pd.DataFrame(data_recurso)
            st.write('Recurso selecionado:')
            st.dataframe(df_recurso)
            if st.button('Apagar recurso'):
                collection_recurso.delete_many({})

