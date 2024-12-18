from flask_restful import Resource
from src.extensions import db
from src.models import Group


class LeaderboardResource(Resource):
    def get(self):
        """
        列出所有群組，並返回每個群組的名稱與分數。
        """
        groups = Group.query.all()

        if not groups:
            return {"message": "No groups found."}, 404

        groups_sorted = sorted(
            groups, key=lambda group: group.group_score, reverse=True
        )

        return [group.to_dict() for group in groups_sorted[:20]], 200
