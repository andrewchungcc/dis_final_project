import secrets
from flask import g
from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash
from src.extensions import db
from src.models import User

parser = reqparse.RequestParser()
parser.add_argument("account", type=str, help="Account of the user", required=True)
parser.add_argument("name", type=str, help="Name of the user", required=True)


class UserResource(Resource):
    def get(self, user_id):
        user_id = g.user_id
        user = User.query.get_or_404(user_id)

        return user.to_dict()

    def post(self):
        args = parser.parse_args()
        account = args["account"]
        name = args["name"]
        password = args["password"]

        user_id = secrets.token_urlsafe(21)
        hashed_password = generate_password_hash(password)

        new_user = User(
            user_id=user_id, account=account, name=name, password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return new_user.to_dict(), 200
