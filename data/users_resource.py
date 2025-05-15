import os
from flask_restful import abort, Resource
from . import db_session
from flask import jsonify, request, make_response
from .users import User
from .reviews import Review
from .photos import Photo
from .users_parse import parser


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


fields_get = ('id', 'surname', 'name', 'age', 'email', 'registration_date', 'about')
fields = tuple(list(fields_get) + ['hashed_password'])


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        return jsonify(
            {
                'user': user.to_dict(only=fields_get)
            }
        )

    def put(self, user_id):
        abort_if_user_not_found(user_id)
        args = parser.parse_args()
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        user.surname = args['surname']
        user.name = args['name']
        user.age = args['age']
        user.email = args['email']
        user.about = args['about']
        user.hashed_password = args['hashed_password']
        db_sess.commit()
        return jsonify({'id': user.id})
    
    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        for review in db_sess.query(Review).filter(Review.author_id == user_id).all():
            for photo in db_sess.query(Photo).filter(Photo.review_id == review.id).all():
                fname = f"./static/img/photo_for_id_{photo.id}.jpg"
                if os.path.isfile(fname):
                    os.remove(fname)
                db_sess.delete(photo)
            db_sess.delete(review)
        fname = f"./static/img/avatar_for_id_{user.id}.jpg"
        if os.path.isfile(fname):
            os.remove(fname)
        db_sess.delete(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        return jsonify(
            {
                'users': [user.to_dict(only=fields_get) for user in users]
            }
        )

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        user = User(
            surname = args['surname'],
            name = args['name'],
            age = args['age'],
            email = args['email'],
            about = args['about'],
            hashed_password = args['hashed_password'])
        db_sess.add(user)
        db_sess.commit()
        return jsonify({'id': user.id})