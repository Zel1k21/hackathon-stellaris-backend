import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
        )

        # Execute dbCreation.sql script
        cursor = connection.cursor()
        try:
            with open("internal/api/dbCreation.sql", "r") as file:
                sql_script = file.read()
                cursor.execute(sql_script)
                connection.commit()
        except Exception as e:
            print(f"Warning: Could not execute dbCreation.sql: {e}")
            connection.rollback()
        finally:
            cursor.close()

        return connection
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        raise


def get_db():
    """Get database connection for repository use"""
    return get_db_connection()
