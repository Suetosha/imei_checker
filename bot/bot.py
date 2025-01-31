import asyncio
import os
from aiogram import Dispatcher, Bot
from dotenv import load_dotenv

import handlers

load_dotenv()


async def main() -> None:
    token = os.getenv('TOKEN')

    bot = Bot(token=token)
    dp = Dispatcher()

    dp.include_router(handlers.router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
