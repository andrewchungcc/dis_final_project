from datetime import datetime
from .extensions import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    account = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "name": self.name,
            "account": self.account,
        }


class Group(db.Model):
    __tablename__ = "groups"

    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_name = db.Column(db.String(50), nullable=False, unique=True)
    created_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def to_dict(self):
        return {
            "group_id": self.group_id,
            "group_name": self.group_name,
            "created_time": self.created_time.isoformat(),
        }


class UserGroup(db.Model):
    __tablename__ = "user_groups"

    user_id = db.Column(
        db.String(50),
        db.ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    group_id = db.Column(
        db.Integer,
        db.ForeignKey("groups.group_id", ondelete="CASCADE"),
        primary_key=True,
    )
    joined_time = db.Column(db.DateTime, default=datetime.now, nullable=False)


class Post(db.Model):
    __tablename__ = "posts"

    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.String(50),
        db.ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    group_id = db.Column(
        db.Integer,
        db.ForeignKey("groups.group_id", ondelete="CASCADE"),
        nullable=False,
    )
    content = db.Column(db.Text, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def to_dict(self):
        return {
            "post_id": self.post_id,
            "user_id": self.user_id,
            "group_id": self.group_id,
            "content": self.content,
            "created_time": self.created_time.isoformat(),
        }
