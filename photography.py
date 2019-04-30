# Copyright (C) 2019 Kevin McKenzie.

import logging
from models_fs import Album
from flask import render_template, redirect, Blueprint

blueprint = Blueprint('photography', __name__)

@blueprint.route('/photography/', defaults={'path': ''})
@blueprint.route('/photography/<path:path>')
def photography(path):
    if len(path) > 0:
        album = Album.get(path)
        if album is None:
            return redirect("./")
        photos = album.photos()
        context = {
            'album': album,
            'photos': photos
        }

        return render_template('album.html', context=context)

    albums = Album.active_albums()
    albums = [] if albums is None else albums

    context = {
        'albums': albums
    }

    return render_template('photography.html', context=context)

