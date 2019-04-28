# Copyright (C) 2017 Kevin McKenzie.
#
# Code may not be copied, reused,  or modified in any way without written
# consent from Kevin McKenzie.

import os
from google.cloud import firestore, storage

PROJECT = "kjtmckenzie-home-fs"
CONFIG_BUCKET = 'kjtmckenzie-home-fs-config'
PROD_FLASK_SECRET = "flask_secret.txt"
DEV_FLASK_SECRET = "dev_flask_secret.txt"
FIREGASE_API_KEY = "firebase_api_key.txt"
PROVIDERS = "google,email"
UPLOAD_BUCKET = "kjtmckenzie-home-fs.appspot.com"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def get_secret(filename):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(CONFIG_BUCKET)
    blob = bucket.get_blob(filename)
    return blob.download_as_string()

def init(app):
    app.config['db'] = firestore.Client(project=PROJECT)
    
    app.config['FIREBASE_PROJECT_ID'] = PROJECT
    app.config['FIREBASE_AUTH_SIGN_IN_OPTIONS'] = PROVIDERS

    if os.getenv('GAE_ENV', '').startswith('standard'):
        app.secret_key = get_secret(PROD_FLASK_SECRET)
        app.config['FIREBASE_API_KEY'] = get_secret(FIREGASE_API_KEY)
        app.config['IS_DEV'] = False
        app.debug = False
        app.config['UPLOAD_BUCKET'] = UPLOAD_BUCKET
    else:
        app.config['IS_DEV'] = True
        app.config['FIREBASE_API_KEY'] = "dev"
        app.secret_key = open(DEV_FLASK_SECRET, 'rb').read()
        app.debug = True
        app.config['UPLOAD_BUCKET'] = "dev_uploads"

       
