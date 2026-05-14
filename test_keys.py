import urllib.request
import urllib.error

keys = [
    'AIzaSyA2bfN_DZPkJy4RhDeGO431pTTnRbfddPI',
    'AIzaSyA2bfN_DZPkJy4RhDeG0431pTTnRbfddPI',
    'AIzaSyA2bfN_DZPkJy4RhDeGO431pTTnRbfddPl',
    'AIzaSyA2bfN_DZPkJy4RhDeG0431pTTnRbfddPl',
    'AIzaSyA2bfN-DZPkJy4RhDeGO431pTTnRbfddPI',
    'AIzaSyA2btN_DZPkJy4RhDeGO431pTTnRbfddPI',
    'AlzaSyA2bfN_DZPkJy4RhDeGO431pTTnRbfddPI',
    'AIzaSyA2bfN_DZPkjy4RhDeGO431pTTnRbfddPI',
    'AIzaSyA2bfN_DZPkJyA4RhDeGO431pTTnRbfddPI',
    'AIzaSyAZbfN_DZPkJy4RhDeGO431pTTnRbfddPI',
    'AIzaSyA2bfN_DZPkJy4Rh0eGO431pTTnRbfddPI',
    'AIzaSyA2bfN_DZPkJy4RhDeGO43lpTTnRbfddPI',
]

for k in keys:
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
