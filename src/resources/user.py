from flask import g
from flask_restful import Resource, reqparse
from src.extensions import db
from src.models import User, Paletter

parser = reqparse.RequestParser()
parser.add_argument("name", type=str, help="Name of the user")
parser.add_argument("profile_picture", type=str, help="Profile picture URL of the user")


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

            paletter = Paletter(
                user_id=user_id,
                paletter_code="Pal-1",
                intimacy_level=100,
                vitality_value=500,
            )

            db.session.add(paletter)
            db.session.commit()
            print("paletter created: ", user_id)

        return user.to_dict()

    def put(self):
        user_id = g.user_id
        user = User.query.get_or_404(user_id)
        args = parser.parse_args()
        user.name = args.get("name", user.name)
        db.session.commit()

        return user.to_dict()
