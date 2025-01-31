import os
import sys
import threading
import subprocess
from backend.db.create_table import create_table

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLASK_PATH = os.path.join(BASE_DIR, "backend", "main.py")
BOT_PATH = os.path.join(BASE_DIR, "bot", "bot.py")

PYTHON_EXEC = sys.executable

def run_flask():
    subprocess.run([PYTHON_EXEC, FLASK_PATH])


def run_bot():
    subprocess.run([PYTHON_EXEC, BOT_PATH])


if __name__ == "__main__":

    create_table()

    flask_thread = threading.Thread(target=run_flask)
    bot_thread = threading.Thread(target=run_bot)

    flask_thread.start()
    bot_thread.start()

    flask_thread.join()
    bot_thread.join()