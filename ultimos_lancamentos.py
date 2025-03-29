import utils
import pandas as pd
import streamlit as st

def show_page(df):
    st.header('Últimos Lançamentos')
    st.divider()

    ultimos = st.number_input(
        'Quantos lançamentos você quer ver?',
        min_value=1,
        max_value=len(df),
        value=len(df),
        step=1
    )
    if len(df) > ultimos:
        df = df[-ultimos:]
    
    total_lancamentos = df['Valor Programado'].sum()

    st.write(f'Aqui estão os últimos {len(df) - ultimos} lançamentos registrados.')
    st.dataframe(df, use_container_width=True)
    st.write(f'Total de lançamentos: {utils.format_currency(total_lancamentos)}')
    