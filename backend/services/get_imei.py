import requests



def get_imei(check_id, token):
    retrieve_url = f"https://api.imeicheck.net/v1/checks/{check_id}"

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept-Language': 'en',
    }

    response = (requests.get(retrieve_url, headers=headers)).json()
    return response

