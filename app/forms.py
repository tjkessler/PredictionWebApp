from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    '''
    Flask form used for login
    '''

    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign in')


class RegistrationForm(FlaskForm):
    '''
    Flask form used for registration
    '''

    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )
    email_conf = StringField(
        'Verify Email',
        validators=[DataRequired(), Email(), EqualTo('email')]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    password_conf = PasswordField(
        'Verify Password',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Register')

    def validate_email(self, email):
        if '.gov' and '.edu' not in email.data.lower():
            raise ValidationError(
                'Only .gov and .edu emails can be used at this time.'
            )
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError('Email already in use!')


class ResetPasswordRequestForm(FlaskForm):
    '''
    Flask form for requesting a password reset
    '''

    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    '''
    Flask form for resetting a password
    '''

    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    password_conf = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Reset Password')


class SubmitMoleculeForm(FlaskForm):
    '''
    Flask form for submitting SMILES strings
    '''

    smiles = TextAreaField(
        'Enter SMILES code(s), one per line:',
        validators=[DataRequired()]
    )
    submit = SubmitField('Predict Cetane Number')
