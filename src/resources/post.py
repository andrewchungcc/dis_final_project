from flask_socketio import emit
from sqlalchemy import func, exists
from flask import g
from flask_restful import Resource, reqparse
from src.extensions import db
from src.models import User, Group, Post, UserGroup
from datetime import datetime, timedelta

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
    # print("T:", T, "S:", S, N)
    return score


class PostResource(Resource):
    def post(self, group_id, user_id):
        """
        在指定組別新增一個 post，並回傳計算後的分數。
        排除同一個人短時間內多次打卡的情況。
        """
        args = parser.parse_args()

        user = User.query.get_or_404(user_id)
        group = Group.query.get_or_404(group_id)

        user_in_group = UserGroup.query.filter_by(
            user_id=user_id, group_id=group_id
        ).first()
        if not user_in_group:
            return {"message": "User is not a member of this group."}, 403

        # 排除同一個人短時間內多次打卡
        time_limit = timedelta(minutes=5)  # 設定 5 分鐘內不能重複打卡
        last_post = (
            Post.query.filter_by(user_id=user_id, group_id=group_id)
            .order_by(Post.created_time.desc())
            .first()
        )

        if last_post and datetime.now() - last_post.created_time < time_limit:
            return {"message": "You cannot post again within 5 minutes."}, 403

        new_post = Post(user_id=user_id, group_id=group_id, content=args["content"])
        db.session.add(new_post)
        db.session.commit()

        score = calculate_dynamic_score(group_id)
        emit(
            "score_update",
            {"group_id": group_id, "score": score},
            namespace="/",
            broadcast=True,
        )
        group.group_score = score
        db.session.commit()

        post_dict = new_post.to_dict()
        post_dict["user_name"] = user.name

        return {
            "message": "Post created successfully.",
            "post": post_dict,
            "score": score,
        }, 200


class PostListResource(Resource):
    def get(self, group_id, user_id):
        """
        列出指定群組中的所有貼文和成員，並標記使用者是否已有貼文。
        """
        target_group = Group.query.filter_by(group_id=group_id).first()
        if not target_group:
            return {"message": "Group not found."}, 404

        members = (
            db.session.query(
                User.user_id,
                User.name,
                func.coalesce(func.max(Post.created_time), None).label(
                    "last_post_time"
                ),
            )
            .join(UserGroup, User.user_id == UserGroup.user_id)
            .outerjoin(
                Post, (Post.user_id == User.user_id) & (Post.group_id == group_id)
            )
            .filter(UserGroup.group_id == group_id)
            .group_by(User.user_id)
            .all()
        )

        posts = (
            db.session.query(
                Post.post_id,
                Post.content,
                Post.created_time,
                User.name.label("user_name"),
            )
            .join(User, User.user_id == Post.user_id)
            .filter(Post.group_id == group_id)
            .order_by(Post.created_time.desc())
            .all()
        )

        user_has_posts = db.session.query(
            exists().where(Post.group_id == group_id).where(Post.user_id == user_id)
        ).scalar()

        members_list = [
            {
                "user_id": member.user_id,
                "name": member.name,
                "last_post_time": (
                    member.last_post_time.isoformat() if member.last_post_time else ""
                ),
            }
            for member in members
        ]

        posts_list = [
            {
                "post_id": post.post_id,
                "user_name": post.user_name,
                "content": post.content,
                "created_time": post.created_time.isoformat(),
            }
            for post in posts
        ]

        print("posts_list: ", posts_list)

        return {
            "group_id": group_id,
            "group_name": target_group.group_name,
            "group_score": target_group.group_score,
            "posts": posts_list,
            "members": members_list,
            "has_user_posts": user_has_posts,
        }, 200
