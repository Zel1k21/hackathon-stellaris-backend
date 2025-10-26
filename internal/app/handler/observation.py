from flask import Flask, request, jsonify
from internal.app.repository.observation import ObservationRepository
from internal.app.repository.spaceBody import SpaceBodyRepository
from internal.models.observation import Observation
from internal.models.spaceBody import SpaceBody
from internal.app.auth.jwt_utils import token_required
import datetime


def register_observation_route(app: Flask):
    @app.route("/api/comets", methods=["POST"])
    @token_required
    def create_observation():
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ["name", "observations"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Проверяем, что observations - это массив
        if not isinstance(data["observations"], list):
            return jsonify({"error": "Observations must be an array"}), 400

        # Проверяем каждый объект в массиве observations
        for i, obs in enumerate(data["observations"]):
            if not isinstance(obs, dict):
                return jsonify({"error": f"Observation {i} must be an object"}), 400

            # Проверяем обязательные поля в каждом наблюдении
            required_obs_fields = [
                "declination",
                "rightAscension",
                "timestamp",
                "photo",
            ]
            for field in required_obs_fields:
                if field not in obs:
                    return jsonify(
                        {"error": f"Missing field '{field}' in observation {i}"}
                    ), 400

        try:
            # Создаем космическое тело (space_body) и получаем его ID
            space_body = SpaceBody(id=None, name=data["name"], is_visible=True)

            # Создаем space_body в базе данных
            space_body_id = SpaceBodyRepository.Create(space_body)

            # Получаем ID пользователя из JWT токена
            user_id = request.user_id

            # Создаем каждое наблюдение в базе данных
            created_observations = []
            for obs_data in data["observations"]:
                # Создаем объект Observation для каждого элемента массива
                observation = Observation(
                    id=None,
                    space_body_id=space_body_id,  # Используем ID созданного космического тела
                    user_id=user_id,  # Используем ID пользователя из JWT токена
                    observation_time=datetime.datetime.fromtimestamp(
                        obs_data["timestamp"]
                    ),
                    declination=obs_data["declination"],
                    ascension=obs_data["rightAscension"],
                    photo_url=obs_data["photo"],
                )

                # Сохраняем в базу данных
                observation_id = ObservationRepository.Create(observation)
                created_observations.append(observation_id)

            return jsonify(
                {
                    "message": f"Created {len(created_observations)} observations for {data['name']}",
                    "space_body_id": space_body_id,
                    "observation_ids": created_observations,
                }
            ), 201

        except Exception as e:
            return jsonify({"error": f"Failed to create observations: {str(e)}"}), 500

    @app.route("/api/comets", methods=["GET"])
    def get_comets_with_observations():
        try:
            # Получаем все космические тела
            space_bodies = SpaceBodyRepository.GetAllSpaceBodies()

            comets_data = []
            for space_body in space_bodies:
                # Получаем все наблюдения для этого космического тела
                observations = ObservationRepository.GetObservationsBySpaceBody(
                    space_body["id"]
                )

                # Формируем данные для ответа
                comet_data = {
                    "id": space_body["id"],
                    "name": space_body["name"],
                    "observations": [],
                }

                # Добавляем наблюдения
                for obs in observations:
                    comet_data["observations"].append(
                        {
                            "timestamp": obs["observation_time"].isoformat()
                            if obs["observation_time"]
                            else None,
                            "declination": obs["declination"],
                            "rightAscension": obs["ascension"],
                            "photo": obs["photo_url"],
                        }
                    )

                comets_data.append(comet_data)

            return jsonify({"comets": comets_data, "total": len(comets_data)}), 200

        except Exception as e:
            return jsonify({"error": f"Failed to get comets: {str(e)}"}), 500
