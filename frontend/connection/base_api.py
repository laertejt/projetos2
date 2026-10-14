import requests

url = "http://127.0.0.1:8000"

class BaseApi:

    def get(self, endpoint, params=None):
        response = requests.get(f"{url}{endpoint}", params=params)
        dados = response.json()
        return dados
    
    def post(self, endpoint, params=None):
        response = requests.post(f"{url}{endpoint}", json=params)
        return response