import re


def validate_imei(imei):
    if re.fullmatch(r"\d{15}", imei):
        return True
    return False
