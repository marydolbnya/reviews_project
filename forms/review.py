from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class ReviewForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    text = TextAreaField('Отзыв', validators=[DataRequired()])
    submit = SubmitField('Сохранить')