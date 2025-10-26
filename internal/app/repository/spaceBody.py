from internal.api.database import get_db_connection
from internal.models.spaceBody import SpaceBody

connection = get_db_connection()


class SpaceBodyRepository:
    def Create(body: SpaceBody):
        conn = connection.cursor()
        conn.execute(
            "insert into space_body (name, is_visible) values (?, ?)",
            (body.name, body.is_visible),
        )
        result = conn.fetchone()
        conn.commit()
        return result

    def GetSpaceBodyByID(body_id: int):
        conn = connection.cursor()
        conn.execute(
            "select * from space_body where id = ?",
            (body_id),
        )
        result = conn.fetchone()
        conn.commit()
        return result
