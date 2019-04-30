# Copyright (C) 2019 Kevin McKenzie.

import logging
import os
from models_fs import Album
from flask import render_template, redirect, Blueprint
from flask import Flask, send_from_directory, redirect, url_for

app = Flask(__name__)
blueprint = Blueprint('utils', __name__)


@blueprint.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@blueprint.route('/dev_uploads/<path:path>')
def dev_uploads(path):
    if app.config['IS_DEV']:
        return send_from_directory(os.path.join(app.root_path, 'dev_uploads'), path)
    else:
        logging.exception('URL only available in dev environment')
        return 'URL only available in dev environment', 500


@blueprint.errorhandler(500)
def server_error(e):
    logging.exception('An error has occurred')
    return 'An error has occurred on the server', 500
