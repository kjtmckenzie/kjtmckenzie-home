# Copyright (C) 2017 Kevin McKenzie.
#
# Code may not be copied, reused,  or modified in any way without written
# consent from Kevin McKenzie.

import logging
from models_fs import Album
from settings import init
from flask import (
    Flask,
    render_template,
    redirect,
    Blueprint
)

app = Flask(__name__)
init(app)

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

