#!/usr/bin/env python

# Copyright (C) 2019 Kevin McKenzie.

import logging, os
from models_fs import Album, User
from settings import init
import admin, photography, utils
from flask_firebase import FirebaseAuth
from flask_login import LoginManager, login_user, logout_user, login_required
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
init(app)

# Set up Firebase authentication
auth = FirebaseAuth(app)
login_manager = LoginManager(app)

# Establish blueprints for website routing
app.register_blueprint(auth.blueprint, url_prefix='/auth')
app.register_blueprint(photography.blueprint)
app.register_blueprint(admin.blueprint)
app.register_blueprint(utils.blueprint)

# Add firebase user loaders and login/logout pages
@auth.production_loader
def production_sign_in(token):
    account = User.get(firebaseID=token['sub'])
    if account is None:
        account = User(token['email'], token['sub'])
        account.put()
    login_user(account)


@auth.development_loader
def development_sign_in(email):
    account = User.get(email=email)
    if account is None:
        account = User(email=email, firebaseID=None, admin=True)
        account.put()
    login_user(account)


@auth.unloader
def sign_out():
    logout_user()


@login_manager.user_loader
def load_user(account_id):
    return User.get(email=account_id)


@login_manager.unauthorized_handler
def authentication_required():
    return redirect(auth.url_for('widget', mode='select', next=request.url))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    albums = Album.active_albums()
    context = {'albums': [] if albums is None else albums}
    return render_template('index.html', context=context)


# Attempt to load the cloud debugger
try:
    import googleclouddebugger
    googleclouddebugger.enable()
except ImportError:
    pass


# used only in development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
