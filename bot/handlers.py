import json
import os

import requests

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from dotenv import load_dotenv

from validation import validate_imei

load_dotenv()
router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer('Здравствуйте!\nДля получения информации отправьте ваш IMEI')


@router.message()
async def process_message(message: Message):
    imei = message.text

    if validate_imei(imei):
        url = 'http://127.0.0.1:5000/api/check-imei'

        header = {
            'Content-Type': 'application/json',
            'X-Telegram-Bot': 'True'
        }

        body = json.dumps({
            'imei': imei,
            'token': os.getenv('SANDBOX_TOKEN')
        })

        response = requests.post(url, headers=header, data=body)


        await message.answer(response.text)

    else:
        await message.answer('У imei должно быть 15 цифр')