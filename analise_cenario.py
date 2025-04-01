import utils
import pandas as pd
import streamlit as st
import plotly.express as px

def show_page(df):
    st.title('Análise de Cenário')
    st.markdown("<hr style='border: 2px solid red;'>", unsafe_allow_html=True)

    df.drop([
        '_id',
        'Vencimento',
        'Valor',
        'Programação',
        'percent_unbudget',
        'createdAt',
        'parcela',
        'id_recurso'
    ], axis=1, inplace=True)

    # today = pd.to_datetime('2025-04-01').normalize()
    today = pd.to_datetime('today').normalize()
    date_ini = today.replace(day=1).date()
    date_fin = (today + pd.offsets.MonthEnd(0)).date()
    min_date = df['Data de Lançamento'].min()
    max_date = df['Data de Lançamento'].max()
    if max_date < today: max_date = today

    date_ini = pd.to_datetime(st.sidebar.date_input(
        'Período Inicial',
        value=date_ini,
        min_value=min_date,
        max_value=max_date
    ))
    date_fin = pd.to_datetime(st.sidebar.date_input(
        'Perído Final',
        value=today,
        min_value=min_date,
        max_value=max_date
    ))
    
    if date_fin >= date_ini:
        df = df.loc[
            (df['Data de Lançamento'] >= date_ini)
            &
            (df['Data de Lançamento'] <= date_fin)
            &
            (df['Valor Programado'] < 0)
            &
            (df['Categoria'] != 'Transferências')
        ].reset_index(drop=True)


        df_show = df.copy()

        df_show['Data de Lançamento'] = df_show['Data de Lançamento'].dt.date
        df_show.rename(columns={
            'Valor Programado': 'Valor',
            'Data de Lançamento': 'Data'
        }, inplace=True)

        st.dataframe(df_show.style.format({
            'Valor': lambda x: utils.format_column_currency(x)
        }), use_container_width=True)
        st.markdown("<hr style='border: 1px solid red;'>", unsafe_allow_html=True)

        #%% Resumo das informações e Gastos Agrupados por data
        dias = (date_fin - date_ini).days + 1
        if dias == 1:
            st.subheader(f"{dias} Dia Analisado")
        else:
            st.subheader(f"{dias} Dias Analisados")

        total_lancado = df['Valor Programado'].sum() * -1
        if total_lancado == -0.00: total_lancado = 0.00
        st.subheader(f"Total de Gastos Acumulados no Período: R$ {utils.format_currency(total_lancado)}")

        gasto_medio_diario = total_lancado / dias
        st.subheader(f"Média diária de gastos: R$ {utils.format_currency(gasto_medio_diario)}")

        st.markdown("<hr style='border: 1px solid red;'>", unsafe_allow_html=True)
        df_group_date = df.copy()
        df_group_date = df_group_date.groupby(by=['Data de Lançamento'])['Valor Programado'].sum().reset_index()

        date_range = pd.date_range(start=date_ini, end=date_fin, freq='D')

        df_full = pd.DataFrame(date_range, columns=['Data de Lançamento'])
        df_full = pd.merge(df_full, df_group_date, on='Data de Lançamento', how='left')
        df_full['Valor Programado'] = df_full['Valor Programado'].fillna(0.00)
        df_full['Valor Programado'] = df_full['Valor Programado'] * -1
        df_full.rename(columns={
            'Data de Lançamento': 'Data',
            'Valor Programado': 'Valor'
        }, inplace=True)
        df_full['Acumulado'] = df_full['Valor'].cumsum()
        st.subheader('Gastos Agrupados por Dia')
        st.dataframe(df_full.style.format({
            'Valor': lambda x: utils.format_column_currency(x),
            'Acumulado': lambda x: utils.format_column_currency(x),
        }), use_container_width=True)

        fig = px.bar(
            df_full,
            x='Data',
            y='Valor',
            title='Gastos por dia',
            labels={
                'Data': 'Data',
                'Valor': 'Valor'
            }
        )

        st.plotly_chart(fig)

        st.markdown("<hr style='border: 1px solid red;'>", unsafe_allow_html=True)
        #%% Gastos Agrupados por Categoria
        st.subheader('Gastos Agrupados por Categoria')
        df_group_category = df.copy()
        df_group_category = df_group_category.groupby(by='Categoria')['Valor Programado'].sum().reset_index()
        df_group_category.sort_values(by=['Valor Programado'], inplace=True)
        df_group_category.reset_index(drop=True, inplace=True)
        df_group_category['Acumulado'] = df_group_category['Valor Programado'].cumsum()
        df_group_category.rename(columns={
            'Valor Programado': 'Valor'
        }, inplace=True)
        st.dataframe(df_group_category.style.format({
            'Valor': lambda x: utils.format_column_currency(x),
            'Acumulado': lambda x: utils.format_column_currency(x)
        }), use_container_width=True)

        df_group_category['Valor'] = df_group_category['Valor'] * -1

        fig = px.bar(
            df_group_category,
            x='Categoria',
            y='Valor',
            title='Gastos por categoria'
        )

        st.plotly_chart(fig)
