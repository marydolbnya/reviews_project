from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField
from wtforms.validators import DataRequired


class PhotoForm(FlaskForm):
    photo = FileField('Фото')
    submit = SubmitField('Сохранить')