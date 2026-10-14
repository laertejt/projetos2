import streamlit as st
from connection.base_api import BaseApi
import pandas as pd
from components.base_tela import TelaBase


class EnderecoTela(TelaBase):
    def __init__(self):
        self.base = BaseApi()
        self.titulo = "Tela de Endereco"
        self.descricao = "Essa tela é usada para consulta de enderecos"

    def consultar(self, id):
        endpoint = f"/alunos/pegar-dados-aluno-por-id/{id}"
        dados = self.base.get(endpoint)
        return dados
    
    def criar_dataframe(self, dados):
        df = pd.DataFrame(dados)
        st.dataframe(df)

    def renderizar(self):
        super().cabecalho(self.titulo, self.descricao)
        
        super().rodape()


EnderecoTela().renderizar()