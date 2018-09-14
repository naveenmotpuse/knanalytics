

import argparse
import time
import json
import requests
import base64
import six
import struct

from base64 import urlsafe_b64decode
#from base64 import b64decode

import jwt

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
#from jwt.contrib.algorithms.py_ecdsa import ECAlgorithm

def base64_to_long(data):
    if isinstance(data, six.text_type):
        data = data.encode("ascii")

    # urlsafe_b64decode will happily convert b64encoded data
    _d = base64.urlsafe_b64decode(bytes(data) + b'==')
    return intarr2long(struct.unpack('%sB' % len(_d), _d))

def intarr2long(arr):
    return int(''.join(["%02x" % byte for byte in arr]), 16)

def get_jwks_json(token,jwks_url):    
    r = requests.get(jwks_url)
    if r.status_code == 200:
        return r.json()
    else:    
        return json.loads('{"keys":[{"alg":"RS512","e":"AQAB","n":"j6Dtct-hCbacNoaTWVskOLh7Fcj4snuQ2kY3ZIpOZfJP-fsBgj6dxUFiqZSKjHikk73xiVLAb6w2SqQ8Z2Ez5hpGmG0U3eZzWkm8gwrpN-DN3eSBjBzyE5UUSTxmfMXGIBZtlwGEmmameycvX8nCJLuF83nK7Q5OQd7MIWUw-_8","kty":"RSA","kid":"k106948190"},{"alg":"RS512","e":"AQAB","n":"iGkARaPALhHTQHIzPEGhD7LCNuXwDezMJfrsGDY7mH5m9JYjbTjxdHUJDEJI7bdnnlg2LFsS7SGO1sP9ZSuHoNURwt65QjLJwSodfJqTzNvGBZrBnLayXjvACLb1ZDDbEVwdoDnr36HF2HETxqRNzebsFLQmLDhJFHIMPofn4b8","kty":"RSA","kid":"k1400006126"},{"alg":"RS512","e":"AQAB","n":"nWenpCTpUgZHbF3Ev2B7MeohSa82T8cDmNSUoso_AfDwJcPAgDoULzKsvgDtqG-IQS8x6EhCpfoSsCQsnfFc2tnRmLoehCWSIms9NO3x3a8RT7YcAbxr6Mvj3cj60Tqf45mpQH8Bnd1QmJ_NRZ5iHaWbw-bt4JXmsi-Q7Gs98pk","kty":"RSA","kid":"k501833123"},{"alg":"RS512","e":"AQAB","n":"lAl1zoD3CG2R9JkLV3f57N63VE6w_RuFA6NAiVI8ht7KvGjWB0gVercLmPjU9dqKN7cxEiQxOOHyjN_0XC-4WLEjXA7kAtbyiFWZut7r027CsDKtL5rt4KRiYVk3uCRzkumst4hOc2SXVfpaZ9sF_LWGc8wRP5OHMnSQYJkXmCM","kty":"RSA","kid":"k1501383191"},{"alg":"RS512","e":"AQAB","n":"pledMj3s5h5atX1VIdOHnn7qnaXbkfUZ724ykxj3-ByZhvg8wE-BWc7_3aUzHvcdfImcQ_t96lW7x27zc2Q8YWB5BERpC2flkGs9BziVBQBhFAunnSMCC6opg97TwpvD9q7SmedG1jCoxgM9Xxd-rEemMZ9UJhgLipuMxSqPlGs","kty":"RSA","kid":"k1935801179"}]}')


def maybe_pad(s):
    return (s + '=' * (4 - len(s) % 4))    
    

def get_token_segments(token):   
    header, payload, signature = token.split(".")    
    header_json_str = urlsafe_b64decode(maybe_pad(header).encode('ascii'))
    payload_json_str = urlsafe_b64decode(maybe_pad(payload).encode('ascii'))
    signature_bytes = urlsafe_b64decode(maybe_pad(signature).encode('ascii'))
    header_json = json.loads(header_json_str, 'utf-8')
    payload_json = json.loads(payload_json_str, 'utf-8')
    return header_json, payload_json, signature_bytes
        
def get_matching_jwks(jwk_sets, kid, algorithm):
    #print("Looking for kid=%s algo=%s in the jwt key sets" % (kid, algorithm))
    for jwks in jwk_sets['keys']:
        if (jwks['kid'] == kid and jwks['alg'] == algorithm):
            return jwks


def get_EXP(token):
    payload_json = get_token_segments(token)[1]
    exp = payload_json['exp']
    print "Time now: %s" % (time.strftime('%Y-%m-%d %H:%M:%S',
                                          time.localtime(time.time())))
    print "Expires:  %s" % (time.strftime('%Y-%m-%d %H:%M:%S',
                                          time.localtime(exp)))
    return exp

def get_CLIENTID(token):
    payload_json = get_token_segments(token)[1]
    #print("check payload json " + str(payload_json) )
    clientId = payload_json['client_id']
    return clientId

def get_ALG(token):
    header_json = get_token_segments(token)[0]
    alg = header_json['alg']
    return alg


def get_KID(token):
    header_json = get_token_segments(token)[0]
    kid = header_json['kid']
    return kid

    
def validateToken(token,jwks_url):  
    k_stackTrace = {} 
    try:  
        #k_stackTrace['message'] = "validateToken Start-->>"
        kid = get_KID(token)
        #k_stackTrace['kid'] = str(kid)
        alg = get_ALG(token) 
        #k_stackTrace['alg'] = str(alg) 
        k_stackTrace['jwks_url'] = jwks_url
        jwk_sets = get_jwks_json(token,jwks_url)        
        jwk = get_matching_jwks(jwk_sets, kid, alg)
        #k_stackTrace['jwks_url'] = str(jwks_url) 
        #k_stackTrace['jwk'] = str(jwk)  
        exponent = base64_to_long(jwk['e'])
        #k_stackTrace['exponent'] = str(exponent)  
        modulus = base64_to_long(jwk['n'])    
        #k_stackTrace['modulus'] = str(modulus)  
        numbers = RSAPublicNumbers(exponent, modulus)          
        public_key = numbers.public_key(backend=default_backend())
        #k_stackTrace['public_key'] = str(public_key)
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )         
        secret = pem   
        #k_stackTrace['secret/pem'] = str(secret)   
        payload_decoded_and_verified = jwt.decode(token, secret, algorithms=[alg], verify=True)            
        k_stackTrace['payload_decoded_and_verified'] = payload_decoded_and_verified
        
        return k_stackTrace  
    except Exception, e: 
        k_stackTrace['exception'] =  str(e) 
        return k_stackTrace  
      

def main(token, jwks_url):
    print ("main method - ")
    retObj = validateToken(token,jwks_url)
    if retObj.get('payload_decoded_and_verified'):
        print ("verify successful.\npayload:\n%s\n" %
               (retObj['payload_decoded_and_verified']))
    else:
        print ("verify failed.\n%s\n" % (retObj['exception']))
          

if __name__ == "__main__":  
    parser = argparse.ArgumentParser()  
    parser.add_argument('--token', help='a JWT or JWS token.', required=True)
    args = parser.parse_args()
    print (args)
    main(args.token, args.jwks_url)
    
    
    
    
    



#end jwtvalidat







