from internal.api.server import get_db
from internal.models.user import User

connection = get_db()


class UserRepository:
    def Create(user: User):
        conn = connection.cursor()
        conn.execute(
            "insert into users (name, password, is_moderator) values (?, ?, ?)",
            (user.name, user.password, user.is_moderator),
        )
        result = conn.fetchone()
        conn.commit()
        return result

    def GetUserByID(user_id: int):
        conn = connection.cursor()
        conn.execute(
            "select * from users where id = ?",
            (user_id,),
        )
        result = conn.fetchone()
        conn.commit()
        return result
