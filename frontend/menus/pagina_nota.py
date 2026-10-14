import streamlit as st
from connection.base_api import BaseApi
import pandas as pd


base = BaseApi()
id = st.text_input("Digite o ID")
id = int(id)

endpoint = f"/alunos/pegar-dados-aluno-por-id/{id}"
dados = base.get(endpoint)

df = pd.DataFrame(dados)
st.dataframe(df)