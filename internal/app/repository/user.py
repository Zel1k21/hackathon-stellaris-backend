from internal.api.database import get_db_connection
from internal.models.user import User


class UserRepository:
    @staticmethod
    def Create(user: User):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, password, is_moderator) VALUES (%s, %s, %s) RETURNING id",
                (user.name, user.password, user.is_moderator),
            )
            user_id = cursor.fetchone()[0]
            conn.commit()
            return user_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def GetUserByID(user_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,),
            )
            result = cursor.fetchone()
            if result:
                return {
                    "id": result[0],
                    "name": result[1],
                    "password": result[2],
                    "is_moderator": result[3],
                }
            return None
        except Exception as e:
            raise e
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def Authenticate(username: str, password: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM users WHERE name = %s AND password = %s",
                (username, password),
            )
            result = cursor.fetchone()
            if result:
                return {
                    "id": result[0],
                    "name": result[1],
                    "password": result[2],
                    "is_moderator": result[3],
                }
            return None
        except Exception as e:
            raise e
        finally:
            cursor.close()
            conn.close()
