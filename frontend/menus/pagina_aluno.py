import streamlit as st
from connection.base_api import BaseApi
import pandas as pd
from components.base_tela import TelaBase

class AlunoTela(TelaBase):

    def __init__(self):
        self.base = BaseApi()
        self.titulo = "Tela de aluno"
        self.descricao = "Essa tela é usada para consulta de alunos"

    def consultar(self):
        endpoint = "/alunos/pegar-dados-aluno"
        dados = self.base.get(endpoint)
        return dados
    
    def consultar_por_id(self, id):
        endpoint = f"/alunos/pegar-dados-aluno-por-id/{id}"
        dados = self.base.get(endpoint)
        return dados
    
    def criar(self, params):
        endpoint = f"/alunos/criar-aluno"
        return self.base.post(endpoint, params)
    
    def criar_dataframe(self, dados):
        df = pd.DataFrame(dados)
        st.dataframe(df)

    def renderizar(self):
        super().cabecalho(self.titulo, self.descricao)
        abas = st.tabs(["Consultar", "Consultar por ID", "Criar", "Atualizar", "Excluir"])
        with abas[0]:
            dados = self.consultar()
            self.criar_dataframe(dados)
        with abas[1]:
            id = st.text_input("Digite o ID")
            if id:
                id = int(id)
                dados = self.consultar_por_id(id)
                self.criar_dataframe(dados)
        with abas[2]:
            matricula = st.text_input("Digite a Matricula")
            nome_aluno = st.text_input("Digite o Nome")
            email = st.text_input("Digite o Email")
            endereco_id = st.text_input("Digite o ID do endereco")
            params = {
                "matricula": matricula,
                "nome_aluno": nome_aluno,
                "email": email,
                "endereco_id": endereco_id
            }
            retorno = self.criar(params)
            st.success(retorno)
        with abas[3]:
            pass
        with abas[4]:
            pass
        super().rodape()

AlunoTela().renderizar()