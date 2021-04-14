from flask import session, request

def bearer_token(token: str) -> str:
    token = session.get(request.cookies.get('auth'))['token']

    print(token)
    return "Bearer " + token

def authorization_header(token: str) -> dict:
    headers = {
        'Authorization': bearer_token(token)
    }

    return headers

def generate_authorization_header() -> dict:
    return authorization_header(bearer_token)
