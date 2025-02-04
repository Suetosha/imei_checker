import enum
import json
import os
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, request, jsonify, session

from backend.services.create_imei import create_imei
from backend.services.get_imei import get_imei
from backend.services.generate_response import generate_response
from db.db_connection import get_db_connection
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt

load_dotenv()
app = Flask(__name__)

jwt = JWTManager(app)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
IMEI_CHECK_PAIR = {}



class Statuses(enum.Enum):
    waiting = 'waiting'
    processing = 'processing'
    successful = 'successful'
    unsuccessful = 'unsuccessful'
    failed = 'failed'


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username = ?", (username,))

    if cur.fetchone():
        conn.close()
        return f"Пользователь {username} Уже существует"

    cur.execute(f"INSERT INTO users (username, password) VALUES (?,?)", (username, password))
    conn.commit()
    conn.close()

    return "Регистрация завершена успешно"


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE username=?", (username,))
    user = cur.fetchone()
    conn.close()

    if not user or not password == user['password']:
        return "Неверно введен логин или пароль"

    access_token = create_access_token(identity=username)
    session["jwt"] = access_token
    return jsonify(access_token=access_token)


@app.route('/logout', methods=['POST'])
@jwt_required
def logout():
    session.pop("jwt")
    return jsonify({'message': 'Вы вышли из системы'}), 200


def is_telegram_request():
    return request.headers.get('X-Telegram-Bot') == 'True'


def jwt_required_for_api(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if is_telegram_request():
            return func(*args, **kwargs)
        else:
            return jwt_required()(func)(*args, **kwargs)
    return wrapper


@app.route('/api/check-imei', methods=['POST'])
@jwt_required_for_api
def check_imei():
    data = request.get_json()
    imei = data.get("imei")
    token = data.get("token")

    if imei not in IMEI_CHECK_PAIR:
        response = create_imei(token, imei)

        check_id = response.get('id', None)
        status = response.get('status', None)
        IMEI_CHECK_PAIR[imei] = check_id

        if status == Statuses.failed or status is None:
            del IMEI_CHECK_PAIR[imei]
            data = generate_response(error="Что-то пошло не так, попробуйте загрузить ваш imei ещё раз")
            return json.dumps(data, ensure_ascii=False)

        elif status in [Statuses.successful, Statuses.unsuccessful]:
            payload = {
                    "imei": imei,
                    "status": status,
                }
            data = generate_response(message="Создание проверки прошло успешно", payload=payload)
            return json.dumps(data, ensure_ascii=False)

    response = get_imei(IMEI_CHECK_PAIR[imei], token)
    status = response['status']

    if status in [Statuses.waiting, Statuses.processing]:

        payload = {
            "imei": imei,
            "status": status,
        }

        data = generate_response(
            error="Ваш imei находится на этапе обработки, отправьте повторно через несколько минут",
            payload=payload
        )
        return json.dumps(data, ensure_ascii=False)

    payload = {
        "imei": imei,
        "status": status,
    }

    data = generate_response(message="Получение проверки прошло успешно", payload=payload)
    return json.dumps(data, ensure_ascii=False)


if __name__ == '__main__':
    app.run(debug=True)
