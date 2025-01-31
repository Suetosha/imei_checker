import requests


def get_imei(check_id):
    retrieve_url = f"https://api.imeicheck.net/v1/checks/{check_id}"

    headers = {
        'Authorization': 'Bearer e4oEaZY1Kom5OXzybETkMlwjOCy3i8GSCGTHzWrhd4dc563b',
        'Accept-Language': 'en',
    }

    response = (requests.get(retrieve_url, headers=headers)).json()
    return response

