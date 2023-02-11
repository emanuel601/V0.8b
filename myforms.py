from flask_wtf import FlaskForm, RecaptchaField
from db_definitions import db, CarBrand, app
from wtforms import SelectField, SubmitField, StringField, EmailField, PasswordField
# from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import DataRequired, EqualTo, URL, Email
from flask_ckeditor import CKEditorField, CKEditor

from flask_gravatar import Gravatar


class ConsultPrice(FlaskForm):
    marca = SelectField('Marca', validators=[DataRequired('seleccione una marca')])
    modelo = SelectField('Modelo', default=None, validate_choice=False)
    version = SelectField('Versión', default=None, validate_choice=False)
    year = SelectField('Año', default=None, validate_choice=False)
    recaptcha = RecaptchaField()

    submit = SubmitField('enviar')

    def __init__(self):
        super(ConsultPrice, self).__init__()

        with app.app_context():
            lista = db.session.query(CarBrand).all()
            lista = [(item.brand_id, item.marca) for item in lista]
            self.marca.choices = lista


# forms to login/register

class CreateUser(FlaskForm):
    user = StringField("Usuario", validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField('Repetí la contraseña', validators=[EqualTo('password')])
    recaptcha = RecaptchaField()
    submit = SubmitField('Registrarse')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Ingresar')

# Blog forms

class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class CommentForm(FlaskForm):
    comment = CKEditorField('comment', validators=[DataRequired()])
    submit = SubmitField('submit')


ckeditor = CKEditor(app)

gravatar = Gravatar(app,
                    size=30,
                    rating='g', default='retro', force_default=False, force_lower=True, use_ssl=False, base_url=None)

# Contact Form


class ContactForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired()])
    mail = EmailField("Email", validators=[DataRequired(), Email()])
    subject = StringField("Motivo de la Consulta", validators=[DataRequired()])
    message = StringField("Mensaje", validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Enviar Mensaje')
