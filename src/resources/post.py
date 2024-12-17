from flask import g
from flask_restful import Resource, reqparse
from src.extensions import db
from src.models import User, Group, Post, UserGroup
from datetime import datetime

parser = reqparse.RequestParser()
parser.add_argument(
    "content", type=str, required=True, help="Post content is required."
)


# 計算積分的函數
def calculate_dynamic_score(group_id):
    """
    根據公式計算指定群組的分數，考慮會員多隊伍參與的權重：
    Score = T / (alpha * (S + 1)) + beta * N
    """
    alpha = 1
    beta = 0.01

    user_groups = UserGroup.query.filter_by(group_id=group_id).all()
    total_weighted_users = 0
    for user_group in user_groups:
        user_teams = UserGroup.query.filter_by(user_id=user_group.user_id).count()
        total_weighted_users += 0 if user_teams == 0 else 1 / user_teams

    T = total_weighted_users

    first_post = (
        Post.query.filter_by(group_id=group_id)
        .order_by(Post.created_time.asc())
        .first()
    )
    last_post = (
        Post.query.filter_by(group_id=group_id)
        .order_by(Post.created_time.desc())
        .first()
    )
    if first_post and last_post:
        S = (last_post.created_time - first_post.created_time).total_seconds()
    else:
        S = 0

    N = (
        UserGroup.query.filter_by(group_id=group_id)
        .filter(
            UserGroup.joined_time >= datetime.now().replace(hour=0, minute=0, second=0)
        )
        .count()
    )

    score = T / (alpha * (S + 1)) + beta * N
    return score


class PostResource(Resource):
    def post(self, group_id):
        """
        在指定組別新增一個 post，並回傳計算後的分數。
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

        # 計算分數
        score = calculate_dynamic_score(group_id)

        return {
            "message": "Post created successfully.",
            "post": new_post.to_dict(),
            "score": score,  # 回傳計算的分數
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
