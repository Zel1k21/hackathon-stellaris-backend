from internal.api.database import get_db_connection
from internal.models.spaceBody import SpaceBody


class SpaceBodyRepository:
    @staticmethod
    def Create(body: SpaceBody):
        """Create a new space body in the database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO spaceBodies (name, is_visible) VALUES (%s, %s) RETURNING id",
                (body.name, body.is_visible),
            )
            space_body_id = cursor.fetchone()[0]
            conn.commit()
            return space_body_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def GetSpaceBodyByID(body_id: int):
        """Get space body by ID from database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM spaceBodies WHERE id = %s",
                (body_id,),
            )
            result = cursor.fetchone()
            if result:
                return {
                    "id": result[0],
                    "name": result[1],
                    "is_visible": result[2],
                }
            return None
        except Exception as e:
            raise e
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def GetSpaceBodyByName(name: str):
        """Get space body by name from database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM spaceBodies WHERE name = %s",
                (name,),
            )
            result = cursor.fetchone()
            if result:
                return {
                    "id": result[0],
                    "name": result[1],
                    "is_visible": result[2],
                }
            return None
        except Exception as e:
            raise e
        finally:
            cursor.close()
            conn.close()
