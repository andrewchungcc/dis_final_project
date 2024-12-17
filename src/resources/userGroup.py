from flask_restful import Resource, reqparse
from src.extensions import db
from src.models import User, Group, UserGroup
from datetime import datetime

# 解析器設定
join_parser = reqparse.RequestParser()
join_parser.add_argument(
    "user_id", type=str, required=True, help="User ID is required."
)
join_parser.add_argument(
    "group_id", type=int, required=True, help="Group ID is required."
)

class UserGroupResource(Resource):
    def post(self):
        """
        讓使用者加入指定群組，同時更新 user_groups 關聯表。
        """
        args = join_parser.parse_args()
        user_id = args["user_id"]
        group_id = args["group_id"]

        # 檢查使用者和群組是否存在
        user = User.query.filter_by(user_id=user_id).first()
        group = Group.query.filter_by(group_id=group_id).first()

        if not user:
            return {"message": "User not found."}, 404
        if not group:
            return {"message": "Group not found."}, 404

        # 檢查是否已經加入過該群組
        existing_relation = UserGroup.query.filter_by(user_id=user_id, group_id=group_id).first()
        if existing_relation:
            return {"message": "User already joined this group."}, 400

        # 創建新的關聯紀錄
        new_relation = UserGroup(user_id=user_id, group_id=group_id, joined_time=datetime.now())
        db.session.add(new_relation)
        db.session.commit()

        return {
            "message": "User joined the group successfully.",
            "user_id": user_id,
            "group_id": group_id,
        }, 201
