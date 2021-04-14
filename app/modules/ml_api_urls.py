import os

def ml_api_urls(key: str) -> str:
    base_url = os.getenv('ML_API_URL')
    classify = "/classify"

    if key == "get_classify":
        return base_url + classify
    else:
        return ""