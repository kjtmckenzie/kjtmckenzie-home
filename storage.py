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

app = Flask(__name__)
init(app)

'''
def is_local():
    return local_run()

def base_url():
    if local_run():
        return local_api_url()
    return "https://storage.googleapis.com"


BUCKET_NAME = os.environ.get('BUCKET_NAME',
                       app_identity.get_default_gcs_bucket_name())


def write(filename, content_type, content, public=True):
    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    options = {}
    if public:
        options = {'x-goog-acl': 'public-read'}

    gcs_file = gcs.open(filename,
                      'w',
                      content_type=content_type,
                      options=options,
                      retry_params=write_retry_params)

    gcs_file.write(content)
    gcs_file.close()


def read_file(filename):
    gcs_file = gcs.open(filename)
    result = gcs_file.read()
    gcs_file.close()
    return result

def upload_file_to_gcs(uploaded_file, foldername):
    file_name = '/{0}/{1}/{2}'.format(BUCKET_NAME,
                foldername,
                secure_filename(uploaded_file.filename))
    write(file_name, uploaded_file.content_type, uploaded_file.read())
    return file_name
'''


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


def upload_file(file, folder):
    """
    Uploads a file to a given Cloud Storage bucket and returns the public url
    to the new object.
    """

    if not file:
        return None

    filename = _safe_filename(file.filename)

    if app.config['IS_DEV']:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        url = "/uploads/" + filename
    else:
        client = storage.Client()
        bucket = client.bucket(app.BUCKET_NAME + folder)
        blob = bucket.blob(filename)

        blob.upload_from_string(
            file.read(),
            content_type=file.content_type)

        url = blob.public_url

    if isinstance(url, six.binary_type):
        url = url.decode('utf-8')


    print("URL of uploaded file: %s" % str(url))

    return url