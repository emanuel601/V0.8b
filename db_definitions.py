from flask import Flask
from flask_sqlalchemy import SQLAlchemy, query
from sqlalchemy.orm import relationship
from flask_login import UserMixin
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///all_cars.db'
app.config['SQLALCHEMY_BINDS'] = {'db2': 'sqlite:///users.db', 'db3': 'sqlite:///url_images.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv('RECAPTCHA_PUBLIC_KEY')  # <-- Add your site key
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv('RECAPTCHA_PRIVATE_KEY')  # <-- Add your secret key
db = SQLAlchemy(app)
key = os.getenv('API-KEY')

# CREATE TABLE IN DB
class CarBrand(db.Model):
    __tablename__ = 'All_brands'
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.String(100), unique=True)
    marca = db.Column(db.String(100))
    children = relationship("CarModel", back_populates="parent")


# CREATE TABLE IN DB
class CarModel(db.Model):
    __tablename__ = 'All_cars'
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    cantidad = db.Column(db.Integer)
    parent_id = db.Column(db.Integer, db.ForeignKey("All_brands.id"))
    parent = relationship("CarBrand", back_populates="children")
    versions = relationship("CarVersion", back_populates="model")


class CarVersion(db.Model):
    __tablename__ = 'version'
    id = db.Column(db.Integer, primary_key=True)
    model = relationship("CarModel", back_populates="versions")
    car_id = db.Column(db.Integer, db.ForeignKey("All_cars.car_id"))
    version_id = db.Column(db.String(100))
    version = db.Column(db.String(100))
    cantidad = db.Column(db.Integer)
    years = db.Column(db.String(100))

## BLOG DB

class User(db.Model, UserMixin):
    __bind_key__ = 'db2'
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False, unique=True)
    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")


    ##  CONFIGURE TABLES

class BlogPost(db.Model):
    __bind_key__ = 'db2'
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments_children = relationship("Comment", back_populates="post_commented")


class Comment(db.Model):
    __bind_key__ = 'db2'
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    post_commented = relationship("BlogPost", back_populates="comments_children")

## IMAGES DB


class ImageDataBase(db.Model):
    __bind_key__ = 'db3'
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    q_image = db.Column(db.Text, nullable=False)
    url_image = db.Column(db.Text, nullable=False)
