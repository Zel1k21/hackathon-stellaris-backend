from flask import Flask
from internal.app.handler.user import register_user_routes
from internal.app.handler.spaceBody import space_body_info


def register_routes(app: Flask):
    register_user_routes(app)
    space_body_info(app)
