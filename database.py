from peewee import *
import os
from dotenv import load_dotenv

load_dotenv()

def get_database():
    return PostgresqlDatabase(
        os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PSW'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )