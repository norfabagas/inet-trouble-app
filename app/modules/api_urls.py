import os

def api_urls(key: str) -> str:
    # split urls
    base_url = os.getenv("API_URL")
    api = "/api"
    v1 = "/v1"
    private = "/private"
    users = "/users"
    login = "/login"
    internet_troubles = "/internet_troubles"
    get_troubles = "/get_troubles"
    show_trouble = "/show_trouble"

    # combined urls
    v1_private = base_url + api + v1 + private
    v1_public = base_url + api + v1

    if key == "post_v1_private_users":
        return v1_private + users
    elif key == "post_v1_private_users_login":
        return v1_private + users + login
    elif key == "get_v1_private_internet_troubles_index":
        return v1_private + internet_troubles
    elif key == "post_v1_internet_troubles":
        return v1_public + internet_troubles
    elif key == "post_v1_private_internet_troubles":
        return v1_private + internet_troubles
    elif key == "get_v1_private_get_troubles":
        return v1_private + get_troubles
    elif key == "get_v1_private_show_trouble":
        return v1_private + show_trouble
    elif key == "put_v1_private_internet_troubles":
        return v1_private + internet_troubles
    else:
        return ""