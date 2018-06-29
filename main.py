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
                "cover": CoverImage.get(album.title),
                "images": Album.photos(album.title)
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
