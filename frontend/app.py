import sys
from pathlib import Path
import streamlit as st
# configuracao do diretorio onde o app.py do streamlit esta sendo executado
BASE_DIR = Path(__file__).parent
sys.path.append(BASE_DIR)
# Configura as paginas que estao no menu lateral
pagina_aluno = st.Page("menus/pagina_aluno.py", title="Pagina de Alunos", icon=":material/school:")
pagina_endereco = st.Page("menus/pagina_endereco.py", title="Pagina de Enderecos")
pagina_nota = st.Page("menus/pagina_nota.py", title="Pagina de Notas")
# cria o menu lateral do frontend
menus = {
    "Aluno": [pagina_aluno],
    "Endereço": [pagina_endereco],
    "Notas": [pagina_nota],
}
pg = st.navigation(menus)
# Executa o app.py
pg.run()