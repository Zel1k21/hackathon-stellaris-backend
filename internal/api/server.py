from flask import Flask, g
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
        )
    return g.db


app = Flask(__name__)


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
