# Copyright (C) 2017 Kevin McKenzie.
#
# Code may not be copied, reused,  or modified in any way without written
# consent from Kevin McKenzie.

import logging
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from settings import init
from storage import upload_file_to_gcs
from google.appengine.api import users

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)

# apply our settings
init(app)

@app.route('/upload/', methods=['POST', 'GET'])
def create_image():
    '''Create an image'''

    user_signed_in = signed_in()
    logging.info("user_signed_in is %s" % str(user_signed_in))

    if not user_signed_in:
        return redirect('../login/')

    context = {}

    initialized = is_initialized()

    user_profile = get_user(users.get_current_user().email())
    given_name = user_profile['given_name']

    context = {
        'signed_in': user_signed_in,
        'given_name': given_name
    }

    if request.method == 'GET':
        return render_template('create_image.html', context=context)

    # The app.yaml file ensures that users are logged in before
    # making it to this page.
    user    = users.get_current_user()
    folder  = "public"

    if user:
        folder = user.user_id()
        user = user.email()
    else:
        user = "public"

    category = None
    if 'cat_id' in request.form:
        category = request.form['cat_id']

    # Saves the file and returns the name, minus the base URL.
    try:

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
        if allowed_file(file.filename):
            saved_file_name = upload_file_to_gcs(file, folder)
            save_uploaded_image(category=category, url=saved_file_name,
                                details=request.form['details'])
            flash('Upload Complete')
        elif len(file.filename) > 0:
            flash('File must be of type .jpg, .jpeg, or .png')
    except Exception as e:
        if "larger than" in str(e):
            flash("Upload error: uploaded image is larger than " +
                  "15MB size limit.  Please downsize your image before "
                  "uploading.")
        elif "Exceeds upload limit" in str(e):
            flash("Upload error: you have exceeded your upload limit.  " 
                  "Please delete at least one image from your profile "
                  "before uploading a new image.")
        elif "Exceeds daily upload limit" in str(e):
            flash("Upload error: you have exceeded your daily upload limit.  " 
                  "Please vote on additional images or delete at least one of "
                  "the images you uploaded today from your profile.")
        else:
            logging.info("failed with error code: %s" % str(e))
            flash("Server error.  Try again later." % str(e))

    # Notify the user
    return redirect(url_for('create_image'))


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error has occurred')

    return 'An error has occurred on the server', 500
