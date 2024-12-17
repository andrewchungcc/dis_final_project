from sqlalchemy import func
from flask_restful import Resource, reqparse
from src.extensions import db
from src.models import User, Group, UserGroup, Post

parser = reqparse.RequestParser()
parser.add_argument(
    "group_name", type=str, required=True, help="Group name is required."
)


class GroupResource(Resource):
    def get(self, group_id):
        """
        列出指定群組中的所有貼文和成員。
        """
        target_group = Group.query.filter_by(group_id=group_id).first()
        if not target_group:
            return {"message": "Group not found."}, 404

        members = (
            db.session.query(User.user_id, User.name)
            .join(UserGroup, User.user_id == UserGroup.user_id)
            .filter(UserGroup.group_id == group_id)
            .all()
        )

        posts = (
            db.session.query(Post.post_id, Post.title, Post.content, Post.created_time)
            .filter(Post.group_id == group_id)
            .order_by(Post.created_time.desc())
            .all()
        )

        members_list = [
            {"user_id": member.user_id, "name": member.name} for member in members
        ]

        posts_list = [
            {
                "post_id": post.post_id,
                "title": post.title,
                "content": post.content,
                "created_time": post.created_time.isoformat(),
            }
            for post in posts
        ]

        return {
            "group_id": group_id,
            "group_name": target_group.group_name,
            "posts": posts_list,
            "members": members_list,
        }, 200

    def post(self, group_id, user_id):
        if group_id == 0:
            # 創建新的群組
            args = parser.parse_args()
            group_name = args["group_name"]

            # 檢查群組名稱是否已存在
            existing_group = Group.query.filter_by(group_name=group_name).first()
            if existing_group:
                return {"message": "Group name already exists."}, 400

            # 創建新群組
            new_group = Group(group_name=group_name)
            db.session.add(new_group)
            db.session.commit()

            # 將創建者加入新群組
            user_group_entry = UserGroup(user_id=user_id, group_id=new_group.group_id)
            db.session.add(user_group_entry)
            db.session.commit()

            return {
                "message": "Group created successfully.",
                "group": {
                    "group_id": new_group.group_id,
                    "group_name": new_group.group_name,
                    "member_count": 1,
                },
            }, 200

        # 加入指定群組
        target_group = Group.query.filter_by(group_id=group_id).first()
        if not target_group:
            return {"message": "Group not found."}, 404

        # 檢查使用者是否已在群組中
        existing_user_group = UserGroup.query.filter_by(
            user_id=user_id, group_id=group_id
        ).first()
        if existing_user_group:
            return {"message": "User is already in the group."}, 400

        # 將使用者加入群組
        user_group_entry = UserGroup(user_id=user_id, group_id=group_id)
        db.session.add(user_group_entry)
        db.session.commit()

        # 計算群組目前的人數
        member_count = (
            db.session.query(func.count(UserGroup.user_id))
            .filter_by(group_id=group_id)
            .scalar()
        )

        return {
            "message": f"User {user_id} successfully added to group {group_id}.",
            "group": {
                "group_id": group_id,
                "group_name": target_group.group_name,
                "member_count": member_count,
            },
        }, 200


class GroupListResource(Resource):
    def get(self, user_id):
        """
        列出所有群組，依照創建時間倒序排序，並標記該使用者是否已加入。
        """
        # 查詢所有群組及其會員數
        groups_with_count = (
            db.session.query(
                Group.group_id,
                Group.group_name,
                Group.created_time,
                func.count(UserGroup.user_id).label("member_count"),
            )
            .outerjoin(UserGroup, Group.group_id == UserGroup.group_id)
            .group_by(Group.group_id, Group.group_name, Group.created_time)
            .order_by(Group.created_time.desc())
            .all()
        )

        # 查詢指定 user_id 加入了哪些群組
        joined_group_ids = set(
            db.session.query(UserGroup.group_id)
            .filter(UserGroup.user_id == user_id)
            .all()
        )
        # 轉換成一維 set
        joined_group_ids = {group_id for (group_id,) in joined_group_ids}

        # 將結果轉為字典形式，並標記 is_joined
        result = [
            {
                "group_id": group.group_id,
                "group_name": group.group_name,
                "created_time": group.created_time.isoformat(),
                "member_count": group.member_count,
                "is_joined": group.group_id in joined_group_ids,
            }
            for group in groups_with_count
        ]

        return result, 200
