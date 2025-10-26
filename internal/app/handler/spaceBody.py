from flask import Flask, jsonify
from internal.app.repository.spaceBody import SpaceBodyRepository
from internal.app.repository.observation import ObservationRepository


def register_space_body_routes(app: Flask):
    @app.route("/api/comets/<int:body_id>", methods=["GET"])
    def get_space_body(body_id: int):
        """Return full information about a comet (space body) by id.

        Response:
          200 -> { "comet": { "id": int, "name": str,} }
          404 -> { "error": "Comet not found" }
          500 -> { "error": "..." }
        """
        try:
            result = SpaceBodyRepository.GetSpaceBodyByID(body_id)

            if not result:
                return jsonify({"error": "Comet not found"}), 404

            # result may be a mapping (dict-like) or a tuple. Handle both.
            comet = None
            if hasattr(result, "get"):
                comet = {
                    "id": result.get("id"),
                    "name": result.get("name"),
                }
            else:
                # tuple/list-like: assume (id, name, is_visible)
                try:
                    comet = {
                        "id": result[0],
                        "name": result[1],
                    }
                except Exception:
                    # fallback: return raw row
                    return jsonify({"comet": result, "observations": []}), 200

            # Fetch related observations for this comet (space body)
            try:
                obs_rows = ObservationRepository.GetObservationsBySpaceBody(body_id)

            except Exception:
                obs_rows = None

            observations = []
            if obs_rows:
                for row in obs_rows:
                    if hasattr(row, "get"):
                        observations.append(
                            {
                                "timestamp": row.get("observation_time"),
                                "declination": row.get("declination"),
                                "rightAscension": row.get("ascension"),
                                "photo": row.get("photo_url"),
                            }
                        )
                    else:
                        # tuple-like: (id, space_body_id, user_id, observation_time, declination, ascension, photo_url)
                        try:
                            observations.append(
                                {
                                    "timestamp": row[3],
                                    "declination": row[4],
                                    "rightAscension": row[5],
                                    "photo": row[6] if len(row) > 6 else None,
                                }
                            )
                        except Exception:
                            observations.append(row)

            return jsonify({"comet": comet, "observations": observations}), 200

        except Exception as e:
            return jsonify({"error": f"Failed to get comet info: {str(e)}"}), 500
