from flask import g
from flask_restful import Resource, reqparse
from src.extensions import db
from src.models import User, Group, Post, UserGroup

parser = reqparse.RequestParser()
parser.add_argument(
    "content", type=str, required=True, help="Post content is required."
)


class PostResource(Resource):
    def post(self, group_id):
        """
        在指定組別新增一個 post。
        """
        args = parser.parse_args()
        user_id = g.user_id  # 從 g 獲取當前用戶 id

        # 驗證用戶是否存在
        user = User.query.get_or_404(user_id)

        # 驗證群組是否存在
        group = Group.query.get_or_404(group_id)

        # 驗證用戶是否屬於該群組
        user_in_group = UserGroup.query.filter_by(
            user_id=user_id, group_id=group_id
        ).first()
        if not user_in_group:
            return {"message": "User is not a member of this group."}, 403

        # 新增 post
        new_post = Post(user_id=user_id, group_id=group_id, content=args["content"])
        db.session.add(new_post)
        db.session.commit()

        return {
            "message": "Post created successfully.",
            "post": new_post.to_dict(),
        }, 200


class PostListResource(Resource):
    def get(self, group_id):
        """
        取得指定組別的所有 posts。
        """
        user_id = g.user_id  # 從 g 獲取當前用戶 id

        # 驗證用戶是否存在
        user = User.query.get_or_404(user_id)

        # 驗證群組是否存在
        group = Group.query.get_or_404(group_id)

        # 驗證用戶是否屬於該群組
        user_in_group = UserGroup.query.filter_by(
            user_id=user_id, group_id=group_id
        ).first()
        if not user_in_group:
            return {"message": "User is not a member of this group."}, 403

        # 查詢所有 posts
        posts = Post.query.filter_by(group_id=group_id).all()
        return [post.to_dict() for post in posts], 200
