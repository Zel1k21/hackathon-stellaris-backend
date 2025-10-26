from flask import Flask, jsonify
from internal.app.repository.spaceBody import SpaceBodyRepository
from internal.app.repository.observation import ObservationRepository


def register_space_body_routes(app: Flask):
    @app.route("/api/comets/<int:body_id>", methods=["GET"])
    def get_space_body(body_id: int):
        """Return full information about a comet (space body) by id.

        Response:
          200 -> { "id": int, "name": str, "observations": [...] }
          404 -> { "error": "Comet not found" }
          500 -> { "error": "..." }
        """
        try:
            result = SpaceBodyRepository.GetSpaceBodyByID(body_id)

            if not result:
                return jsonify({"error": "Comet not found"}), 404

            # Extract comet info
            comet_id = None
            comet_name = None
            if hasattr(result, "get"):
                comet_id = result.get("id")
                comet_name = result.get("name")
            else:
                # tuple/list-like: assume (id, name, is_visible)
                try:
                    comet_id = result[0]
                    comet_name = result[1]
                except Exception:
                    # fallback: return raw row
                    return jsonify({"error": "Invalid comet data format"}), 500

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
                            # If we can't parse, skip this observation
                            continue

            # Return in the required format
            return jsonify(
                {"id": comet_id, "name": comet_name, "observations": observations}
            ), 200

        except Exception as e:
            return jsonify({"error": f"Failed to get comet info: {str(e)}"}), 500
