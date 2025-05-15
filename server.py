import os
from flask import Flask, render_template, redirect, request, url_for
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import reqparse, abort, Api, Resource
from forms.login import LoginForm
from forms.register import RegisterForm
from forms.review import ReviewForm
from forms.comment import CommentForm
from forms.photo import PhotoForm
from data.users import User
from data.reviews import Review
from data.comments import Comment
from data.photos import Photo
from data import users_resource, reviews_resource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_dolbnya_maria_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

api = Api(app)

api.add_resource(users_resource.UsersListResource, '/api/users')
api.add_resource(users_resource.UserResource, '/api/users/<int:user_id>')

api.add_resource(reviews_resource.ReviewsListResource, '/api/reviews')
api.add_resource(reviews_resource.ReviewResource, '/api/reviews/<int:review_id>')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        out_file_name = f"img/avatar_for_id_{user.id}.jpg"
        if form.avatar.data:
            request.files[form.avatar.name].save("./" + url_for("static", filename=out_file_name)[1:])

        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
def user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if user:
        if request.method == 'GET':
            return render_template('user.html', user=user)
        elif request.method == 'POST':
            new_email = request.form.get("email", user.email)
            if new_email != user.email:
                if db_sess.query(User).filter(User.email == new_email).first():
                    pass # email остается тем же
                else:
                    user.email = new_email
            user.surname = request.form.get("surname", user.surname)
            user.name = request.form.get("name", user.name)
            user.age = request.form.get("age", user.age)
            user.about = request.form.get("about", user.about)
            file = request.files.get("avatar", None)
            if file and file.filename and file.filename.endswith(".jpg"):
                out_file_name = f"img/avatar_for_id_{user.id}.jpg"
                file.save("./" + url_for("static", filename=out_file_name)[1:])
            db_sess.commit()
    return redirect('/')


@app.route('/')
def index():
    db_sess = db_session.create_session()
    reviews = db_sess.query(Review).all()
    return render_template('index.html', reviews=reviews)


@app.route('/review_add', methods=['GET', 'POST'])
@login_required
def review_add():
    form = ReviewForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        review = Review(
            author_id = current_user.id,
            title = form.title.data,
            text = form.text.data
        )
        db_sess.add(review)
        db_sess.commit()
        return redirect("/")
    return render_template('review_add.html', form=form, title="Добавление отзыва")


@app.route('/review_edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def review_edit(review_id):
    form = ReviewForm()
    db_sess = db_session.create_session()
    review = db_sess.query(Review).get(review_id)
    if review and review.author_id == current_user.id:
        if request.method == 'GET':
            form.title.data = review.title
            form.text.data = review.text
            return render_template('review_add.html', form=form, title='Редактирование отзыва')
        if form.validate_on_submit():
            review.title = form.title.data
            review.text = form.text.data
            db_sess.commit()
        return redirect(f"/review/{review.id}")
    return render_template('review_add.html', form=form)
        

@app.route('/review_add_photo/<int:review_id>', methods=['GET', 'POST'])
@login_required
def review_add_photo(review_id):
    form = PhotoForm()
    db_sess = db_session.create_session()
    review = db_sess.query(Review).get(review_id)
    if review and review.author_id == current_user.id:
        if request.method == 'GET':
            return render_template('photo_add.html', form=form, title='Добавление фото')
        if form.validate_on_submit():
            photo = Photo(
                review_id = review_id
            )
            db_sess.add(photo)
            db_sess.commit()

            out_file_name = f"img/photo_for_id_{photo.id}.jpg"
            if form.photo.data:
                request.files[form.photo.name].save("./" + url_for("static", filename=out_file_name)[1:])
    return redirect(f"/review/{review_id}")


@app.route('/review_photo_del/<int:photo_id>')
@login_required
def review_photo_del(photo_id):
    db_sess = db_session.create_session()
    photo = db_sess.query(Photo).get(photo_id)
    if photo:
        review = db_sess.query(Review).filter(Review.id == photo.review_id).first()
        if review and review.author_id == current_user.id:
            fname = f"./static/img/photo_for_id_{photo_id}.jpg"
            if os.path.isfile(fname):
                os.remove(fname)
            db_sess.delete(photo)
            db_sess.commit()
            return redirect(f"/review/{review.id}")
    return redirect("/")


@app.route('/review_del/<int:review_id>')
@login_required
def review_del(review_id):
    db_sess = db_session.create_session()
    review = db_sess.query(Review).get(review_id)
    if review and review.author_id == current_user.id:
        for comment in db_sess.query(Comment).filter(review_id == Comment.review_id).all():
            db_sess.delete(comment)
        for photo in db_sess.query(Photo).filter(review_id == Photo.review_id).all():
            fname = f"./static/img/photo_for_id_{photo.id}.jpg"
            if os.path.isfile(fname):
                os.remove(fname)
            db_sess.delete(photo)
        db_sess.delete(review)
        db_sess.commit()
    return redirect("/")
    

@app.route('/review/<int:review_id>')
@login_required
def review(review_id):
    db_sess = db_session.create_session()
    review = db_sess.query(Review).get(review_id)
    if review:
        comments = db_sess.query(Comment).filter(Comment.review_id == review.id).all()
        photos = db_sess.query(Photo).filter(Photo.review_id == review.id).all()
        return render_template('review.html', title='Просмотр отзыва', review=review, comments=comments, photos=photos)
    return redirect("/")
    

@app.route('/comment_add/<int:review_id>', methods=['GET', 'POST'])
@login_required
def comment_add(review_id):
    form = CommentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comment = Comment(
            author_id = current_user.id,
            review_id = review_id,
            text = form.text.data
        )
        db_sess.add(comment)
        db_sess.commit()
        return redirect(f"/review/{review_id}")
    return render_template('comment_add.html', form=form, title='Добавление комментария')


@app.route('/comment_del/<int:comment_id>')
@login_required
def comment_del(comment_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).get(comment_id)
    if comment and comment.author_id == current_user.id:
        db_sess.delete(comment)
        db_sess.commit()
        return redirect(f"/review/{comment.review_id}")
    return redirect("/")


@app.route('/comment_edit/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def comment_edit(comment_id):
    form = CommentForm()
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).get(comment_id)
    if comment and comment.author_id == current_user.id:
        if request.method == 'GET':
            form.text.data = comment.text
            return render_template('comment_add.html', form=form, title='Редактирование комментария')
        if form.validate_on_submit():
            comment.text = form.text.data
            db_sess.commit()
        return redirect(f"/review/{comment.review_id}")
    return render_template('comment_add.html', form=form)

    

if __name__ == '__main__':
    db_session.global_init("db/reviews.db")
    app.run(host="0.0.0.0", port=8080)