import os

def validate_bearer(auth_header: str):
    if not auth_header:
        return False
    token = auth_header.split(' ')[1] if ' ' in auth_header else None
    return token == os.getenv('BEARER_TOKEN')