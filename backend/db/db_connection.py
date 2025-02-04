import os
import sqlite3

script_dir = os.path.abspath(os.path.dirname(__file__))
database_file = os.path.join(script_dir, "users")

def get_db_connection():
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row
    return conn
