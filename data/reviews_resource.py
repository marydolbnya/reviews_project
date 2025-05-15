import os
from flask_restful import abort, Resource
from . import db_session
from flask import jsonify, request, make_response
from .users import User
from .reviews import Review
from .photos import Photo
from .users_parse import parser


def abort_if_review_not_found(review_id):
    session = db_session.create_session()
    review = session.query(Review).get(review_id)
    if not review:
        abort(404, message=f"Review {review_id} not found")


fields = ('id', 'author_id', 'title', 'text', 'creation_date')


class ReviewResource(Resource):
    def get(self, review_id):
        abort_if_review_not_found(review_id)
        db_sess = db_session.create_session()
        review = db_sess.query(Review).get(review_id)
        return jsonify(
            {
                'review': review.to_dict(only=fields)
            }
        )

    def put(self, review_id):
        abort_if_review_not_found(review_id)
        args = parser.parse_args()
        db_sess = db_session.create_session()
        review = db_sess.query(Review).get(review_id)
        review.title = args['title']
        review.text = args['text']
        db_sess.commit()
        return jsonify({'id': review.id})
    
    def delete(self, review_id):
        abort_if_review_not_found(review_id)
        db_sess = db_session.create_session()
        review = db_sess.query(Review).get(review_id)
        for photo in db_sess.query(Photo).filter(Photo.review_id == review.id).all():
            fname = f"static/img/photo_for_id_{photo.id}.jpg"
            if os.path.isfile(fname):
                os.remove(fname)
            db_sess.delete(photo)
        db_sess.delete(review)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class ReviewsListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        reviews = db_sess.query(Review).all()
        return jsonify(
            {
                'reviews': [review.to_dict(only=fields) for review in reviews]
            }
        )

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        review = Review(
            author_id = args['author_id'],
            title = args['title'],
            text = args['text'])
        db_sess.add(review)
        db_sess.commit()
        return jsonify({'id': review.id})