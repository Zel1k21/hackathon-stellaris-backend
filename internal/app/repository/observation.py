from internal.api.database import get_db_connection
from internal.models.observation import Observation


class ObservationRepository:
    @staticmethod
    def Create(observation: Observation):
        """Create a new observation in the database"""
        conn = get_db_connection()
        cursor = conn.cursor()
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
            observation_id = cursor.fetchone()[0]
            conn.commit()
            return observation_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def GetObservationByID(observation_id: int):
        """Get observation by ID from database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM observations WHERE id = %s",
                (observation_id,),
            )
            result = cursor.fetchone()
            if result:
                return {
                    "id": result[0],
                    "space_body_id": result[1],
                    "user_id": result[2],
                    "observation_time": result[3],
                    "declination": result[4],
                    "ascension": result[5],
                    "photo_url": result[6],
                }
            return None
        except Exception as e:
            raise e
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def GetObservationsBySpaceBody(space_body_id: int):
        """Get all observations for a specific space body"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM observations WHERE space_body_id = %s ORDER BY observation_time DESC",
                (space_body_id,),
            )
            results = cursor.fetchall()
            observations = []
            for result in results:
                observations.append(
                    {
                        "id": result[0],
                        "space_body_id": result[1],
                        "user_id": result[2],
                        "observation_time": result[3],
                        "declination": result[4],
                        "ascension": result[5],
                        "photo_url": result[6],
                    }
                )
            return observations
        except Exception as e:
            raise e
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def GetObservationsByUser(user_id: int):
        """Get all observations for a specific user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM observations WHERE user_id = %s ORDER BY observation_time DESC",
                (user_id,),
            )
            results = cursor.fetchall()
            observations = []
            for result in results:
                observations.append(
                    {
                        "id": result[0],
                        "space_body_id": result[1],
                        "user_id": result[2],
                        "observation_time": result[3],
                        "declination": result[4],
                        "ascension": result[5],
                        "photo_url": result[6],
                    }
                )
            return observations
        except Exception as e:
            raise e
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def GetObservationsBySpaceBody(space_body_id: int):
        """Get all observations for a specific space body"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM observations WHERE space_body_id = %s ORDER BY observation_time DESC",
                (space_body_id,),
            )
            results = cursor.fetchall()
            observations = []
            for result in results:
                observations.append(
                    {
                        "id": result[0],
                        "space_body_id": result[1],
                        "user_id": result[2],
                        "observation_time": result[3],
                        "declination": result[4],
                        "ascension": result[5],
                        "photo_url": result[6],
                    }
                )
            return observations
        except Exception as e:
            raise e
        finally:
            cursor.close()
            conn.close()
