# Copyright (C) 2017 Kevin McKenzie.
#
# Code may not be copied, reused,  or modified in any way without written
# consent from Kevin McKenzie.

import os
from google.cloud import firestore

PROJECT = "kjtmckenzie-home-fs"
PROVIDERS = "google,email"
FIREBASE_API_KEY = 'AIzaSyD4Q3PltZ6qSYlNWDv2P3ekDIqwwv-nMaI'

UPLOAD_BUCKET = "kjtmckenzie-home-fs.appspot.com"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def init(app):
    app.secret_key = open("flask_secret.txt", 'rb').read()
    app.config['db'] = firestore.Client(project=PROJECT)

    app.config['FIREBASE_API_KEY'] = FIREBASE_API_KEY
    app.config['FIREBASE_PROJECT_ID'] = PROJECT
    app.config['FIREBASE_AUTH_SIGN_IN_OPTIONS'] = PROVIDERS

    if os.getenv('GAE_ENV', '').startswith('standard'):
        app.config['IS_DEV'] = False
        app.debug = False
        app.config['UPLOAD_BUCKET'] = UPLOAD_BUCKET
    else:
        app.config['IS_DEV'] = True
        app.debug = True
        app.config['UPLOAD_BUCKET'] = "dev_uploads"

       
