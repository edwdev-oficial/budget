import plotly.express as px
from datetime import datetime
import streamlit as st
import pandas as pd
import utils

def show_controle_cartoes(df):

    # cartoes = ['Visa Platinum', 'Visa Signature', 'Nubank']

    # st.title('Controle de Gastos com Cartões de Crédito')
    # st.divider()

    # df['Data de Lançamento'] = pd.to_datetime(df['Data de Lançamento'], errors='coerce')

    # st.dataframe(df)

    # df.rename(columns={'Fonte': 'Cartão', 'Data de Lançamento': 'Data'}, inplace=True)
    # df['Valor'] = df['Valor'] * -1
    # df = df[df['Cartão'].isin(cartoes)].copy()
    # df.sort_values('Data', inplace=True)

    # df_filtered = df.copy()
    # df_filtered = df_filtered[df_filtered['Categoria'] != 'Saldo Fatura']
    # df_filtered['Data'] = df['Data'].apply(utils.format_date)
    # df_filtered['Vencimento'] = df['Vencimento'].apply(utils.format_date)
    # total = df_filtered['Valor'].sum()
    # st.write(f'Lançamentos R${utils.format_currency(total)}')
    # st.dataframe(df_filtered)

    # df_filtered_group = df.groupby(by=['Cartão', 'Data'])['Valor'].sum().reset_index()
    # df_filtered_group.sort_values('Data', inplace=True)
    # df_filtered_group.reset_index(drop=True, inplace=True)
    # df_filtered_group['Data'] = df_filtered_group['Data'].apply(utils.format_date)
    # df_filtered_group['Valor'] = df_filtered_group['Valor'].apply(utils.format_currency)

    # df_filtered_group = df.groupby(by=['Data']).sum('Valor').reset_index()
    # df_filtered_group.sort_values('Data', inplace=True)
    # df_filtered_group.reset_index(drop=True, inplace=True)
    # df_filtered_group['Data'] = df_filtered_group['Data'].apply(utils.format_date)

    # st.write('Lançamentos agrupados por cartão e data')
    # st.dataframe(df_filtered_group)

    # st.write('Lançamentos agrupados por data')
    # st.dataframe(df_filtered_group)

    # fig = px.line(
    #     df_filtered_group,
    #     x="Data",
    #     y="Valor",
    # )

    # st.plotly_chart(fig)

    # data_filter = st.sidebar.date_input('Lançamento')
    # data_filter = utils.format_date(data_filter)

    # bla = df.copy()
    # bla['Data'] = bla['Data'].apply(utils.format_date)

    # bla = df[
    #     df['Data'] == data_filter
    # ]

    # st.write(data_filter)

    # st.dataframe(bla)
    df['Data de Lançamento'] = pd.to_datetime(df['Data de Lançamento'], errors='coerce')
    df['Programação'] = pd.to_datetime(df['Programação'], errors='coerce')
    df.sort_values('Data de Lançamento', inplace=True)
    df['Valor'] = df['Valor'] * -1
    df['Valor Programado'] = df['Valor Programado'] * -1

    # Gastos com Cartões de Crédito
    cartoes = ['Visa Platinum', 'Visa Signature', 'Nubank']
    hide_categorias = [
        'Financiamento de fatura',
        'Juros Multa ou IOF', 
        'Pagamento Contas',
        'Valor reembolsavel'
    ]
    data_filter = datetime(2024, 7, 10)
    df_filtered = df.copy()
    df_filtered = df_filtered[
        (df_filtered['Fonte'].isin(cartoes))
        & (~df_filtered['Categoria'].isin(hide_categorias))
        & (df_filtered['Categoria'] != 'Saldo Fatura')
        & (df_filtered['Data de Lançamento'] >= data_filter)
    ]
    total = df_filtered['Valor'].sum()

    df_grouped = df_filtered.groupby(by=['Data de Lançamento']).sum('Valor').reset_index()

    st.subheader('Gastos com Cartões de Crédito')

    fig = px.line(
        df_grouped, 
        x='Data de Lançamento',
        y='Valor',
        title=f'Gastos com cartões de crédito a partir de {utils.format_date(data_filter)}'
    )

    st.plotly_chart(fig)

    data = utils.format_date(st.sidebar.date_input('Data de gasto'))

    df_filtered['Data de Lançamento'] = df_filtered['Data de Lançamento'].apply(utils.format_date)
    df_filtered = df_filtered[df_filtered['Data de Lançamento'] == data]
    df_filtered = df_filtered.groupby(by=['Categoria']).sum('Valor').reset_index()
    df_filtered.sort_values('Valor', inplace=True)
    total = df_filtered['Valor'].sum()
    st.write(f'Total gasto em {data} R$ {utils.format_currency(total)}')
    st.table(df_filtered[['Categoria', 'Valor']].reset_index(drop=True))

    # Vencimento de Faturas
    st.divider()
    st.subheader('Vencimento de Faturas')
    df_filtered = df.copy()
    df_filtered = df_filtered[
        (df_filtered['Fonte'].isin(cartoes))
    ]
    total = df_filtered['Valor'].sum()
    df_filtered['month/year'] = df_filtered['Vencimento'].dt.strftime('%Y-%m')
    df_group_monthyear = df_filtered.groupby(by=['month/year']).sum('Valor').reset_index()
    df_group_monthyear = df_group_monthyear.sort_values('month/year')

    st.write(f'Valor total das faturas acumulado: {utils.format_currency(total)}')

    fig = px.bar(
        df_group_monthyear,
        x='month/year',
        y='Valor',
        title='Vencimento de faturas',
    )

    st.plotly_chart(fig)

    df_group_monthyear = df_filtered.groupby(by=['Fonte', 'month/year']).sum('Valor').reset_index()
    df_group_monthyear = df_group_monthyear.sort_values('month/year')

    fig = px.bar(
        df_group_monthyear,
        x='month/year',
        y='Valor',
        color='Fonte',
        title='Vencimento de faturas por cartões',
    )

    st.plotly_chart(fig)


    vencimento = st.sidebar.date_input('Vencimento')
    df_filtered = df.copy()
    df_filtered = df_filtered[
        (df_filtered['Fonte'].isin(cartoes))
        & (df_filtered['Vencimento'] == pd.to_datetime(vencimento))
    ]
    total = df_filtered['Valor'].sum()
    st.write(f'Detalhamento para total de vencimento {utils.format_date(vencimento)}: R$ {utils.format_currency(total)}')
    st.dataframe(df_filtered)

    # Programações
    st.divider()
    st.subheader('Programações')
    df_filtered = df.copy()
    df_filtered = df_filtered[
        (df_filtered['Fonte'].isin(cartoes))
    ]
    df_grouped = df_filtered.groupby(by=['Programação']).sum('Valor Programado').reset_index()
    df_grouped = df_grouped.sort_values('Programação')
    df_grouped['Programação'] = df_grouped['Programação'].apply(utils.format_date)

    total = df_grouped['Valor Programado'].sum()
    st.write(f'Valor total programado acumulado: R$ {utils.format_currency(total)}')

    fig = px.bar(
        df_grouped,
        x='Programação',
        y='Valor Programado',
        title='Programações',
        text_auto=True
    )

    st.plotly_chart(fig)

    df_grouped = df_filtered.groupby(by=['Fonte', 'Programação']).sum('Valor Programado').reset_index()
    df_grouped = df_grouped.sort_values('Programação')

    df_grouped['Programação'] = df_grouped['Programação'].apply(utils.format_date)

    df_grouped['Programação'] = df_grouped['Programação'].astype(str)

    fig = px.bar(
        df_grouped,
        x='Programação',
        y='Valor Programado',
        color='Fonte',
        title='Programações por cartões',
        category_orders={'Programação': df_grouped['Programação'].unique().tolist()},
        text_auto=True
    )

    st.plotly_chart(fig)
