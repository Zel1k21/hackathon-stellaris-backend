from internal.api.database import get_db
from internal.models.observation import Observation

connection = get_db()


class ObservationRepository:
    def Create(observation: Observation):
        conn = connection.cursor()
        conn.execute(
            "insert into observation (name, space_body_id, user_id, observation_time, declination, ascension, photo_url) values (?, ?, ?, ?, ?, ?, ?)",
            (
                observation.name,
                observation.space_body_id,
                observation.user_id,
                observation.observation_time,
                observation.declination,
                observation.ascension,
                observation.photo_url,
            ),
        )
        result = conn.fetchone()
        conn.commit()
        return result

    def GetObservationByID(observation_id: int):
        conn = connection.cursor()
        conn.execute(
            "select * from observation where id = ?",
            (observation_id),
        )
        result = conn.fetchone()
        conn.commit()
        return result

    def GetObservationsBySpaceBodyID(space_body_id: int):
        """Return all observations for a given space body id."""
        conn = connection.cursor()
        conn.execute(
            "select * from observation where space_body_id = ?",
            (space_body_id,),
        )
        results = conn.fetchall()
        conn.commit()
        return results
