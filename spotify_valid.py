import time,requests,json
def valid_access_token(tokens):
    expiry = tokens.get('expiry')
    if time.time() > expiry:
        response = requests.post('https://musync-k60r.onrender.com/spotify/refresh',params={'refresh_token': tokens.get('refresh_token')})
        if response.status_code == 200:
            tokens = response.json()
            return tokens
