from flask import Flask
from internal.app.handler.user import register_user_routes


def register_routes(app: Flask):
    register_user_routes(app)
