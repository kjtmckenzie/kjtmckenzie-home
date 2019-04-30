# Copyright (C) 2019 Kevin McKenzie.

from werkzeug.utils import secure_filename
from google.cloud import storage
import datetime
import six
import os

from google.api_core.exceptions import NotFound

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


def upload_file(file, folder, upload_bucket, make_public=True, is_dev=False):
    """
    Uploads a file to a given Cloud Storage bucket and returns the public url
    to the new object.
    """

    if not file:
        return None

    filename = _safe_filename(file.filename)

    if is_dev:
        file.save(os.path.join(upload_bucket, filename))
        url = "/" + upload_bucket + "/" + filename
    else:
        client = storage.Client()
        bucket = client.bucket(upload_bucket)
        blob = bucket.blob(folder + filename)

        try: 
            blob.upload_from_string(
                file.read(),
                content_type=file.content_type)
        except NotFound:
            raise NotFound("Could not upload file, bucket or folder %s does not exist" %
                           (upload_bucket + folder))

        if make_public:
            blob.make_public()

        url = blob.public_url

    if isinstance(url, six.binary_type):
        url = url.decode('utf-8')

    return url
