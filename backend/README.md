# Guia de Configuração e Execução do Projeto (FastAPI + SQLAlchemy + Alembic)

Guia completo para configurar e montar o banco de dados, como também utilizar e testar os comandos do CRUD na prática com o FastAPI e SQLAlchemy



## 1. Clonar e Preparar o Ambiente

Após clonar o repositório na máquina, execute os seguintes comandos para configurar o ambiente virtual em que o projeto rodará:

```bash
# 1. Cria o ambiente virtual
uv venv --python 3.14

# 2. Sincroniza e instala todas as dependências do projeto
uv sync
```


## 2. Configuração das Variáveis de Ambiente (`.env`)

Na raiz do projeto, crie um arquivo chamado  `.env` e o preencha com as credenciais do PostgreSQL da sua máquina:

```env
user=postgres
senha=sua_senha_do_postgres
host=localhost
porta=5432
banco=nome_do_banco_de_dados
```
*(Nota: Não coloque aspas ao redor dos valores e nem espaços antes ou depois do sinal de igual).*



## 3. Remontar o Banco de Dados (Alembic)

Antes de rodar as migrações, **você precisa abrir o PostgreSQL (via pgAdmin ou DBeaver) e criar um banco de dados vazio** com o mesmo nome que você colocou na variável `banco` no `.env`.

Basta abrir o PostgreSQL, clicar com o botão direito no ícone dele na aba de `Conexões`, clicar em `Criar`, logo em seguida, em `Banco de Dados` e colocar o nome do seu banco de dados definido no `.env`

Com o banco vazio criado, use o Alembic para reconstruir todas as tabelas (Endereços, Alunos, Disciplinas e Notas). Como o projeto já possui a pasta `alembic/versions` com o histórico, você só precisa executar o comando final de atualização:

```bash
alembic upgrade head
```
Em caso de as 'versions' estarem indisponíveis, rode esses comandos em ordem para cria-las do zero e assim seguir com a reconstrução das tabelas do seu banco de dados

```bash
alembic revision --autogenerate -m "mensagem"
alembic upgrade head
```


## 4. Rodar o Servidor (Uvicorn)

Para iniciar o servidor, execute no terminal:

```bash
uvicorn app.main:app --reload
```

Ele prinará uma URL, é nela que o projeto estará rodando, é nela que as rotas devem ser inseridas para interagir com o banco de dados



## 5. Populando o Banco de Dados (Postman)

Para inserir os dados corretamente, deve-se seguir a ordem das tabelas, pois elas são tabelas relacionais, então sempre deve seguir a ordem de dependência das Foreign Keys.

Siga a ordem abaixo para realizar os `POST` requests.

### Passo 1: Criar Endereço
* **Rota:** `POST http://127.0.0.1:8000/enderecos/criar-endereco`

**Exemplo de inserção de dados:**
```json
{
  "cep": "70000-000",
  "endereco": "Rua das Flores, 123",
  "bairro": "Centro",
  "cidade": "Brasília",
  "estado": "DF",
  "regiao": "Centro-Oeste"
}
```
*É sempre importante se atentar aos valores gerados no banco de dados, como o ID, pois os mesmos podem ser necessários para a população de outras tabelas*.

### Passo 2: Criar Aluno
* **Rota:** `POST http://127.0.0.1:8000/alunos/criar-aluno`

**Exemplo de inserção de dados:**
```json
{
  "matricula": "202612345",
  "nome_aluno": "João Silva",
  "email": "joao@email.com",
  "endereco_id": 1
}
```
*(O `endereco_id` deve ser o ID gerado no Passo 1)*.

### Passo 3: Criar Disciplina
* **Rota:** `POST http://127.0.0.1:8000/disciplinas/criar-disciplina`

**Exemplo de inserção de dados:**
```json
{
  "nome_disciplina": "Cálculo Multivariável",
  "carga": 60,
  "semestre": 3
}
```

### Passo 4: Criar Nota
* **Rota:** `POST http://127.0.0.1:8000/notas/criar-nota`

**Exemplo de inserção de dados:**
```json
{
  "aluno_id": 1,
  "disciplina_id": 1,
  "nota": 9.5
}
```
*(Os IDs devem corresponder ao aluno criado no Passo 2 e à disciplina criada no Passo 3)*.



## 6. Lista das Rotas

Para a utilização do CRUD via Postman, as seguintes rotas foram mapeadas, a inserção, remoção e atualização dos dados, para cada tabela, devem ser feitas via as rotas abaixo, foi também especificado o método para cada uma para a fácil execução do CRUD em diferentes tabelas

**Endereços (`/enderecos`)**:
* `GET /enderecos/pegar-dados-endereco`
* `POST /enderecos/criar-endereco`
* `PUT /enderecos/atualizar-endereco/{id}`
* `DELETE /enderecos/deletar-endereco/{id}`

**Alunos (`/alunos`)**:
* `GET /alunos/pegar-dados-alunos`
* `GET /alunos/pegar-dados-alunos-por-id/{id}`
* `POST /alunos/criar-aluno`
* `PUT /alunos/atualizar-aluno/{id}`
* `DELETE /alunos/deletar-aluno/{id}`

**Disciplinas (`/disciplinas`)**:
* `GET /disciplinas/pegar-dados-disciplina`
* `POST /disciplinas/criar-disciplina`
* `PUT /disciplinas/atualizar-disciplina/{id}`
* `DELETE /disciplinas/deletar-disciplina/{id}`

**Notas (`/notas`)**:
* `GET /notas/pegar-dados-nota`
* `POST /notas/criar-nota`
* `PUT /notas/atualizar-nota/{id}`
* `DELETE /notas/deletar-nota/{id}`
