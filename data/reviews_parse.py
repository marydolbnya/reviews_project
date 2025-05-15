from flask_restful import reqparse
from datetime import datetime

parser = reqparse.RequestParser()
parser.add_argument('author_id', required=True, type=int)
parser.add_argument('title', required=True)
parser.add_argument('text', required=True, type=int)
parser.add_argument('creation_date', required=True, type=datetime)
