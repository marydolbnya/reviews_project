from sqlalchemy import orm
import sqlalchemy
import datetime
from .db_session import SqlAlchemyBase


class Photo(SqlAlchemyBase):
    __tablename__ = 'photos'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    review_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("reviews.id"), nullable=False)
    creation_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now, nullable=False)

    review = orm.relationship('Review')