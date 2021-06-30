import base64
import requests

API_KEY = 'nqzum2aq44amvq8g8b8wbqx4'
SECRET_KEY = '2FgCD9uN8b'
TOKEN_ENDPOINT = 'https://api.manheim.com/oauth2/token.oauth2'

header = ""
token = ""
def get_encoded_header():
    authorization_string = API_KEY + ":" + SECRET_KEY
    authorization_string_bytes = authorization_string.encode("ascii")

    authorization_header_encoded = base64.b64encode(authorization_string_bytes)
    return authorization_header_encoded.decode('ascii')


def get_access_token(authorization_header_encoded):
    r = requests.post(TOKEN_ENDPOINT,
                      headers={'Authorization': 'Basic ' + authorization_header_encoded,
                               'content-type': 'application/x-www-form-urlencoded'},
                      data={'grant_type': 'client_credentials'})
    #token = r.json()['access_token']
    
    return r.json()


def has_token_expires(token):
    r = requests.get('https://api.manheim.com/oauth2/token/status',
                     headers={'Authorization': f'{token["token_type"]} {token["access_token"]}'})
    if r.status_code == 200:
        return False
    else:
        return True


def get_data(token):
    r = requests.get('https://api.manheim.com/valuations/vin/1VWAH7A34DC146014?include=retail,historical,forecast',
                      headers={'Authorization': f'{token["token_type"]} {token["access_token"]}'})
    
    print(r.json())

header = get_encoded_header()
token = get_access_token(header)
get_data(token)
#print(has_token_expires(token))



#token = {'token_type': 'Bearer', 'access_token': 'tdvmtdz436rb6tm7evaajvpw'}
#if has_token_expires(token):
#    print("Token expired. Generating new one")
#    header = get_encoded_header()
#    token = get_access_token(header)

#print("Token", token)
#get_data(token)
