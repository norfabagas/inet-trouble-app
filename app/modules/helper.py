import time

def is_duplicate(first_var, second_var):
    if first_var == second_var:
        return True
    else:
        return False

def get_current_unix_time():
    return int(time.time())

def hour_to_second(hour: int) -> int:
    return hour * 60 * 60

def get_request_header():
    return {
        "Content-Type": "application/json"
    }

def validates_null_in_dict(dict: dict) -> bool:
    if "" in dict:
        return False
    else:
        return True

def transform_error_message(error: dict) -> str:
    error_key = list(error)[0].capitalize()
    error_val = list(error.values())[0][0]

    return error_key.capitalize() + " : " + error_val

def get_first_name(name: str) -> str:
    return name.split()[0]