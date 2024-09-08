from datetime import datetime
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

    # data = datetime(2024, 7, 10)
    # st.write(data)
    # st.write(df['Programação'].dtype)

    # df = df[df['Programação'] <= '2025-01-23']

    df = df.sort_values(by=['Programação', 'Valor Programado'], ascending=[True, False]).reset_index(drop=True)
    df['Saldo'] = df['Valor Programado'].cumsum()

    # Process dates and filter data
    df['Data de Lançamento'] = pd.to_datetime(df['Data de Lançamento'])
    datas_lancamento = df[df['Data de Lançamento'] >= '2024-07-10'].groupby(by='Data de Lançamento').size().reset_index(name='Count')
    datas_lancamento = process_date_column(datas_lancamento, 'Data de Lançamento')

    select_data = st.sidebar.selectbox('Budget em', datas_lancamento['Data de Lançamento'])
    lancamentos_ate = pd.to_datetime(select_data, dayfirst=True)

    datas_programacao = df.groupby('Programação').size().reset_index(name='Count')
    datas_programacao = process_date_column(datas_programacao, 'Programação')
    select_datas_programacao = st.sidebar.selectbox('Programação', datas_programacao['Programação'])

    lancamento_date = datetime(2024, 7, 10)
    df_budget = df[
        (df['Data de Lançamento'] <= lancamento_date) |
        ((df['Data de Lançamento'] > lancamento_date) & (df['percent_unbudget'] == 0))
    ]

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

    # Unbudget data
    df_unbudget = df[
        (df['Data de Lançamento'] > lancamentos_ate) 
        & 
        (df['percent_unbudget'] > 0)
        # (df['Data de Lançamento'] < '2024-11-01')
    ].drop(columns=['_id', 'Saldo'])

    df_unbudget = df_unbudget.sort_values(by='Data de Lançamento').reset_index(drop=True)
    df_unbudget['Valor unbudget'] = df_unbudget['Valor Programado'] * df_unbudget['percent_unbudget']
    df_unbudget['Total Unbudget'] = df_unbudget['Valor unbudget'].cumsum()
    unbudget = df_unbudget['Valor unbudget'].sum()

    dias = (pd.Timestamp.now() - pd.to_datetime(select_data, format='%d/%m/%Y')).days
    media_dia_unbudget = unbudget / dias

    st.write(f'Unbudget após {select_data} R$ {utils.format_currency(unbudget)} :worried:')
    global meu_emoj
    if media_dia_unbudget <= 100: 
        meu_emoj = ':-1:' 
    else: 
        meu_emoj = ':clap:'
    st.write(f'Média diária em {dias} dias: R$ {utils.format_currency(media_dia_unbudget)} {meu_emoj}')
    df_unbudget.to_excel('excedente.xlsx')
    st.dataframe(df_unbudget)

    if st.button('Salvar unbudget'):
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        now = now.replace("-", "").replace(":", "").replace(".", "").replace(" ", "")
        df_unbudget.to_excel(f'./excel/unbudget{now}.xlsx', )

    # ==========================================================================================================================================
    # Database

    st.divider()
    df_database = df.copy()
    # df_database = df.drop(columns=['_id'])
    st.subheader('Database')
    st.dataframe(df_database)

    # ==========================================================================================================================================


    def save_data_base():
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        now = now.replace("-", "").replace(":", "").replace(".", "").replace(" ", "")
        df_database.to_excel(f'./excel/database{now}.xlsx', )

    st.button('Salvar', on_click=save_data_base)

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


    # Filtro por Programação
    st.divider()
    # df_filtered = df[df['Programação'] == select_datas_programacao]
    df_filtered = df[df['Programação'] == pd.to_datetime(select_datas_programacao, format='%d/%m/%Y')]
    df_filtered = df_filtered.sort_values(by=['Data de Lançamento'], ascending=[True])
    df_filtered = df_filtered.groupby(by='Fonte').sum('Valor Programado').drop(columns=['Saldo'])
    st.write(f'Programação para a data {select_datas_programacao}')
    st.dataframe(df_filtered)

    df_filtered = df[
        (df['Programação'] == pd.to_datetime(select_datas_programacao, format='%d/%m/%Y')) 
        & 
        (df['Fonte'] == fonte)
    ]
    df_filtered = df_filtered.sort_values(by=['Data de Lançamento'], ascending=[True])
    total = df_filtered['Valor'].sum()
    st.write(f'Lançamentos {fonte} programados para {select_datas_programacao}: {utils.format_currency(total)}')
    st.dataframe(df_filtered)

    # df_filtered.to_excel('Fatura Cartão.xlsx')

