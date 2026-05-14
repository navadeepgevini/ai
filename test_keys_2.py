import urllib.request
import urllib.error
import string
import itertools

base_key = 'AIzaSyA2bfN_DZPkJy4RhDeGO431pTTnRbfddPI'

keys_to_try = [
    'AIzaSyA2bfN_DZPkJy4RhDeGO43IpTTnRbfddPI',
    'AIzaSyA2bfN_DZPkJy4RhDeG043IpTTnRbfddPI',
    'AIzaSyA2bfN_0ZPkJy4RhDeGO431pTTnRbfddPI',
    'AIzaSyA2bfN_DZPkJy4RhDeGQ431pTTnRbfddPI',
    'AIzaSyA2bfN_DZPkJy4RhDeG0431pTTnRbfddP1',
    'AIzaSyA2bfN_DZPkJy4RhDeGO431pTTnRbfddP1',
    'AIzaSyA2bfN_DZPkJv4RhDeGO431pTTnRbfddPI',
    'AIzaSyA2bfN_DZPkJy4RhDeGO4B1pTTnRbfddPI',
    'AIzaSyA2bfN_DZPkJy4RhDeG04B1pTTnRbfddPI',
    'AIzaSyA2bfN_DZPkJy4RbDeGO431pTTnRbfddPI',
    'AIzaSyA2btN_DZPkJy4RhDeGO431pTTnRbfddPI',
    'AIzaSyA2btN_DZPkJy4RhDeG0431pTTnRbfddPI',
    'AIzaSyA2bfN_DZPhJy4RhDeGO431pTTnRbfddPI',
]

for k in keys_to_try:
    try:
        req = urllib.request.Request(f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={k}', data=b'{}', headers={'Content-Type': 'application/json'})
        resp = urllib.request.urlopen(req)
        print(f"{k} : VALID")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if 'API_KEY_INVALID' in body:
            print(f"{k} : INVALID")
        else:
            print(f"{k} : OTHER_ERROR ({body})")
