from app import app
from app import db
from app.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm
from app.forms import ResetPasswordForm, SubmitMoleculeForm
from app.models import User
from app.email import send_password_reset_email
from app.auto_predict import predict_from_web
from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from threading import Thread


@app.before_request
def before_request():
    '''
    Checks to see if user is already logged in, logs last seen time
    '''

    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
@app.route('/index')
def index():
    '''
    Main page
    '''

    return render_template('index.html')


@app.route('/launch', methods=['GET', 'POST'])
@login_required
def launch():
    '''
    Launch (predict) page; redirects to index if user not logged in
    '''

    form = SubmitMoleculeForm()
    if form.validate_on_submit():
        allowed_chars = [
            'C', 'c', 'h', 'H',
            'N', 'n', 'Na', 'na',
            'O', 'o', 'B', 'b',
            'P', 'p', 'Cl', 'cl',
            'Br', 'br', 'I', 'i',
            '.', '-', '=', '#',
            '$', ':', '/', '\\',
            '(', ')', '\n', '\r'
        ]
        for char in range(0, len(form.smiles.data)):
            if form.smiles.data[char] not in allowed_chars:
                try:
                    if int(form.smiles.data[char]):
                        continue
                except:
                    try:
                        if form.smiles.data[char] + form.smiles.data[char+1]\
                                not in allowed_chars:
                            flash('Invalid SMILES format')
                            return redirect(url_for('launch'))
                        else:
                            continue
                    except:
                        flash('Invalid SMILES character: {}'.format(char))
                        return redirect(url_for('launch'))
        mol_count = 0
        for char in range(0, len(form.smiles.data)):
            if form.smiles.data[char] == '\r':
                mol_count += 1
        if mol_count > 50:
            flash('Error: maximum submissions allowed = 50')
            return render_template('launch.html', title='Launch', form=form)
        th = Thread(
            target=predict_from_web.predict,
            args=(current_user.email, form.smiles.data,)
        )
        th.start()
        flash('Results will be emailed to {}'.format(current_user.email))
        return render_template('launch.html', title='Launch', form=form)
    return render_template('launch.html', title='Launch', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Login page; once logged in, redirects to page visited before
    '''

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Log In', form=form)


@app.route('/logout')
def logout():
    '''
    Logs out the user, redirects to index
    '''

    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Registration page; if already logged in, redirects to home. After
    registration, redirects to login.
    '''

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    '''
    Password reset request page; after form data is populated, redirects to
    login page
    '''

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template(
        'reset_password_request.html',
        title='Reset Password',
        form=form
    )


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    '''
    Tokenized password reset page; after password is changed, redirects to
    login page
    '''

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template(
        'reset_password.html',
        title='Reset Password',
        form=form
    )
