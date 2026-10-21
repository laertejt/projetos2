import json
from urllib.request import urlopen
from fastapi import HTTPException
from app.schemas import EnderecoIn


def consultar_cep(cep: str) -> EnderecoIn:
    # 1. Remove o hífen e verifica os 8 dígitos.
    cep = cep.strip().replace('-', '')
   # 2. Consulta o ViaCEP.
    url = f'https://viacep.com.br/ws/{cep}/json/'
    try:
        with urlopen(url, timeout=5) as resposta:
            dados = json.load(resposta)        # 3. Retorna os campos usados no cadastro do endereço.
        return EnderecoIn(
            cep=dados['cep'],
            endereco=dados.get('logradouro', ''),
            bairro=dados.get('bairro', ''),
            cidade=dados['localidade'],
            estado=dados['uf'],
            regiao=dados.get('regiao', ''),
        )
    except (OSError, ValueError, KeyError, AttributeError):
        raise HTTPException(status_code=502, detail='Não foi possível consultar o ViaCEP.')
