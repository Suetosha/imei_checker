import json

def generate_response(error='', message='', payload=None):

    if payload is None:
        payload = {}

    data = {
        "error": error,
        "message": message,
        "payload": payload
    }

    return data
