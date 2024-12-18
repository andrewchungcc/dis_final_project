import secrets
from flask import g
from flask_restful import Resource, reqparse
from werkzeug.security import check_password_hash, generate_password_hash
from src.extensions import db
from src.models import User

login_parser = reqparse.RequestParser()
login_parser.add_argument("account", type=str, help="Account is required.", required=True, )
login_parser.add_argument("password", type=str, help="Password is required.", required=True, )

register_parser = reqparse.RequestParser()
register_parser.add_argument("account", type=str, help="Account of the user", required=True)
register_parser.add_argument("name", type=str, help="Name of the user", required=True)
register_parser.add_argument("password", type=str, help="Password of the user", required=True)


class UserResource(Resource):
    def get(self, user_id):
        user_id = g.user_id
        user = User.query.get_or_404(user_id)

        return user.to_dict()

    def post(self):
        args = register_parser.parse_args()
        account = args["account"]
        name = args["name"]
        password = args["password"]

        user_id = secrets.token_urlsafe(21)
        # hashed_password = generate_password_hash(password)
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        new_user = User(
            user_id=user_id, account=account, name=name, password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return new_user.to_dict(), 200

class LoginResource(Resource):
    def post(self):
        """
        登入功能
        """
        args = login_parser.parse_args()
        account = args["account"]
        password = args["password"]

        # 檢查帳號是否存在
        user = User.query.filter_by(account=account).first()
        if not user:
            return {"message": "Invalid account or password."}, 401

        # 驗證密碼
        if not check_password_hash(user.password, password):
            return {"message": "Invalid account or password."}, 401

        # 登入成功，回傳使用者資訊
        return {
            "message": "Login successful.",
            "user": user.to_dict()
        }, 200