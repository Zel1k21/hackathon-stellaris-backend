from flask import Flask
from internal.app.handler.observation import register_observation_route
from internal.app.handler.spaceBody import register_space_body_routes
from internal.app.handler.user import register_user_routes


def register_routes(app: Flask):
    register_observation_route(app)
    register_space_body_routes(app)
    register_user_routes(app)
