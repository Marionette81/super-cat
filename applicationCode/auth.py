import flask
import requests

#import google.oauth2.credentials
#import google_auth_oauthlib.flow
#import googleapiclient.discovery

import os
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from applicationCode.db import get_db #Windows
from . import envoi_mail #Windows
#import db #MAC
#from db import get_db #MAC
#import envoi_mail # MAC
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['DEBUG'] = '1'



# Création d'un blueprint nommé "auth", associé à l'URL /auth
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Cette variable spécifie le nom du fichier contenant les informations OAuth 2.0 pour l'application, y compris son client_id et son client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

app = flask.Flask(__name__)

app.secret_key = 'ljgjhkgl'


# Formulaire d'inscription à remplir pour créer son compte sur l'application
@bp.route('/inscription_envoi_code', methods=('GET', 'POST'))
def inscription_envoi_code():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        nom_doodle = request.form['nom_doodle']
        mail = request.form['mail']
        db = get_db()
        error = None

        if not username:
            error = 'Veuillez entrer un nom d\'utilisateur.'
        elif not password:
            error = 'Veuillez entrer un mot de passe pour votre compte.'
        elif not nom_doodle:
            error = 'Veuillez entrer un nom pour le remplissage des sondages Doodle.'
        elif not mail:
            error = 'Veuillez entrer une adresse mail.'
        elif not envoi_mail.verif_mail(mail):
            error = 'Veuillez entrer une adresse mail valide.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
            ).fetchone() is not None:
            error = 'L\'utilisateur {} existe déjà.'.format(username)
        elif db.execute(
            'SELECT mail FROM user WHERE mail = ?', (mail,)
            ).fetchone() is not None:
            error = "Un compte est déjà associé à l'adresse mail : {}".format(mail)

        if error is not None:
            flash(error)

        else:
            code = envoi_mail.code_verification(mail)
            return render_template('verification_mail_inscription.html', username=username, password=password, nom_doodle=nom_doodle, mail=mail, code=code)

    return render_template('inscription.html')

# 
@bp.route('/<string:username>/<string:password>/<string:nom_doodle>/inscription_renvoi_code', methods=('GET', 'POST'))
def inscription_renvoi_code(username, password, nom_doodle):
    # On récupère la nouvelle adresse mail
    if request.method == 'POST':
        mail= request.form['nouv_mail']
        db = get_db()
        error = None

        if not mail:
            error = 'Veuillez entrer une adresse mail.'
        elif db.execute(
            'SELECT mail FROM user WHERE mail = ?', (mail,)
            ).fetchone() is not None:
            error = "Un compte est déjà associé à l'adresse mail : {}".format(mail)

        if error is not None:
            flash(error)

        else:
            code = envoi_mail.code_verification(mail)
            return render_template('verification_mail_inscription.html', username=username, password=password, nom_doodle=nom_doodle, mail=mail, code=code)

    return render_template('verification_mail_inscription.html', username=username, password=password, nom_doodle=nom_doodle, mail=mail, code=code)


# 
@bp.route('/<string:username>/<string:password>/<string:nom_doodle>/<string:mail>/<string:code>/inscription_finalisation', methods=('GET', 'POST'))
def inscription_finalisation(username, password, nom_doodle, mail, code):
    # On récupère le code de vérification
    if request.method == 'POST':
        code_verif= request.form['code_verif']
        db = get_db()
        error = None

        if code_verif is None:
            error = "Veuillez rentrer le code de vérification"
        elif code != code_verif:
            error = "Le code est erroné"

        if error is not None:
            flash(error)
        else:
            db.execute(
                'INSERT INTO user (username, password, nom_doodle, mail) VALUES (?, ?, ?, ?)',
                (username, generate_password_hash(password), nom_doodle, mail)
                )
            db.commit()
            return redirect(url_for('auth.login'))
    return render_template('verification_mail_inscription.html', username=username, password=password, nom_doodle=nom_doodle, mail=mail, code=code)

    

# Vue pour se connecter à l'application
@bp.route('/login', methods=('GET', 'POST'))
def login():
    error = None
    db = get_db()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Nom d\'utilisateur incorrect.'
        elif not check_password_hash(user['password'], password):
            error = 'Mot de passe incorrect.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']

            return redirect(url_for('page_principale'))

        flash(error)

    return render_template('login.html')


@bp.route('/identifiants_oublies', methods=('GET', 'POST'))
def identifiants_oublies():
    error=None
    db = get_db()
    if request.method == 'POST':
        # On récupère la clé du sondage
        mail = request.form['mail']

        if not mail:
            error = 'Veuillez entrer votre adresse mail.'
        elif not envoi_mail.verif_mail(mail):
            error = 'Veuillez entrer une adresse mail valide.'
        # On vérifie que l'adresse mail est associée à un compte
        elif db.execute( 
            'SELECT mail FROM user WHERE mail = ?', (mail,)
            ).fetchone() is None:
            error = "Il n'y a pas de compte associé à l'adresse mail : {}.".format(mail)

        if error is not None:
            flash(error)
        else:
            nom_utilisateur= (db.execute(
                                    'SELECT username FROM user WHERE mail = ?', (mail,)
                                    ).fetchone())['username']
            nouv_mdp = envoi_mail.mot_de_passe_oublie(mail,nom_utilisateur)
            db.execute(
                'UPDATE user SET password = ?'
                ' WHERE mail = ?',
                (generate_password_hash(nouv_mdp), mail)
            )   
            db.commit()
            return redirect(url_for('auth.login'))

    return render_template('mot_de_passe_oublie.html')


@bp.route('/revoke')
def revoke():
##  if 'credentials' not in flask.session:
##    return ('You need to <a href="/authorize">authorize</a> before ' +
##            'testing the code to revoke credentials.')
##
##  credentials = google.oauth2.credentials.Credentials(
##    **flask.session['credentials'])
##
##  revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
##      params={'token': credentials.token},
##      headers = {'content-type': 'application/x-www-form-urlencoded'})
##
##  status_code = getattr(revoke, 'status_code')
  session.clear()
  return redirect(url_for('auth.login'))



# Identifie si un utilisateur est connecté dans la session.
# Permet d'ouvrir les pages accessibles seulement par des utilisateurs et d'acceder aux données de leur compte
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# Page pour se déconnecter
@bp.route('/logout')
def logout():

    return redirect(url_for('auth.revoke'))

# Certaines fonctionnalités requierent d'être connecté à un compte pour être utilisées
# On redirige donc vers la page d'identification login
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
