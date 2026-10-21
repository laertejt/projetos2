# Guia de Configuração e Execução do Projeto (FastAPI + SQLAlchemy + Alembic)

Guia completo para configurar e montar o banco de dados, como também utilizar e testar os comandos do CRUD na prática com o FastAPI e SQLAlchemy

## Cadastro com CEP e situação acadêmica

### Roteiro para a aula

Leia os arquivos nesta ordem:

1. `app/routers/alunos.py`: recebe a requisição e chama o service.
2. `app/services/aluno_service.py`: consulta o CEP e cadastra o aluno.
3. `app/services/cep_service.py`: busca o endereço no ViaCEP.
4. `app/models.py`: mostra as classes que representam as tabelas do banco.

No cadastro, acompanhe os comentários numerados de `criar_com_cep`:

```text
Consultar ViaCEP
          ↓
Procurar endereço no banco
          ↓
Criar endereço, se necessário
          ↓
Criar aluno
          ↓
Salvar tudo com commit()
```

Comandos usados no ORM:

- `select(...)`: monta uma consulta.
- `db.scalar(...)`: executa a consulta e pega um resultado.
- `db.add(...)`: prepara um objeto para cadastro.
- `db.flush()`: envia o cadastro ao banco para obter o ID, sem confirmar.
- `db.commit()`: confirma as alterações.
- `db.rollback()`: desfaz as alterações ainda não confirmadas.

Em `situacao_academica`, a regra usa `sum(notas) / len(notas)` para calcular
a média e `if/else` para decidir entre aprovado, reprovado e sem notas.

As rotas de alunos seguem o fluxo `router → aluno_service → SQLAlchemy ORM → PostgreSQL`.
O `aluno_service` consulta o ViaCEP por meio de `cep_service`.

Antes de usar os endpoints, execute na pasta `backend`:

```bash
uv run alembic upgrade head
```

A migration `a7c29e314b80` cria um índice único em `lower(trim(email))`.
Matrícula e CEP já possuem restrições de unicidade. Se houver emails duplicados
na base atual, a migration falhará sem remover registros. Localize os grupos
com a consulta abaixo e corrija os cadastros antes de tentar novamente:

```sql
SELECT lower(trim(email)) AS email_normalizado, count(*)
FROM tb_alunos
GROUP BY lower(trim(email))
HAVING count(*) > 1;
```

### POST /alunos/criar-com-cep

```json
{
  "matricula": "2026001",
  "nome_aluno": "Ana Silva",
  "email": "ana@example.com",
  "cep": "01001-000"
}
```

Aceita CEP com ou sem hífen. Consulta o ViaCEP com timeout de 5 segundos,
reutiliza um endereço pelo CEP ou cria um novo e cadastra o aluno. Endereço e
aluno são persistidos na mesma transação. O endereço representa os dados do
CEP, sem número ou complemento individual do aluno.

Resposta `201`:

```json
{
  "id": 1,
  "matricula": "2026001",
  "nome_aluno": "Ana Silva",
  "email": "ana@example.com",
  "endereco_id": 1
}
```

Erros: `422` para entrada inválida;
`404` para CEP não encontrado; `502` para falha de consulta ao ViaCEP,
incluindo timeout e resposta inválida. Email é salvo em minúsculas, sem espaços nas extremidades.
Matrícula, email e CEP continuam protegidos pelas restrições do banco.
Nesta versão didática, erros de integridade não são tratados pelo service;
conflitos retornam erro interno (500), sem mensagem personalizada.
A sessão é fechada por `get_db()` ao final da requisição, desfazendo alterações
não confirmadas em caso de falha.

Contrato do provedor: https://viacep.com.br/

### GET /alunos/{id}/situacao-academica

Calcula a média simples de todas as notas lançadas para o aluno. Não há pesos
por disciplina. Média maior ou igual a 7 resulta em `aprovado`; abaixo de 7,
`reprovado`. Sem notas, retorna `media: null` e `situacao: "sem_notas"`.
Aluno inexistente retorna `404`.

```json
{
  "aluno_id": 1,
  "matricula": "2026001",
  "nome_aluno": "Ana Silva",
  "total_notas": 2,
  "media": 7.5,
  "situacao": "aprovado"
}
```

A situação é calculada antes do arredondamento da média exibida para duas casas.
Por exemplo, média exata de 6,995 retorna `media: 7.0` e `situacao: "reprovado"`.

### Testes

Na pasta `backend`, execute:

```bash
uv run python -m unittest discover -s tests -v
```

Os testes usam SQLite em memória, ViaCEP simulado e compilação da migration
para PostgreSQL. Não acessam bancos configurados nem fazem consultas externas.
O módulo `database.py` também configura MySQL na importação; para executar a
aplicação e o Alembic, mantenha as variáveis `MYSQL_USER`, `MYSQL_PASSWORD`,
`MYSQL_HOST` e `MYSQL_DATABASE` exigidas pela configuração atual.

## Upload de notas por CSV

Envie o arquivo para `POST /notas/upload-csv`, no campo `arquivo` do formulário.
No Swagger (`/docs`), abra a rota, clique em **Try it out** e selecione o CSV.

Formato: UTF-8, separado por vírgulas e com ponto nas casas decimais.
Os IDs devem corresponder a alunos e disciplinas já cadastrados.

```csv
aluno_id,disciplina_id,nota
1,1,8.5
1,2,7.0
2,1,9.0
```

Arquivo de exemplo: `exemplos/notas.csv`.
Cada linha cria uma nota; enviar novamente cadastra novas linhas.
A rota lê o CSV, adiciona os objetos `Nota` e executa um único `commit()`.
Não há validações adicionais nem tratamento personalizado de erros.

```bash
curl -X POST http://localhost:8000/notas/upload-csv \
  -F "arquivo=@exemplos/notas.csv"
```

O upload usa `python-multipart`, incluído nas dependências do projeto,
conforme a [documentação do FastAPI](https://fastapi.tiangolo.com/tutorial/request-files/).



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
