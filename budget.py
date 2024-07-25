# import plotly.express as px
# import streamlit as st
# import pandas as pd
# import utils

# def show_budget(df):

#     df = df.sort_values(by=['Programação', 'Valor Programado'], ascending=[True, False])
#     df = df.reset_index(drop=True)
#     df['Saldo'] = df['Valor Programado'].cumsum()    

#     df['Data de Lançamento'] = pd.to_datetime(df['Data de Lançamento'])
    
#     datas_lancamento = df[df['Data de Lançamento'] >= '2024-07-08']
#     datas_lancamento = datas_lancamento.groupby(by=['Data de Lançamento']).size().reset_index(name='Count')
#     datas_lancamento['Data de Lançamento'] = datas_lancamento['Data de Lançamento'].dt.strftime('%d/%m/%Y')

#     select_data = st.sidebar.selectbox('Lançamento', datas_lancamento['Data de Lançamento'])
#     lancamentos_ate = pd.to_datetime(select_data, dayfirst=True)

#     df_budget = df[
#         (df['Data de Lançamento'] <= lancamentos_ate) | (df['Data de Lançamento'] > '2024-11-01')
#     ]
#     df_budget = df_budget[['Programação', 'Valor Programado']]
#     df_budget = df_budget.groupby(by='Programação').sum()
#     df_budget = df_budget.reset_index()
#     df_budget['Saldo'] = df_budget['Valor Programado'].cumsum()

#     df_budget_atualizado = df[['Programação', 'Valor Programado']]
#     df_budget_atualizado = df_budget_atualizado.groupby(by='Programação').sum()
#     df_budget_atualizado = df_budget_atualizado.reset_index()
#     df_budget_atualizado['Saldo'] = df_budget_atualizado['Valor Programado'].cumsum()

#     df_budget_budget_atualizado = pd.merge(df_budget, df_budget_atualizado, on='Programação')
#     df_budget_budget_atualizado = df_budget_budget_atualizado.reset_index(drop=True)
#     df_budget_budget_atualizado = df_budget_budget_atualizado.rename(columns={'Saldo_x': 'Sdo Programado'})
#     df_budget_budget_atualizado = df_budget_budget_atualizado.rename(columns={'Saldo_y': 'Sdo Atualizado'})

#     fig = px.line(
#         df_budget_budget_atualizado,
#         x='Programação',
#         y=['Sdo Programado','Sdo Atualizado'],
#         labels={'value': 'Saldo (R$)', 'variable': 'Legend'}
#     )

#     st.plotly_chart(fig)
#     st.write('Budget x Budget Atualizado')
#     st.dataframe(df_budget_budget_atualizado[['Programação', 'Sdo Programado', 'Sdo Atualizado']])    

#     df_unbudget = df[
#         (df['Data de Lançamento'] > lancamentos_ate) & 
#         (df['Data de Lançamento'] < '2024-11-01')
#     ]
#     df_unbudget = df_unbudget.drop(columns=['_id'])
#     df_unbudget = df_unbudget.sort_values(by=['Data de Lançamento']).reset_index(drop=True)
#     df_unbudget['Saldo'] = df_unbudget['Valor Programado'].cumsum()
#     unbudget = df_unbudget['Valor Programado'].sum()
#     st.write(f'Unbudget após {select_data} R$ {utils.format_currency(unbudget)}')
#     st.dataframe(df_unbudget)

#     st.divider()
#     st.subheader('Database')
#     st.dataframe(df)

"""
Código refatorado
"""

import plotly.express as px
import streamlit as st
import pandas as pd
import utils

def calculate_cumsum(df, group_by_col, value_col):
    df = df.groupby(by=group_by_col).sum().reset_index()
    df['Saldo'] = df[value_col].cumsum()
    return df

def process_date_column(df, date_col, date_format='%d/%m/%Y'):
    df[date_col] = pd.to_datetime(df[date_col])
    df[date_col] = df[date_col].dt.strftime(date_format)
    return df

def get_filtered_df(df, date_col, filter_date, start_date='2024-11-01'):
    return df[(df[date_col] <= filter_date) | (df[date_col] > start_date)]

def show_budget(df):

    st.title('Budget')
    st.divider()


    df = df.sort_values(by=['Programação', 'Valor Programado'], ascending=[True, False]).reset_index(drop=True)
    df['Saldo'] = df['Valor Programado'].cumsum()

    # Process dates and filter data
    df['Data de Lançamento'] = pd.to_datetime(df['Data de Lançamento'])
    datas_lancamento = df[df['Data de Lançamento'] >= '2024-07-08'].groupby(by='Data de Lançamento').size().reset_index(name='Count')
    datas_lancamento = process_date_column(datas_lancamento, 'Data de Lançamento')

    select_data = st.sidebar.selectbox('Budget em', datas_lancamento['Data de Lançamento'])
    lancamentos_ate = pd.to_datetime(select_data, dayfirst=True)

    datas_programacao = df.groupby('Programação').size().reset_index(name='Count')
    datas_programacao = process_date_column(datas_programacao, 'Programação')
    select_datas_programacao = st.sidebar.selectbox('Programação', datas_programacao['Programação'])

    # Budget data
    df_budget = get_filtered_df(df, 'Data de Lançamento', lancamentos_ate)
    df_budget = calculate_cumsum(df_budget[['Programação', 'Valor Programado']], 'Programação', 'Valor Programado')

    # Updated budget data
    df_budget_atualizado = calculate_cumsum(df[['Programação', 'Valor Programado']], 'Programação', 'Valor Programado')

    # Merge data
    df_merged_budget = pd.merge(df_budget, df_budget_atualizado, on='Programação', suffixes=('_Programado', '_Atualizado'))
    df_merged_budget = df_merged_budget.rename(columns={'Saldo_Programado': 'Sdo Programado', 'Saldo_Atualizado': 'Sdo Atualizado'})

    # Plotting
    fig = px.line(
        df_merged_budget,
        x='Programação',
        y=['Sdo Programado', 'Sdo Atualizado'], labels={'value': 'Saldo (R$)', 'variable': 'Legend'},
        title='Bugdet inicial e atual',
        markers=True,
        # text='y'
    )
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig)



    st.write('Budget x Budget Atualizado')
    st.dataframe(df_merged_budget[['Programação', 'Sdo Programado', 'Sdo Atualizado']])

    # Filtro por Programação
    # df_filtered = df[df['Programação'] == select_datas_programacao]
    df_filtered = df[df['Programação'] == pd.to_datetime(select_datas_programacao, format='%d/%m/%Y')]
    df_filtered = df_filtered.sort_values(by=['Data de Lançamento'], ascending=[True])
    df_filtered = df_filtered.groupby(by='Fonte').sum('Valor Programado').drop(columns=['Saldo'])
    st.write(f'Programação para a data {select_datas_programacao}')
    st.dataframe(df_filtered)

    # Unbudget data
    df_unbudget = df[(df['Data de Lançamento'] > lancamentos_ate) & (df['Data de Lançamento'] < '2024-11-01')].drop(columns=['_id'])
    df_unbudget = df_unbudget.sort_values(by='Data de Lançamento').reset_index(drop=True)
    df_unbudget['Saldo'] = df_unbudget['Valor Programado'].cumsum()
    unbudget = df_unbudget['Valor Programado'].sum()

    dias = (pd.Timestamp.now() - pd.to_datetime(select_data, format='%d/%m/%Y')).days - 1
    media_dia_unbudget = unbudget / dias

    st.write(f'Unbudget após {select_data} R$ {utils.format_currency(unbudget)} :worried:')
    global meu_emoj
    if media_dia_unbudget <= 100: 
        meu_emoj = ':-1:' 
    else: 
        meu_emoj = ':clap:'
    st.write(f'Média diária R$ {utils.format_currency(media_dia_unbudget)} {meu_emoj}')
    st.dataframe(df_unbudget)

    st.divider()
    df_database = df.drop(columns=['_id'])
    st.subheader('Database')
    st.dataframe(df_database)

    # df_database.to_excel('database.xlsx', )

    fontes = df['Fonte'].drop_duplicates().sort_values()
    fonte = st.sidebar.selectbox('Fontes', fontes)
    df_fonte = df[df['Fonte'] == fonte]
    df_fonte = df_fonte.drop(columns=['_id'])
    df_fonte = df_fonte.reset_index(drop=True)
    total_programado = df_fonte['Valor Programado'].sum()
    st.subheader('Filtrado por fontes')
    st.write(f'Valor total programado R$ {utils.format_currency(total_programado)}')
    st.dataframe(df_fonte)

    df_fonte_grouped = df_fonte.groupby('Programação').sum('Valor Programado').drop(columns=['Saldo']).reset_index()
    df_fonte_grouped['Valor Programado'] = df_fonte_grouped['Valor Programado'] * -1 
    df_fonte_grouped['Programação'] = df_fonte_grouped['Programação'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_fonte_grouped)
    fig = px.bar(
        df_fonte_grouped,
        x='Programação',
        y='Valor Programado',
        labels={'value': 'Valor Programado (R$)', 'variable': 'Legend'},
        title=f'Fonte {fonte}'
    )
    st.plotly_chart(fig)    

