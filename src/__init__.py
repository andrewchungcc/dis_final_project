import os
import logging
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_restful import Api
from flask_socketio import SocketIO
import firebase_admin
from firebase_admin import credentials, auth
from config import Config
from .extensions import db
from src.resources.user import UserResource, LoginResource
from src.resources.post import PostResource, PostListResource
from src.resources.group import GroupResource, GroupListResource
from src.resources.userGroup import UserGroupResource
from src.resources.leaderboard import LeaderboardResource


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.logger.setLevel(logging.DEBUG)

    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_error_logger.handlers
    app.logger.setLevel(gunicorn_error_logger.level)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode="eventlet",
    )
    socketio.init_app(app)

    # firebase_admin.initialize_app()

    api = Api(app)
    api.add_resource(LoginResource, "/api/login")
    api.add_resource(UserResource, "/api/user", "/api/user/<string:user_id>")
    api.add_resource(PostResource, "/api/post/<int:group_id>/<string:user_id>")
    api.add_resource(PostListResource, "/api/posts/<int:group_id>/<string:user_id>")
    api.add_resource(GroupResource, "/api/group/<int:group_id>/<string:user_id>")
    api.add_resource(GroupListResource, "/api/groups/<string:user_id>")
    api.add_resource(UserGroupResource, "/api/usergroup")
    api.add_resource(LeaderboardResource, "/api/leaderboard")

    # @app.before_request
    # def authenticate_user():
    #     try:
    #         if request.method != "OPTIONS":
    #             auth_header = request.headers.get("Authorization")

    #             if not auth_header:
    #                 return jsonify({"error": "Unauthorized"}), 401
    #             else:
    #                 bearer_token = auth_header.split(" ")[1]
    #                 decoded_token = auth.verify_id_token(bearer_token)

    #                 g.user_id = decoded_token["uid"]
    #                 g.user_name = decoded_token["name"]
    #     except Exception as e:
    #         return jsonify({"error": str(e)}), 401

    return app, socketio
