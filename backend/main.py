import enum

from dotenv import load_dotenv
from flask import Flask, request, jsonify

from backend.services.create_imei import create_imei
from backend.services.get_imei import get_imei
from backend.services.generate_response import generate_response
from db.db_connection import get_db_connection
from flask_jwt_extended import create_access_token, jwt_required, JWTManager



load_dotenv()
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)

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
    return jsonify(access_token=access_token)


@app.route('/api/check-imei', methods=['POST'])
@jwt_required()
def check_imei():
    data = request.get_json()
    imei = data.get("imei")
    token = data.get("token")

    if imei not in IMEI_CHECK_PAIR:
        response = create_imei(token, imei)

        check_id = response['id']
        status = response['status']
        IMEI_CHECK_PAIR[imei] = check_id

        if status == Statuses.failed:
            del IMEI_CHECK_PAIR[imei]
            data = generate_response(error="Что-то пошло не так, попробуйте загрузить ваш imei ещё раз")
            return jsonify(data)

        elif status in [Statuses.successful, Statuses.unsuccessful]:
            payload = {
                    "imei": imei,
                    "status": status,
                }
            data = generate_response(message="Создание проверки прошло успешно", payload=payload)
            return jsonify(data)

    response = get_imei(IMEI_CHECK_PAIR[imei])
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
        return jsonify(data)


    elif status == Statuses.failed:
        del IMEI_CHECK_PAIR[imei]

        payload = {
            "imei": imei,
            "status": status
        }

        data = generate_response(
            error="Что-то пошло не так, попробуйте загрузить ваш imei ещё раз",
            payload=payload
        )

        return jsonify(data)

    payload = {
        "imei": imei,
        "status": status,
    }

    data = generate_response(message="Получение проверки прошло успешно", payload=payload)
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
