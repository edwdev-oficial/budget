import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode
from database import collection
from bson import ObjectId
import pandas as pd
from datetime import datetime

def change_all(df):

    fields = df.columns.tolist()
    fields.remove('_id')
    change_field = st.selectbox('Field', fields)
    field_type = df[change_field].dtypes

    if field_type == 'object':
        value_data = st.text_input('Alterar para:')
    elif field_type == 'float64':
        value_data = st.number_input('Alterar para:')
    elif field_type == 'datetime64[ns]':
        value_data = st.date_input('Alterar para:')
        # programacao = datetime.combine(programacao, datetime.min.time()) 
        value_data = datetime.combine(value_data, datetime.min.time())

    if st.button('Salvar'):
        for index, row in df.iterrows():
            _id = ObjectId(row['_id'])
            # st.write(_id, change_field ,value_data)
            novo_valor = { change_field: value_data }
            st.write(novo_valor)

            budget = collection()

            budget.update_one({'_id': _id}, {'$set': novo_valor})

def show_controle_saldo(df):
    
    st.header('Controle Saldo')
    st.divider()

    considerar_flash = st.sidebar.toggle('Considerar Flash')

    df_descricao = df.copy()
    df_descricao = df_descricao.groupby(['Descrição']).size().reset_index(name='Count')
    descricao_options = df_descricao['Descrição'].tolist()
    descricao_options.insert(0, '')
    descricao_option = st.sidebar.selectbox('Descrição:', descricao_options)

    df_copy = df.copy()

    if considerar_flash == False:
        df_copy = df_copy[df_copy['Fonte'] != 'Flash']

    # AgGrid 1

    df_group = df_copy.groupby(['Fonte', 'Programação'])['Valor Programado'].sum().reset_index()
    df_group = df_group.sort_values(by=['Programação', 'Valor Programado'], ascending=[True, False])
    df_group['Saldo'] = df_group['Valor Programado'].cumsum()
    df_group['Status Saldo'] = df_group['Saldo'].apply(lambda x: 'Negativo' if x <0 else 'Positivo')
    df_group['Status Limite'] = df_group['Saldo'].apply(lambda x: 'Estourado' if x < -16690 else '')

    gb = GridOptionsBuilder.from_dataframe(df_group)
    gb.configure_selection('single')

    grid_options = gb.build()

    date_init = st.sidebar.date_input('A partir de:')

    hoje = pd.to_datetime(date_init).normalize()

    df_ultimo_registro_anterior = df_group[df_group['Programação'] < hoje].iloc[[-1]]

    df_group = df_group[df_group['Programação'] >= hoje]
    df_group = pd.concat([df_ultimo_registro_anterior, df_group], ignore_index=True)

    grid_response = AgGrid(
        df_group,
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
        print()
        selected_row = selected_rows.iloc[0]

        df_filtered = df.copy()
        if considerar_flash:
            df_filtered = df_filtered[
                (df_filtered['Fonte'] == selected_row['Fonte']) 
                &
                (df_filtered['Programação'] == selected_row['Programação'])
            ]
        else:
            df_filtered = df_filtered[
                (df_filtered['Fonte'] == selected_row['Fonte']) 
                &
                (df_filtered['Programação'] == selected_row['Programação'])
                &
                (df_filtered['Fonte'] != 'Flash')
            ]

        # AgGrid 2
        # st.dataframe(df_filtered)

        gb_filtered = GridOptionsBuilder.from_dataframe(df_filtered)
        gb_filtered.configure_selection('single')
        gb_filtered.configure_column('_id', hide=True)
        grid_options_filtered = gb_filtered.build()

        grid_response = AgGrid(
            df_filtered,
            gridOptions = grid_options_filtered,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            update_mode = GridUpdateMode.MODEL_CHANGED,
            theme = 'alpine',
            enable_enterprise_modules = False,
            height = 300,
            width ='100%',
            reload_data = True
        )

        alterar_todos = st.toggle('Alterar todos')
        if alterar_todos == True:
            change_all(df_filtered)
        else:
            selected_rows = grid_response['selected_rows']
            if selected_rows is not None and len(selected_rows) > 0:

                    selected_row = selected_rows.iloc[0]

                    st.write(selected_row['_id'])
                    st.write(datetime.fromisoformat(selected_row['Data de Lançamento']))

                    data_lancamento = st.date_input('Lançamento', datetime.fromisoformat(selected_row['Data de Lançamento']))
                    fonte = st.text_input('Fonte', selected_row['Fonte'])
                    descricao = st.text_input('Descrição', selected_row['Descrição'])
                    vencimento = st.date_input('Vencimento', datetime.fromisoformat(selected_row['Vencimento']))
                    valor = st.number_input('Valor', value=float(selected_row['Valor']))
                    programacao = st.date_input('Programação', datetime.fromisoformat(selected_row['Programação']))
                    valor_programado = st.number_input('Valor Programado', value=float(selected_row['Valor Programado']))
                    categoria = st.text_input('Categoria', selected_row['Categoria'])

                    data_lancamento = datetime.combine(data_lancamento, datetime.min.time())
                    vencimento = datetime.combine(vencimento, datetime.min.time())
                    programacao = datetime.combine(programacao, datetime.min.time())

                    col1, col2 = st.columns([2, 1])
                    budget = collection()
                    novos_valores = {
                        'Data de Lançamento': data_lancamento,
                        'Fonte': fonte,
                        'Descrição': descricao,
                        'Vencimento': vencimento,
                        'Valor': valor,
                        'Programação': programacao,
                        'Valor Programado': valor_programado,
                        'Categoria': categoria,
                        'percent_unbudget': 1 
                    }
                    with col1:
                        if st.button('Salvar alterações'):
                            _id = ObjectId(selected_row['_id'])
                            budget.update_one({'_id': _id}, {'$set': novos_valores})
                            st.success('Dados alterados com sucesse!')
                    with col2:
                        if st.button('Duplicar registro'):
                            novos_valores['Data de Lançamento'] = pd.to_datetime('today').normalize()
                            novos_valores['createdAt'] = pd.to_datetime('now')
                            budget.insert_one(novos_valores)
                            st.success('Dado duplicado com sucesso!')


# # 

#     # AgGrid 3


#     if descricao_option != '':
#         st.divider()
#         st.subheader('Editar')
#         df_filtered = df.copy()
#         df_filtered = df_filtered[
#             (df_filtered['Descrição'] == descricao_option)
#         ]

#         df_filtered = df_filtered.sort_values(by=['Programação', 'Vencimento'])

#         gb_filtered = GridOptionsBuilder.from_dataframe(df_filtered)
#         gb_filtered.configure_selection('single')
#         gb_filtered.configure_column('_id', hide=True)
#         grid_options_filtered = gb_filtered.build()

#         grid_response = AgGrid(
#             df_filtered,
#             gridOptions = grid_options_filtered,
#             data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
#             update_mode = GridUpdateMode.MODEL_CHANGED,
#             theme = 'alpine',
#             enable_enterprise_modules = False,
#             height = 300,
#             width ='100%',
#             reload_data = True
#         )


















































        #%% Parte para alteração de todos os registros com a mesma descrição (revisar)
        # alterar_todos = st.toggle('Alterar todos desta descrição')
        # if alterar_todos == True:
        #     change_all(df_filtered)
        #     # fields = df_filtered.columns.tolist()
        #     # fields.remove('_id')
        #     # change_field = st.selectbox('Field', fields)
        #     # field_type = df_filtered[change_field].dtypes

        #     # if field_type == 'object':
        #     #     value_data = st.text_input('Alterar para:')
        #     # elif field_type == 'float64':
        #     #     value_data = st.number_input('Alterar para:')
        #     # elif field_type == 'datetime64[ns]':
        #     #     value_data = st.date_input('Alterar para:')

        #     # if st.button('Salvar'):
        #     #     st.write('Enviar')
        #     #     # for valor in df_filtered['_id']:
        #     #     #     _id = ObjectId(valor)
        #     #     #     data = collection.find({"_id": _id})
        #     #     #     # st.write(_id, change_field, value_data)
        #     #     #     # collection.update_one({"_id": _id}, {"$set": {change_field: value_data}})
        #     #     #     d_list = list(data)
        #     #     #     st.write(d_list)

        # else:
        #     selected_rows = grid_response['selected_rows']
        #     if selected_rows is not None and len(selected_rows) > 0:

        #             selected_row = selected_rows.iloc[0]

        #             st.write(selected_row['_id'])
        #             st.write(datetime.fromisoformat(selected_row['Data de Lançamento']))
                    
        #             valor_program = float(selected_row['Valor Programado'])
        #             st.write(valor_program)

        #             data_lancamento = st.date_input('Lançamento', datetime.fromisoformat(selected_row['Data de Lançamento']))
        #             fonte = st.text_input('Fonte', selected_row['Fonte'])
        #             descricao = st.text_input('Descrição', selected_row['Descrição'])
        #             vencimento = st.date_input('Vencimento', datetime.fromisoformat(selected_row['Vencimento']))
        #             valor = st.number_input(label='Valor', value=selected_row['Valor'], step=0.01)
        #             programacao = st.date_input('Programação', datetime.fromisoformat(selected_row['Programação']))
        #             valor_programado = st.number_input(label='Valor Programado', value=valor_program, step=0.01)
        #             categoria = st.text_input('Categoria', selected_row['Categoria'])

        #             data_lancamento = datetime.combine(data_lancamento, datetime.min.time())
        #             vencimento = datetime.combine(vencimento, datetime.min.time())
        #             programacao = datetime.combine(programacao, datetime.min.time())

        #             # col1, col2 = st.columns(2)
        #             # with col1:
        #             #     if st.button('Salvar alteraçõessssssss'):
        #             #         novos_valores = {
        #             #             'Data de Lançamento': data_lancamento,
        #             #             'Fonte': fonte,
        #             #             'Descrição': descricao,
        #             #             'Vencimento': vencimento,
        #             #             'Valor': valor,
        #             #             'Programação': programacao,
        #             #             'Valor Programado': valor_programado,
        #             #             'Categoria': categoria    
        #             #         }

        #             #         _id = ObjectId(selected_row['_id'])

        #             #         st.write(_id)
        #             #         st.write(novos_valores)

        #             #         budget = collection()

        #             #         st.write('VEIO EM ALTERAR REGISTRO: ', _id)
        #             #         budget.update_one({'_id': _id}, {'$set': novos_valores})

        #             #         documents = budget.find({'_id': _id})

        #             #         df = pd.DataFrame(documents)
        #             #         st.write(df)
        #             # with col2:
        #             #     if st.button('Duplicar registro'):
        #             #         pass
                        

    #%% Alteração via código
    st.divider()
    st.subheader('Alteração via código', divider='red')
    collection_budget = collection()
    # data = list(collection_budget.find(
    #     {'Programação': {'$gte': pd.to_datetime('2025-04-01').normalize()}},
    # ))
    data = list(
        collection_budget.find(
            {
                '$expr': {
                    '$in': [
                        {
                            '$month': '$Programação'
                        },
                        [
                            1,
                            2
                        ]
                    ]
                }
            }
        )
    )
    
    data_filter = [item for item in data if item['Descrição'] == 'IPTU']
    dados_ordenados = sorted(data_filter, key=lambda x: x['Programação'])
    st.write(f'Total de registros: {len(dados_ordenados)}')
    for index, item in enumerate(dados_ordenados):
        st.divider()
        st.write(index + 1) 
        st.write(f'_id: {item["_id"]}')
        st.write(f'Data de Lançamento: {item["Data de Lançamento"]}')
        st.write(f'Fonte: {item["Fonte"]}')
        st.write(f'Descrição: {item["Descrição"]}')
        st.write(f'Vencimento: {item["Vencimento"]}')
        st.write(f'Valor: {item["Valor"]}')
        st.write(f'Programação: {item["Programação"]}')
        st.write(F'Valor Programado: {item["Valor Programado"]}')
        st.write(f'Categoria: {item["Categoria"]}')
        if st.button(f'Excluir {item["_id"]}'):
            collection_budget.delete_one({"_id": item['_id']})
            st.success('Registro excluído com sucesso!')
        if st.button(f"Alterar Vencimento {item['_id']}"):
            month = item['Vencimento'].month
            year = item['Vencimento'].year
            new_date = pd.to_datetime(f'{year}-{month}-10')
            st.write(new_date)
            collection_budget.update_one(
                {'_id': item['_id']},
                {'$set': {
                        'Vencimento': new_date,
                        'Programação': new_date
                    }
                }
            )
            st.success('Registro alterado com sucesso!')
        if st.button(f'Alterar valor {item['_id']}'):
            collection_budget.update_one(
                {'_id': item['_id']},
                {'$set': {
                        'Valor': -215.04,
                        'Valor Programado': -215.04
                    }
                }
            )
            st.success('Registro alterado com sucesso!')
        
        # _id = ObjectId(item['_id'])
        # novos_valores = {
        #     'Data de Lançamento': item['Data de Lançamento'],
        #     'Fonte': item['Fonte'],
        #     'Descrição': item['Descrição'],
        #     'Vencimento': item['Vencimento'],
        #     'Valor': item['Valor'],
        #     'Programação': item['Programação'],
        #     'Valor Programado': item['Valor Programado'],
        #     'Categoria': item['Categoria']
        # }
        # collection_budget.update_one({'_id': _id}, {'$set': novos_valores})
    # st.write(len(dados_ordenados))
    # st.write(dados_ordenados)