# Copyright (C) 2017 Kevin McKenzie.
#
# Code may not be copied, reused,  or modified in any way without written
# consent from Kevin McKenzie.

import os

WEB_CLIENT_ID = os.getenv('WEB_CLIENT_ID')
IS_APP_ENGINE_ENV = os.getenv('SERVER_SOFTWARE') and os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')

def init(app):
    app.debug = not IS_APP_ENGINE_ENV
    app.secret_key = open("flask_secret.txt", 'rb').read()









