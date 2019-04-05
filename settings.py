# Copyright (C) 2017 Kevin McKenzie.
#
# Code may not be copied, reused,  or modified in any way without written
# consent from Kevin McKenzie.

import os
from google.cloud import firestore

PROJECT = "kjtmckenzie-home-fs"

UPLOAD_BUCKET = 'gs://' + PROJECT
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def init(app):
    app.secret_key = open("flask_secret.txt", 'rb').read()
    app.config['db'] = firestore.Client(project=PROJECT)

    if os.getenv('GAE_ENV', '').startswith('standard'):
        app.config['IS_DEV'] = False
        app.debug = False
        app.config['UPLOAD_FOLDER'] = UPLOAD_BUCKET
    else:
        app.config['IS_DEV'] = True
        app.debug = True
        app.config['UPLOAD_FOLDER'] = ""  # just post to /images/

       
