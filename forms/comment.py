from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    text = TextAreaField('Комментарий', validators=[DataRequired()])
    submit = SubmitField('Сохранить')