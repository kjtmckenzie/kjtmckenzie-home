# Copyright (C) 2017 Kevin McKenzie.
#
# Code may not be copied, reused,  or modified in any way without written
# consent from Kevin McKenzie.

import logging
from models import Album, CoverImage

from flask import (
    Flask,
    render_template,
    flash
)

import flask
from settings import init

app = Flask(__name__)
init(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    albums = Album.active_albums()

    album_list = []

    for album in albums:
        try:
            album_dict = {
                "album": album,
                "cover": CoverImage.get(album.title)
            }
            album_list.append(album_dict)
        except:
            logging.info("Invalid album: %s" % str(album))

    context = {
        'albums' : album_list
    }

    return render_template('index.html', context=context)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error has occurred')

    return 'An error has occurred on the server', 500



if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)