# Copyright (C) 2017 Kevin McKenzie.
#
# Code may not be copied, reused,  or modified in any way without written
# consent from Kevin McKenzie.

from werkzeug.utils import secure_filename
from google.cloud import storage
import datetime
import six
from settings import init
from flask import Flask
import os

from google.api_core.exceptions import NotFound

app = Flask(__name__)
init(app)


def _safe_filename(filename):
    """
    Generates a safe filename that is unlikely to collide with existing objects
    in Google Cloud Storage.

    ``filename.ext`` is transformed into ``filename-YYYY-MM-DD-HHMMSS.ext``
    """
    filename = secure_filename(filename)
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
    basename, extension = filename.rsplit('.', 1)
    return "{0}-{1}.{2}".format(basename, date, extension)


def upload_file(file, folder, make_public=True):
    """
    Uploads a file to a given Cloud Storage bucket and returns the public url
    to the new object.
    """

    if not file:
        return None

    filename = _safe_filename(file.filename)

    if app.config['IS_DEV']:
        file.save(os.path.join(app.config['UPLOAD_BUCKET'], folder, filename))
        url = "/uploads/" + filename
    else:
        client = storage.Client()
        bucket = client.bucket(app.config['UPLOAD_BUCKET'])
        blob = bucket.blob(folder + filename)

        try: 
            blob.upload_from_string(
                file.read(),
                content_type=file.content_type)
        except NotFound:
            raise NotFound("Could not upload file, bucket or folder %s does not exist" %
                           (app.config['UPLOAD_BUCKET'] + folder))

        if make_public:
            blob.make_public()

        url = blob.public_url

    if isinstance(url, six.binary_type):
        url = url.decode('utf-8')

    return url
