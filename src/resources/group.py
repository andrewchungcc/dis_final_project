from sqlalchemy import func
from flask_restful import Resource, reqparse
from src.extensions import db
from src.models import Group, UserGroup

parser = reqparse.RequestParser()
parser.add_argument(
    "group_name", type=str, required=True, help="Group name is required."
)


class GroupResource(Resource):
    def post(self):
        """
        創建指定名稱的群組。
        """
        args = parser.parse_args()
        group_name = args["group_name"]

        # 檢查群組名稱是否已存在
        existing_group = Group.query.filter_by(group_name=group_name).first()
        if existing_group:
            return {"message": "Group name already exists."}, 400

        # 創建新的群組
        new_group = Group(group_name=group_name)
        db.session.add(new_group)
        db.session.commit()

        return {
            "message": "Group created successfully.",
            "group": new_group.to_dict(),
        }, 201


class GroupListResource(Resource):
    def get(self, user_id):
        """
        列出所有群組，依照創建時間倒序排序，並標記該使用者是否已加入。
        """
        args = parser.parse_args()
        user_id = args["user_id"]

        # 查詢所有群組及會員數
        groups_with_count = (
            db.session.query(
                Group.group_id,
                Group.group_name,
                Group.created_time,
                func.count(UserGroup.user_id).label("member_count"),
                # 標記該 user 是否已加入
                func.sum(func.ifnull(UserGroup.user_id == user_id, 0)).label(
                    "is_joined"
                ),
            )
            .outerjoin(UserGroup, Group.group_id == UserGroup.group_id)
            .group_by(Group.group_id, Group.group_name, Group.created_time)
            .order_by(Group.created_time.desc())
            .all()
        )

        # 將結果轉為字典形式
        result = [
            {
                "group_id": group.group_id,
                "group_name": group.group_name,
                "created_time": group.created_time.isoformat(),
                "member_count": group.member_count,
                "is_joined": bool(group.is_joined),
            }
            for group in groups_with_count
        ]

        return result, 200
