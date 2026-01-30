#!/usr/bin/env python3
import time
import hmac
import hashlib
import requests

API_KEY = "465edd938a57d272184fcdd8c4cbdd20"
API_SECRET = "3dda9877d956de7bfa41aa65db4a60205b5abdca33c4aeea1d9a450782d543f3"

def gen_sign(method, url, query_string='', payload_string=''):
    t = str(int(time.time()))
    m = hashlib.sha512()
    m.update((payload_string or '').encode('utf-8'))
    hashed_payload = m.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string, hashed_payload, t)
    sign = hmac.new(API_SECRET.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': API_KEY, 'Timestamp': t, 'SIGN': sign}

url = 'https://api.gateio.ws'
prefix = '/api/v4'
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

query_param = ''
body_param = ''
sign_headers = gen_sign('GET', prefix + '/spot/accounts', query_param, body_param)
headers.update(sign_headers)

r = requests.request('GET', url + prefix + '/spot/accounts', headers=headers)
print(r.status_code)
print(r.json())
