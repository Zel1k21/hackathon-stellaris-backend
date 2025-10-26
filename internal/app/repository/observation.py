from internal.api.database import get_db_connection
from internal.models.observation import Observation

connection = get_db_connection()


class ObservationRepository:
    @staticmethod
    def Create(observation: Observation):
        """Create an observation and return the new id (or None)."""
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO observations (space_body_id, user_id, observation_time, declination, ascension, photo_url) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (
                    observation.space_body_id,
                    observation.user_id,
                    observation.observation_time,
                    observation.declination,
                    observation.ascension,
                    observation.photo_url,
                ),
            )
            result = cursor.fetchone()
            connection.commit()
            return result[0] if result else None
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()

    @staticmethod
    def GetObservationByID(observation_id: int):
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT * FROM observations WHERE id = %s",
                (observation_id,),
            )
            result = cursor.fetchone()
            return result
        except Exception:
            raise
        finally:
            cursor.close()

    @staticmethod
    def GetObservationsBySpaceBodyID(space_body_id: int):
        """Return all observations for a given space body id."""
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT * FROM observations WHERE space_body_id = %s ORDER BY observation_time DESC",
                (space_body_id,),
            )
            results = cursor.fetchall()
            return results
        except Exception:
            raise
        finally:
            cursor.close()
