from sqlalchemy import orm
import sqlalchemy
import datetime
from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    review_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("reviews.id"), nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    creation_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now, nullable=False)

    author = orm.relationship('User')
    review = orm.relationship('Review')