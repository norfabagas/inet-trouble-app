from flask import session
from .helper import get_current_unix_time, get_first_name

def generate_auth_session(
        authorized_status: bool,
        expiry: int,
        regular_user: bool,
        name: str,
        token: str):
    session[token] = {
        'authorized': authorized_status,
        'exp': expiry,
        'regular_user': regular_user,
        'name': name,
        'first_name': get_first_name(name),
        'token': token
    }

def is_session_valid(token: str) -> bool:
    if session.get(token):
        if session.get(token)['exp'] >= get_current_unix_time():
            return True
        else:
            session.pop(token)
            return False
    else:
        return False