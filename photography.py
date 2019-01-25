# Copyright (C) 2017 Kevin McKenzie.
#
# Code may not be copied, reused,  or modified in any way without written
# consent from Kevin McKenzie.

import logging
import models
from models import Album, CoverImage

from flask import (
    Flask,
    render_template,
    flash,
    redirect
)

import flask
from settings import init

app = Flask(__name__)
init(app)

@app.route('/photography/', defaults={'path': ''})
@app.route('/photography/<path:path>')
def index(path):

    if len(path) > 0:
        album = Album.get(path)
        if album is None:
            return redirect("./")
        photos = Album.photos(album.title)
        context = {
            'album': album,
            'photos': photos
        }

        return render_template('album.html', context=context)

    albums = Album.active_albums()

    album_list = []

    for album in albums:
        album_dict = {}
        album_dict["album"] = album
        album_dict["cover"] = CoverImage.get(album.title)
        album_dict["urlsafe"] = album.key.urlsafe()

        album_list.append(album_dict)

    context = {
        'albums' : album_list
    }

    logging.info("context")
    logging.info(str(context))

    return render_template('photography.html', context=context)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error has occurred')

    return 'An error has occurred on the server', 500
