from functools import wraps

import googleapiclient.errors
from flask import render_template, request, url_for, redirect, jsonify, flash, abort
from flask_bootstrap import Bootstrap
from db_definitions import CarBrand, CarModel, CarVersion, User, BlogPost, Comment
from db_definitions import db, app
from price_calculator import calc_price
from myforms import ConsultPrice, CreateUser, LoginForm, CreatePostForm, CommentForm, ContactForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from imagesearch import image_search, fulfill_carrousel, fulfill_images_db
from datetime import date
from notification_manager import NotificationManager


Bootstrap(app)
login_manager = LoginManager()

with app.app_context():
    # db.init_app(app)
    login_manager.init_app(app)
    # db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.get_id() != '1':
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def home():
    posts = BlogPost.query.all()
    images_carrousel = fulfill_carrousel()
    # images_all_cars = fulfill_images_db()
    return render_template("index.html", logged_in=current_user.is_authenticated, posts=posts,
                           images_carrousel=images_carrousel)


@app.route('/cars', methods=['GET', 'POST'])
def cars():
    form = ConsultPrice()
    # print(form.marca.data)
    if request.method == 'POST':
        brand_validation = CarBrand.query.filter_by(brand_id=form.marca.data).first()
        form.marca.choices = [(brand_validation.brand_id, brand_validation.marca)]

        model_validation = CarModel.query.filter_by(car_id=form.modelo.data).first()
        form.modelo.choices = [(model_validation.car_id, model_validation.modelo)]

        version_validation = CarVersion.query.filter_by(version_id=form.version.data).first()
        form.version.choices = [(version_validation.version_id, version_validation.version)]

        cars_years_validation = CarVersion.query.filter_by(car_id=form.modelo.data).all()
        for car in cars_years_validation:
            if car.version_id == form.version.data:
                years_validation = eval(car.years)

        form.year.choices = [{'year': key for (key, value) in year.items()} for year in years_validation]

        if form.validate_on_submit():
            model = form.modelo.data
            brand = form.marca.data
            version = form.version.data
            year = form.year.data
            # years = f'{year}-{year}'
        # print(model)
        # print(brand)

            return redirect(url_for("get_price", model=model, brand=brand, version=version, year=year))

    return render_template('cars.html', form=form, logged_in=current_user.is_authenticated)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = CreateUser()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        elif User.query.filter_by(name=form.user.data).first():
            # User already exists
            flash("There is already an user with this name, choose another please")
            return redirect(url_for('register'))

        new_user = User(
            email=form.email.data,
            password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8),
            name=form.user.data
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash(f'There is no user registered for {email}')
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
        else:
            login_user(user)
            return redirect(url_for('cars'))

    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/models_list', methods=['POST'])  # populates the form with the models of a particular brand
def models_list():
    brand_id = request.get_json()['data']
    print(brand_id)

    brand = CarBrand.query.filter_by(brand_id=brand_id).first()
    # print(brand)
    car_models = CarModel.query.filter_by(parent_id=brand.id).all()
    print(car_models)
    models_array = []

    for car_model in car_models:
        if car_model.cantidad > 1:
            car_model_obj = {'id': car_model.car_id, 'name': car_model.modelo}
            models_array.append(car_model_obj)

    return jsonify({'car_models': models_array})


@app.route('/version_list', methods=['POST'])  # populates the form with the versions of a particular model
def version_list():
    car_id = request.get_json()['car']
    car_versions = CarVersion.query.filter_by(car_id=car_id).all()
    # print(car_models)
    versions_array = []

    for car_version in car_versions:
        if car_version.cantidad > 1:
            car_versions_obj = {'id': car_version.version_id, 'name': car_version.version}
            versions_array.append(car_versions_obj)

    print(versions_array)
    return jsonify({'car_versions': versions_array})


@app.route('/year_list', methods=['POST'])  # Populates the forms with the years of models and versions
def get_year():
    car_id = request.get_json()['car']
    version_id = request.get_json()['version']
    print(car_id, version_id)
    cars = CarVersion.query.filter_by(car_id=car_id).all()
    for car in cars:
        if car.version_id == version_id:
            years = eval(car.years)

    years_list = [{'year': key for (key, value) in year.items()} for year in years]
    print(years_list)

    return jsonify({'years': years_list})


@app.route('/result/<model>/<version>/<brand>/<year>', methods=['GET', 'POST'])
def get_price(model, brand, version, year):
    print(model)
    print(brand)
    print(version)
    # print(request.get_json())
    marca = CarBrand.query.filter_by(brand_id=brand).first()
    modelo = CarModel.query.filter_by(car_id=model).first()
    versions = CarVersion.query.filter_by(car_id=modelo.car_id).all()
    for version_ in versions:
        if version_.version_id == version:
            model_version = version_.version

    model_name = modelo.modelo
    brand_name = marca.marca
    years = f'{year}-{year}'
    car_price = calc_price(brand_name, model_name, brand, model, version, years)

    price = car_price[0]
    cars = car_price[1]

    try:
        # image_banner = image_search(f'"{brand_name} {model_name}" {model_version}')
        image_banner = image_search(f'"{brand_name} {model_name}" {model_version}')
        # image_banner = image_search(f'{brand_name} logo')
    except googleapiclient.errors.HttpError:
        # image_banner = image_search(f'unknown car')
        image_banner = image_search(f'{brand_name} {model_name}')
    print(image_banner)

    return render_template('results.html', brand=brand_name, model=model_name, version=model_version, price=price,
                           years=year, logged_in=current_user.is_authenticated, background_image=image_banner)


@app.route('/blog')
def blog():
    posts = BlogPost.query.all()
    return render_template('blog.html', logged_in=current_user.is_authenticated, posts=posts)


@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_posting = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_posting)
        db.session.commit()
        return redirect(url_for("blog"))
    return render_template('make-post.html', logged_in=current_user.is_authenticated, form=form)


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    posts = BlogPost.query.all()
    new_comment = CommentForm()
    if new_comment.validate_on_submit():
        comment = Comment(text=new_comment.comment.data,
                          comment_author=current_user,
                          post_commented=requested_post)
        db.session.add(comment)
        db.session.commit()
    return render_template("blog-details.html", post=requested_post, logged_in=current_user.is_authenticated,
                           background_image=requested_post.img_url, form=new_comment, posts=posts)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        # author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        # post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, logged_in=current_user.is_authenticated)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('blog'))


@app.route("/contacto", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        mail_sender = NotificationManager()
        mail_sender.send_email(form.name.data, form.mail.data, form.subject.data, form.message.data)
        # print(form.name.data, form.mail.data, form.subject.data, form.message.data)
        return render_template("contact.html", logged_in=current_user.is_authenticated)
    return render_template("contact.html", logged_in=current_user.is_authenticated, form=form)


@app.route("/acercade")
def about():
    return render_template("about.html", logged_in=current_user.is_authenticated)


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
