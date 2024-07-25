import plotly.express as px
import streamlit as st
import pandas as pd
import utils

def show_controle_cartoes(df):

    cartoes = ['Visa Platinum', 'Visa Signature', 'Nubank']

    st.title('Controle de Gastos com Cartões de Crédito')
    st.divider()

    st.dataframe(df)

    df.drop(columns=['_id', 'Programação', 'Valor Programado'], inplace=True)
    df.rename(columns={'Fonte': 'Cartão', 'Data de Lançamento': 'Data'}, inplace=True)
    df['Valor'] = df['Valor'] * -1
    df = df[df['Cartão'].isin(cartoes)]
    df = df[df['Categoria'] != 'Saldo Fatura']
    df.sort_values('Data', inplace=True)
    df.reset_index(drop=True, inplace=True)

    df_filtered = df.copy()
    df_filtered['Data'] = df['Data'].apply(utils.format_date)
    df_filtered['Vencimento'] = df['Vencimento'].apply(utils.format_date)
    total = df_filtered['Valor'].sum()
    st.write(f'Lançamentos R${utils.format_currency(total)}')
    st.dataframe(df_filtered)

    df_filtered.to_excel('df_filtered.xlsx', index=False)

    # df_filtered_group = df.groupby(by=['Cartão', 'Data'])['Valor'].sum().reset_index()
    # df_filtered_group.sort_values('Data', inplace=True)
    # df_filtered_group.reset_index(drop=True, inplace=True)
    # df_filtered_group['Data'] = df_filtered_group['Data'].apply(utils.format_date)
    # # df_filtered_group['Valor'] = df_filtered_group['Valor'].apply(utils.format_currency)

    # st.write('Lançamentos agrupados por cartão e data')
    # st.dataframe(df_filtered_group)

    # df_filtered_group = df.groupby(by=['Data']).sum('Valor').reset_index()
    # df_filtered_group.sort_values('Data', inplace=True)
    # df_filtered_group.reset_index(drop=True, inplace=True)
    # df_filtered_group['Data'] = df_filtered_group['Data'].apply(utils.format_date)
    # # # df_filtered_group['Valor'] = df_filtered_group['Valor'].apply(utils.format_currency)

    # st.write('Lançamentos agrupados por data')
    # st.dataframe(df_filtered_group)

    # fig = px.line(
    #     df_filtered_group,
    #     x="Data",
    #     y="Valor",
    # )

    # st.plotly_chart(fig)
