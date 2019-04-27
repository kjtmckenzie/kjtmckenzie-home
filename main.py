#!/usr/bin/env python

# Copyright (C) 2017 Kevin McKenzie.
#
# Code may not be copied, reused,  or modified in any way without written
# consent from Kevin McKenzie.

import logging
from models_fs import Album, User
import os
from settings import init
import admin
import photography
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import (
    Flask,
    render_template,
    send_from_directory,
    request,
    redirect,
    url_for
)

app = Flask(__name__)
init(app)

from flask_firebase import FirebaseAuth

auth = FirebaseAuth(app)
login_manager = LoginManager(app)

app.register_blueprint(auth.blueprint, url_prefix='/auth')


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


@app.route('/admin/', methods=['POST', 'GET'])
@login_required
def render_admin():
    if not current_user.admin:
        return "User is not a site admin", 403
    return admin.render()


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/photography/', defaults={'path': ''})
@app.route('/photography/<path:path>')
def render_photography(path):
    return photography.render(path)


@app.route('/dev_uploads/<path:path>')
def dev_uploads(path):
    if app.config['IS_DEV']:
        return send_from_directory(os.path.join(app.root_path, 'dev_uploads'), path)
    else:
        logging.exception('URL only available in dev environment')
        return 'URL only available in dev environment', 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    albums = Album.active_albums()
    context = {'albums': [] if albums is None else albums}
    return render_template('index.html', context=context)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error has occurred')
    return 'An error has occurred on the server', 500


try:
    import googleclouddebugger
    googleclouddebugger.enable()
except ImportError:
    pass


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
