import utils
import pandas as pd
import streamlit as st
from datetime import datetime
from database import get_database
from bson import ObjectId
from dateutil.relativedelta import relativedelta

def show_home(df):

    db = get_database()
    collection_recurso = db['recurso']
    doc_recurso = list(collection_recurso.find())

    if doc_recurso:
        saldo = doc_recurso[0]['Valor Programado'] * -1
        if saldo == -0.00: saldo = 0.00
        st.title(f'Saldo {doc_recurso[0]["Descrição"]}')
        st.title(f'R$ {utils.format_currency(saldo)}')

        st.divider()
        
        df = df.drop(columns=[
            # '_id',
            'Vencimento',
            'Programação',
            'Categoria'
        ])

        if 'id_recurso' in df.columns:
            df = df[
                (df['id_recurso'] == doc_recurso[0]['id_recurso']) 
            ]

            df.sort_values(by=['createdAt'], inplace=True)
            df.reset_index(drop=True, inplace=True)
            # df.sort_values(by=['Data de Lançamento'], inplace=True)

            df['Total Acumulado'] = df['Valor Programado'].cumsum()

            if len(df): 
                st.dataframe(df)
                df_unbudget = df[df['percent_unbudget'] > 0]
                if len(df_unbudget):
                    df_unbudget = df_unbudget.copy()
                    df_unbudget['valor_unbudget'] = df_unbudget['Valor Programado'] * df['percent_unbudget'] 
                    total_unbudget = df_unbudget['valor_unbudget'].sum() * -1
                    st.write(f'<h1 style="color:red">Sua verba está estourada em: R$ {utils.format_currency(total_unbudget)}</h1>', unsafe_allow_html=True)

    #     # if st.button('Corrigir percentuais ungudget'):

    #     #     valor_programado = -3000
    #     #     estouro = 0
    #     #     list_dict = []

    #     #     for index, row in df.iterrows():
    #     #         # st.write(row)
    #     #         percent_ubudget = 0
    #     #         if valor_programado < row['Valor Programado']:
    #     #             percent_ubudget = 0
    #     #         elif valor_programado == row['Valor Programado']:
    #     #             percent_ubudget = 0
    #     #         else:
    #     #             if valor_programado == 0:
    #     #                 percent_ubudget = 1
    #     #             else:
    #     #                 diferenca = row['Valor Programado'] - saldo
    #     #                 percent_ubudget = diferenca / row['Valor Programado']
    #     #         saldo = valor_programado - row['Valor Programado']
    #     #         if saldo > 0: saldo = 0
    #     #         estouro = estouro + row['Valor Programado'] * percent_ubudget 
    #     #         dict_row = {
    #     #             '_id': row['_id'],
    #     #             'Valor Programado': row['Valor Programado'],
    #     #             'percent_unbudget': row['percent_unbudget'],
    #     #             'novo_percent_unbudget': percent_ubudget,
    #     #             'saldo': saldo,
    #     #             'estouro': estouro
    #     #         }
    #     #         valor_programado = saldo
    #     #         list_dict.append(dict_row)

    #     #     collection_budget_test = db['budget_test']
    #     #     for dict in list_dict:
    #     #         id = ObjectId(dict['_id'])
    #     #         new_percent_ubudget = dict['novo_percent_unbudget'] 
    #     #         st.write(id)
    #     #         st.write(new_percent_ubudget)
    #     #         collection_budget_test.update_one(
    #     #             {'_id': id},
    #     #             {'$set': {'percent_unbudget': new_percent_ubudget}}
    #     #         )

    #     # if st.button('Ver gasto com viagens'):
    #     #     collection_budget = db['budget_test']
    #     #     df_budget_alvo = pd.DataFrame(list(collection_budget.find(
    #     #         {
    #     #             'Categoria': 'Viagens',
    #     #             '$and': [
    #     #                 {'Data de Lançamento': {'$gte': datetime(2025, 1, 1)}},
    #     #                 {'Data de Lançamento': {'$lte': datetime(2025, 1, 10)}}                        
    #     #             ]
    #     #         }
    #     #     )))
    #     #     df_budget_alvo['Acumulado'] = df_budget_alvo['Valor Programado'].cumsum()
    #     #     st.dataframe(df_budget_alvo)
    #     #     total_viagem = df_budget_alvo['Valor Programado'].sum() * -1
    #     #     st.write(f'<h1 style="color:red">Gasto com viagems no período selecionado: R$ {utils.format_currency(total_viagem)}</h1>', unsafe_allow_html=True)
    #     #     st.markdown(f'<h1 style="color:red;">Gasto com viagens no período selecionado: R$ {utils.format_currency(total_viagem)}</h1>', unsafe_allow_html=True)
    #     #     st.write(f'## :red[Gasto com viagens no período selecionado: R$ {utils.format_currency(total_viagem)}]')

    #     # if st.button('Ver despesas'):
    #     #     collection_budget = db['budget_test']
    #     #     df_budget_alvo = pd.DataFrame(list(collection_budget.find(
    #     #         {
    #     #             'Categoria': {'$ne': 'Transferências'},  	
    #     #             '$and': [
    #     #                 {'Data de Lançamento': {'$gte': datetime(2025, 1, 1)}},
    #     #                 {'Data de Lançamento': {'$lte': datetime(2025, 1, 31)}}                        
    #     #             ]
    #     #         }
    #     #     )))
    #     #     df_budget_alvo['Acumulado'] = df_budget_alvo['Valor Programado'].cumsum()
    #     #     st.dataframe(df_budget_alvo)
    #     #     total_viagem = df_budget_alvo['Valor Programado'].sum() * -1
    #     #     st.markdown(f'<h1 style="color:red;">Gastos no período selecionado: R$ {utils.format_currency(total_viagem)}</h1>', unsafe_allow_html=True)


    # else:
    #     st.title('Nenhum recurso selecionado para os lançamentos')

    # st.divider()
    # collection_budget_test = db['budget_test']
    # df_salarios_fim_mes_sem_bonus = pd.DataFrame(list(collection_budget_test.find({
    #     'Fonte': 'Salário',
    #     'Programação': {'$gte': pd.to_datetime('2025-02-28')},
    #     'Descrição': 'Salário',
    #     '$expr': {
    #         '$and': [
    #             {'$ne': [{'$dayOfMonth': '$Programação'}, 15]},
    #             {'$ne': [{'$month': '$Programação'}, 1]},
    #             {'$ne': [{'$month': '$Programação'}, 4]},
    #             {'$ne': [{'$month': '$Programação'}, 7]},
    #             {'$ne': [{'$month': '$Programação'}, 10]},
    #             # {'$or': [
    #             #     {'$eq': [{'$month': '$Programação'}, 1]},
    #             #     {'$eq': [{'$month': '$Programação'}, 4]},
    #             #     {'$eq': [{'$month': '$Programação'}, 7]},
    #             #     {'$eq': [{'$month': '$Programação'}, 10]},
    #             # ]}
    #             # {'$eq': [{'$month': '$Programação'}, 8]}
    #         ]
    #     }
    # })))
    # df_salarios_fim_mes_sem_bonus.sort_values(by='Programação', inplace=True)
    # df_salarios_fim_mes_sem_bonus.reset_index(drop=True, inplace=True)
    # st.write('Salários fim mês sem bonus')
    # st.dataframe(df_salarios_fim_mes_sem_bonus)
    # salario_total_programado = df_salarios_fim_mes_sem_bonus['Valor Programado'].sum()
    # st.write(f'Salários fim mês sem bonus: {len(df_salarios_fim_mes_sem_bonus)} registors - Valor total programado: {utils.format_currency(salario_total_programado)}')

    # df_salarios_fim_mes_sem_bonus_alterado = df_salarios_fim_mes_sem_bonus.copy()
    # df_salarios_fim_mes_sem_bonus_alterado['Valor Programado'] = 4145.55
    # st.write('Salários fim mês sem bonus alterado')
    # st.dataframe(df_salarios_fim_mes_sem_bonus_alterado)
    # salario_total_programado_alterado = df_salarios_fim_mes_sem_bonus_alterado['Valor Programado'].sum()
    # st.write(f'Salários fim mês sem bonus: {len(df_salarios_fim_mes_sem_bonus_alterado)} registors - Valor total programado: {utils.format_currency(salario_total_programado_alterado)}')

    # diferenca_salarios_fim_mes_sem_bonus = salario_total_programado_alterado - salario_total_programado
    # st.write(f'Diferença salário fim mês sem bonus {utils.format_currency(diferenca_salarios_fim_mes_sem_bonus)}')

    # if st.button('Alterar Salários fim mês sem bonus'):
    #     for index, document in df_salarios_fim_mes_sem_bonus.iterrows():
    #         id = ObjectId(document['_id'])
    #         collection_budget_test.update_one(
    #             {'_id': id},
    #             {'$set': {'Valor Programado': 4145.55}}
    #         )

    # #%% PPRs
    # st.divider()
    # st.write('PPRs Fev')
    # collection_budget_test = db['budget_test']
    # df_pprs_fev = pd.DataFrame(list(collection_budget_test.find({
    #     'Fonte': 'Salário',
    #     'Programação': {'$gte': pd.to_datetime('2025-02-28')},
    #     'Descrição': 'PPR',
    #     '$expr': {
    #         '$and': [
    #             {'$ne': [{'$dayOfMonth': '$Programação'}, 15]},
    #             {'$eq': [{'$month': '$Programação'}, 2]},
    #         ]
    #     }
    # })))
    # df_pprs_fev.sort_values(by=['Programação'], inplace=True)
    # df_pprs_fev.reset_index(drop=True, inplace=True) 
    # st.dataframe(df_pprs_fev)
    # total_pprs_fev = df_pprs_fev['Valor Programado'].sum()
    # st.write(f'PPRs Fev: {len(df_pprs_fev)} registros - Valor total {utils.format_currency(total_pprs_fev)}')

    # df_pprs_fev_alterado = df_pprs_fev.copy()
    # df_pprs_fev_alterado['Valor Programado'] = 1235.77
    # st.dataframe(df_pprs_fev_alterado)
    # total_pprs_fev_alterado = df_pprs_fev_alterado['Valor Programado'].sum()
    # st.write(f'PPRs Fev: {len(df_pprs_fev_alterado)} registros - Valor total {utils.format_currency(total_pprs_fev_alterado)}')


    # dif_ppr_fev = total_pprs_fev - total_pprs_fev_alterado
    # st.write(f'Diferença PPRs Fev {utils.format_currency(dif_ppr_fev)}')

    # dif_final = diferenca_salarios_fim_mes_sem_bonus - dif_ppr_fev
    # st.write(f'Diferença final {utils.format_currency(dif_final)}')

    # if st.button('Alterar PPRs'):
    #     for index, row in df_pprs_fev.iterrows():
    #         st.write(row)
    #         id = ObjectId(row['_id'])
    #         collection_budget_test.update_one(
    #             {'_id': id},
    #             {'$set': {'Valor Programado': 1235.77}}
    #         )

    # #%% Incluir adiantamentos PPRs
    # st.divider()
    # if st.button('Incluir adiantamentos PPRs'):
    #     collection_budget_test = db['budget_test']
    #     date = datetime(2025, 8, 31)
    #     for index in range(1, 18):
    #         document = {
    #             'Data de Lançamento': datetime(2024, 7, 10),
    #             'Fonte': 'Salário',
    #             'Descrição': 'Adiantamento PPR',
    #             'Vencimento': date,
    #             'Valor': 2471.23,
    #             'Programação': date,
    #             'Valor Programado': 2471.23,
    #             'Categoria': 'Salário',
    #             'percent_unbudget': 0,
    #         }
    #         collection_budget_test.insert_one(document)
    #         # Verifica se já existe um registro igual antes de inserir
    #         if not collection_budget_test.find_one({'Vencimento': date, 'Descrição': 'Adiantamento PPR'}):
    #             collection_budget_test.insert_one(document)
    #         date = date  + relativedelta(years=1)
    #     st.success("Adiantamentos PPRs incluídos com sucesso!")            