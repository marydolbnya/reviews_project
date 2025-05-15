from flask_restful import reqparse
from datetime import datetime

parser = reqparse.RequestParser()
parser.add_argument('surname', required=True)
parser.add_argument('name', required=True)
parser.add_argument('age', required=True, type=int)
parser.add_argument('email', required=True)
parser.add_argument('about', required=True)
parser.add_argument('hashed_password', required=True)
parser.add_argument('registration_date', required=True, type=datetime)
