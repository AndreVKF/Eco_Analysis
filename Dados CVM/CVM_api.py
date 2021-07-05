import requests
import base64
import json

requests.get("https://api.anbima.com.br/feed/fundos/v1/fundos")

ClientID = '2Xy1ey11UDZA'
ClientSecret = 'faStF1Hcd5gt'

codeString = ClientID + ":" + ClientSecret

codeStringBytes = codeString.encode('ascii')
base64CodeBytes = base64.b64encode(codeStringBytes)
base64CodeString = base64CodeBytes.decode('ascii')

url = "https://api.anbima.com.br/oauth/access-token"
headers = {
    'content-type': 'application/json'
    ,'authorization': f'Basic {base64CodeString}'
}
body = {
    "grant_type": "client_credentials"
}
r = requests.post(url=url, data=json.dumps(body), headers=headers, allow_redirects=True)
jsonDict = r.json()

##################
token = jsonDict['access_token']
headers2 = {
    'content-type': 'application/json'
    ,'client_id': ClientID
    ,'access_token': token
}

urlFundos = "https://api-sandbox.anbima.com.br/feed/fundos/v1/fundos"

r2 = requests.get(url=urlFundos, headers=headers2)
r2.status_code
r2.json()

# {'codigo_fundo': '126251',
#    'nome_fantasia': 'DAYCOVAL MULTIFUNDS FIQFI MULTIMERCADO',
#    'cnpj_fundo': '06092123000186',
#    'classe_anbima': 'Multimercados',
#    'situacao_atual': 'A',
#    'data_inicio_divulgacao_cota': '2004-02-18',
#    'data_atualizacao': '2018-04-19T18:40:00'},

codigoFundo = 546353
urlFundo = f"https://api-sandbox.anbima.com.br/feed/fundos/v1/fundos/{codigoFundo}/serie-historica?data-inicio=2021-06-28&data-fim=2021-06-28"

r3 = requests.get(url=urlFundo, headers=headers2)
r3.status_code
r3.text