import streamlit as st

class TelaBase:

    def cabecalho(self, titulo, descricao):
        st.title(titulo)
        st.caption(descricao)

    def rodape(self):
        st.divider()
        st.caption("Sistema de controle de Alunos")