from flask_restful import Resource, reqparse
from src.extensions import db
from src.models import Group

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
    def get(self):
        """
        列出所有群組，依照創建時間倒序排序。
        """
        groups = Group.query.order_by(Group.created_time.desc()).all()
        return [group.to_dict() for group in groups], 200
