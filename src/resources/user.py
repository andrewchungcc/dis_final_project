from flask import g
from flask_restful import Resource, reqparse
from src.extensions import db
from src.models import User

parser = reqparse.RequestParser()
parser.add_argument("name", type=str, help="Name of the user")


class UserResource(Resource):
    def get(self):
        user_id = g.user_id
        print(user_id)

        user = User.query.filter_by(user_id=user_id).first()

        if not user:
            user = User(
                user_id=user_id,
                name="",
                profile_picture="",
                credit_limit=10,
            )
            db.session.add(user)
            db.session.commit()
            print("user created: ", user_id)

        return user.to_dict()
