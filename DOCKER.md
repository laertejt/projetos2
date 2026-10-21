# Produção com Docker Compose

Com Docker e Docker Compose instalados, configure a senha do banco e inicie os serviços:

```bash
cp .env.example .env
```

Edite `DB_PASSWORD` no `.env`. Use apenas letras e números porque o backend monta a URL do banco diretamente com esse valor.

```bash
docker compose up -d --build
```

Frontend: http://localhost:8501  
API: http://localhost:8000/docs

```bash
docker compose logs -f
```

Para parar os serviços:

```bash
docker compose down
```

O banco usa o volume persistente `dados_postgres`. `docker compose down -v` também apaga esse volume e os dados.

## Testar localmente no Dev Container

Instale a extensão **Dev Containers** do VS Code e use **Dev Containers: Reopen in Container**. O ambiente constrói as mesmas imagens, inicia banco, API e interface, e monta o código para refletir alterações. As credenciais do banco são locais e não são usadas na configuração de produção.

Portas encaminhadas: Streamlit em http://localhost:8501 e API em http://localhost:8000/docs. Ao fechar o Dev Container, os serviços param; o volume `dados_devcontainer` mantém os dados locais.
