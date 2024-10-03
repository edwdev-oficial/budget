from datetime import datetime
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np

def format_currency(valor):
    return f'{valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
def show_budget(df):

    st.header('Resultado Projetado')

    now = pd.to_datetime('now')
    default_budget_date = pd.to_datetime('2024-07-10').date()
    budget_date = st.sidebar.date_input('Budget Em', value=default_budget_date)
    lancamentos_ate = st.sidebar.date_input('Lançamentos até')
    budget_date = pd.to_datetime(budget_date)
    lancamentos_ate = pd.to_datetime(lancamentos_ate)

    df['Data de Lançamento'] = pd.to_datetime(df['Data de Lançamento'])
    df['Programação'] = pd.to_datetime(df['Programação'])
    df = df.sort_values(['Programação', 'Valor Programado'], ascending=[True, False])
    df['AnoMes'] = df['Programação'].dt.to_period('M').astype(str)
    df['Saldo'] = df['Valor Programado'].cumsum()

    df = df[df['Data de Lançamento'] <= lancamentos_ate]

    #df_anterior================================================================ 

    df_anterior = df.copy()
    df_anterior = df_anterior[
        (df_anterior['Programação'] < budget_date)
    ]

    if not df_anterior.empty:

        df_ultima_linha_df_anterior = df_anterior.iloc[[-1]]

        df_ultima_linha_df_anterior.loc[:, 'Fonte'] = 'Conta Corrente Itaú'
        df_ultima_linha_df_anterior.loc[:, 'Descrição'] = 'Saldo anterior'
        df_ultima_linha_df_anterior.loc[:, 'Categoria'] = 'Saldo anterior'
        df_ultima_linha_df_anterior.loc[:, 'Valor Programado'] = df_ultima_linha_df_anterior['Saldo']
        df_ultima_linha_df_anterior.loc[:, 'percent_unbudget'] = 0


    #df_posterior_programado===================================================== 

    df_posterior_programado = df.copy()
    df_posterior_programado = df_posterior_programado[
        (df_posterior_programado['Programação'] >= budget_date) 
    ]

    if not df_anterior.empty:
        df_posterior_programado = pd.concat([df_ultima_linha_df_anterior, df_posterior_programado], ignore_index=True)

    df_posterior_programado['percent_unbudget'] = np.where(
        df_posterior_programado['Data de Lançamento'] < budget_date,
        0,
        df_posterior_programado['percent_unbudget']
    )

    df_posterior_programado['Valor Programado'] = df_posterior_programado['Valor Programado'] * (1-df_posterior_programado['percent_unbudget'])
    df_posterior_programado['Saldo'] = df_posterior_programado['Valor Programado'].cumsum()

    df_posterior_programado = df_posterior_programado.groupby('Programação')['Valor Programado'].sum()
    df_posterior_programado = df_posterior_programado.groupby(pd.Grouper(freq='ME')).sum().reset_index()
    df_posterior_programado['Saldo'] = df_posterior_programado['Valor Programado'].cumsum()
    df_posterior_programado.rename(columns={'Valor Programado': 'ResultMonth', 'Saldo': 'Balance'}, inplace=True)

    #df_posterior_realizado===================================================== 

    df_posterior_realizado = df.copy()
    df_posterior_realizado = df_posterior_realizado[
        (df_posterior_realizado['Programação'] >= pd.to_datetime(budget_date))
    ]

    if not df_anterior.empty:
        df_posterior_realizado = pd.concat([df_ultima_linha_df_anterior, df_posterior_realizado], ignore_index=True)

    df_posterior_realizado['Saldo'] = df_posterior_realizado['Valor Programado'].cumsum()

    df_posterior_realizado = df_posterior_realizado.groupby('Programação')['Valor Programado'].sum()
    df_posterior_realizado = df_posterior_realizado.groupby(pd.Grouper(freq='ME')).sum().reset_index()
    df_posterior_realizado['Saldo'] = df_posterior_realizado['Valor Programado'].cumsum()
    df_posterior_realizado.rename(columns={'Valor Programado': 'ChangeResult', 'Saldo': 'ChangeBalance'}, inplace='True')

#df_merge===================================================== 

    df_join = pd.merge(df_posterior_programado, df_posterior_realizado, on='Programação', how='outer')
    df_join['Diference'] = (df_join['ChangeBalance'] - df_join['Balance'])
    df_join = df_join.fillna(0)
    st.divider()

    fig = px.line(
        df_join,
        x='Programação',
        y=['Balance', 'ChangeBalance'], labels={'value': 'Saldo (R$)', 'variable': 'Legend'},
        title='Bugdet inicial e atual',
        markers=True,
        # text='y'
    )
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig)


    st.divider()
    st.subheader('Corrected budget')
    st.dataframe(df_join.style.format({
        "ResultMonth": "{:.2f}",
        "Balance": "{:.2f}",
        "ChangeResult": "{:.2f}",
        "ChangeBalance": "{:.2f}",
        "Diference": "{:.2f}"
    }))


    #df_unbudget===================================================== 

    df_unbudget = df.copy()
    df_unbudget = df_unbudget[
        (df_unbudget['Data de Lançamento'] >= pd.to_datetime(budget_date)) 
        &
        (df_unbudget['percent_unbudget'] > 0)
    ]

    df_unbudget['Valor Programado'] = df_unbudget['Valor Programado'] * df_unbudget['percent_unbudget']
    df_unbudget = df_unbudget.drop(columns=['_id', 'Vencimento', 'Programação', 'percent_unbudget', 'AnoMes', 'Saldo'], axis=1)

    df_unbudget = df_unbudget.sort_values(['Data de Lançamento']).reset_index()

    df_unbudget = df_unbudget.groupby(by=[
        'Data de Lançamento',
        'Fonte',
        'Descrição',
        'Categoria'
    ])['Valor Programado'].sum().reset_index()    

    df_unbudget = df_unbudget.rename(columns={'Valor Programado': 'Valor'})
    df_unbudget = df_unbudget[df_unbudget['Valor'] != 0]
    df_unbudget['Acumulado'] = df_unbudget['Valor'].cumsum()


    total_unbudget = df_unbudget['Valor'].sum()

    st.divider()
    formatted_date = budget_date.strftime("%d/%m/%Y")
    st.subheader(f'Unbudget apartir de {formatted_date} : R$ {format_currency(total_unbudget * -1)}')
    dias = (pd.Timestamp.now() - pd.to_datetime(budget_date, format='%d/%m/%Y')).days + 1
    st.write(f'Média diária em {dias} dias: R$ {format_currency(total_unbudget * -1 / dias)}')
    df_unbudget['Data de Lançamento'] = df_unbudget['Data de Lançamento'].dt.strftime('%d/%m/%Y')
    df_unbudget = df_unbudget.style.format({"Valor": "{:.2f}", "Acumulado": "{:.2f}"})
    st.dataframe(df_unbudget)