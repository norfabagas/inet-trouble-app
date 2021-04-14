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

    # combined urls
    v1_private = base_url + api + v1 + private

    if key == "post_v1_private_users":
        return v1_private + users
    elif key == "post_v1_private_users_login":
        return v1_private + users + login
    elif key == "get_v1_private_internet_troubles_index":
        return v1_private + internet_troubles
    else:
        return ""