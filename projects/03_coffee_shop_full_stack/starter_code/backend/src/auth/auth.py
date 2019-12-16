import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'coffee-shop-raluca.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
method to get the auth token from the request header
it attempts to get the header from the request
it raises an AuthError if no header is present
it attempts to split bearer and the token
it raises an AuthError if the header is malformed
return the token part of the header
code based on Udacity class lecture on Authentication and Authorization
'''
def get_token_auth_header():
    
    if 'Authorization' not in request.headers:
        raise AuthError({
                'code': 'invalid_header',
                'description': 'No Authorization in header.'
            }, 401)

    auth_header = request.headers['Authorization']
    header_parts = auth_header.split(' ')

    if len(header_parts) != 2:
        raise AuthError({
                'code': 'invalid_header',
                'description': 'Authorization malformed.'
            }, 401)
    elif header_parts[0] != 'Bearer':
        raise AuthError({
                'code': 'invalid_header',
                'description': 'Authorization malformed.'
            }, 401)

    return header_parts[1]

'''
method to check if user has a given permission
@INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload
it raises an AuthError if permissions are not included in the payload
it raises an AuthError if the requested permission string is not in the payload permissions array
return true otherwise
code based on Udacity class lecture on Authentication and Authorization
'''
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
                'code': 'bad_request',
                'description': 'No permissions in payload.'
            }, 400)
    if permission not in payload['permissions']:
        raise AuthError({
                'code': 'forbidden',
                'description': 'User does not have required permission.'
            }, 403)

    return True

'''
method to verify and decode jwt
@INPUTS
        token: a json web token (string)
        it should be an Auth0 token with key id (kid)
method verifies the token using Auth0 /.well-known/jwks.json
it decodes the payload from the token
it validates the claims
return the decoded payload
code based on Udacity class lecture on Authentication and Authorization
'''
def verify_decode_jwt(token):
    # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # GET THE DATA IN THE TOKEN HEADER
    unverified_header = jwt.get_unverified_header(token)

    # CHOOSE OUR KEY
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    
    # verify token
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

'''
Decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
it uses the get_token_auth_header method to get the token
it uses the verify_decode_jwt method to decode the jwt
it uses the check_permissions method validate claims and check the requested permission
return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
                return f(payload, *args, **kwargs)
            except AuthError as e:
                print(e.error)
                abort(e.status_code)

        return wrapper
    return requires_auth_decorator
