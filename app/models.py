from app import db
from app import login
from app import app
from time import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.String(128))

    def set_password(self, password):
        '''
        Creates hash from plaintext user password

        Args:
            password (str): plaintext user password
        '''

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        '''
        Checks if supplied password equals the user's hashed password

        Args:
            password (str): plaintext user password
        '''

        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def get_reset_password_token(self, expires_in=600):
        '''
        Creates token for resetting a user's password

        Args:
            expires_in (int): window for password reset, in seconds

        Returns:
            str: token for user password reset
        '''

        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256'
        ).decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        '''
        Verifies password reset token

        Args:
            token (str): token for user password reset

        Returns:
            User: queried user if token verification is successful
        '''

        try:
            id = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=['HS256']
            )['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    '''
    Loads a user

    Args:
        id (str or int): id of the user

    Returns:
        User: queried user
    '''

    return User.query.get(int(id))
