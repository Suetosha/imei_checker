import json

import requests


def create_imei(token, imei):
    create_url = f'https://api.imeicheck.net/v1/checks'

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"

    }

    body = json.dumps({
        "deviceId": f"{imei}",
        "serviceId": "15"
    })

    response = (requests.post(create_url, headers=headers, data=body)).json()
    return response


