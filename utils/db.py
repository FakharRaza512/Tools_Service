# db/db_connection.py

import psycopg2


def get_connection():
    return psycopg2.connect(
        database="naas",
        user="postgres",
        password="1234",
        host="127.0.0.1",
        port="5432"
    )
