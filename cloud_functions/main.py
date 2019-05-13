# Copyright (C) 2019 Kevin McKenzie.

import os
import tempfile
from google.cloud import storage, firestore
from wand.image import Image
from retrying import retry
import google.api_core
import logging

storage_client = storage.Client()
destination_bucket = 'kjtmckenzie-home-fs-thumbnails'
PROJECT = "kjtmckenzie-home-fs"


def retry_if_service_unavailable_error(exception):
    """Return True if we should retry (in this case when it's an ServiceUnavailable), False otherwise"""
    return isinstance(exception, google.api_core.exceptions.ServiceUnavailable)


# Update Firestore album to use the thumbnail as the cover image
@retry(wait_exponential_multiplier=100, wait_exponential_max=2000, retry_on_exception=retry_if_service_unavailable_error)
def update_album_cover_with_thumbnail(url, thumbnail_url):
    db = firestore.Client(project=PROJECT)
    album = next(db.collection('Albums').where('cover', '==', url).get(), None)
    album_ref = db.collection('Albums').document(album.id)
    album_ref.update({'cover': thumbnail_url})
    

# [START functions_imagemagick_analyze]
def thumbnail_image(data, context):
    file_data = data

    file_name = file_data['name']

    # only create thumbnails for images in the "covers" album
    if not file_name.startswith("covers/"):
        return

    bucket_name = file_data['bucket']

    blob = storage_client.bucket(bucket_name).get_blob(file_name)

    logging.info(f'Thumbnailing {file_name}.')
    _, temp_local_filename = tempfile.mkstemp()

    # Download file from bucket.
    blob.download_to_filename(temp_local_filename)

    # Resize the image using ImageMagick.
    with Image(filename=temp_local_filename) as image:
        image.transform(resize='640x480>')
        image.save(filename=temp_local_filename)

    logging.info(f'Image {file_name} was resized.')

    new_file_name = f'{file_name}'.replace("covers/", "")
    destination_blob = storage_client.bucket(destination_bucket).blob(new_file_name)
    destination_blob.upload_from_filename(temp_local_filename)
    destination_blob.make_public()
    logging.info(f'Resized image was uploaded to {new_file_name}.')

    # Delete the temporary file.
    os.remove(temp_local_filename)

    # update firestore record with public URL for thumbnail
    url = blob.public_url
    thumbnail_url = destination_blob.public_url

    try:
        update_album_cover_with_thumbnail(url, thumbnail_url)
        logging.info(
            f'Set Album with cover {url} to have a thumbnail with url {thumbnail_url}')
    except:
        logging.error(
            f'Failed to set album with cover {url} to have a thumbnail with url {thumbnail_url}')
    

# used only in development
if __name__ == '__main__':
    data = {
        'bucket': 'kjtmckenzie-home-fs.appspot.com',
        'name': 'covers/cover-grand-canyon-2019-05-08-202636.jpg'
    }
    thumbnail_image(data, None)
