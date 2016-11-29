from server import app
from model import connect_to_db, db
from flask import current_app, Flask, jsonify, render_template, request
from flask.views import MethodView
import json
import os.path
import shutil


BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIRECTORY = os.path.join(BASE_DIR, 'media')


def make_response(status=200, content=None):
    """ Construct a response to an upload request.

    Success is indicated by a status of 200 and { "success": true }
    contained in the content.
    Also, content-type is text/plain by default since IE9 and below chokes
    on application/json. For CORS environments and IE9 and below, the
    content-type needs to be text/html.
    """

    return current_app.response_class(json.dumps(content,
        indent=None if request.is_xhr else 2), mimetype='text/plain')


def validate(attrs):
    """ No-op function which will validate the client-side data.
    Werkzeug will throw an exception if you try to access an
    attribute that does not have a key for a MultiDict.
    """
    try:
        #required_attributes = ('qquuid', 'qqfilename')
        #[attrs.get(k) for k,v in attrs.items()]
        return True
    except Exception, e:
        return False


def handle_delete(uuid):
    """ Handles a filesystem delete based on UUID."""
    location = os.path.join(app.config['UPLOAD_DIRECTORY'], uuid)
    print(uuid)
    print(location)
    shutil.rmtree(location)


def handle_upload(f, attrs):
    """ Handle a chunked or non-chunked upload.
    """

    # chunked = False
    dest_folder = os.path.join(app.config['UPLOAD_DIRECTORY'], attrs['qquuid'])
    dest = os.path.join(dest_folder, attrs['qqfilename'])
    save_upload(f, dest)


def save_upload(f, path):
    """ Save an upload.
    Uploads are stored in media/uploads
    """
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'wb+') as destination:
        destination.write(f.read())


class UploadAPI(MethodView):
    """ View which will handle all upload requests sent by Fine Uploader.
    Handles POST and DELETE requests.
    """

    def post(self):
        """A POST request. Validate the form and then handle the upload
        based ont the POSTed data. Does not handle extra parameters yet.
        """
        if validate(request.form):
            handle_upload(request.files['qqfile'], request.form)
            return make_response(200, {"success": True})
        else:
            return make_response(400, {"error": "Invalid request"})

    def delete(self, uuid):
        """A DELETE request. If found, deletes a file with the corresponding
        UUID from the server's filesystem.
        """
        try:
            handle_delete(uuid)
            return make_response(200, {"success": True})
        except Exception, e:
            return make_response(400, {"success": False, "error": e.message})



### TEMPORARILY TAKING THIS OUT OF MY SERVER...CHECK FOR CHANGES FROM ABOVE

# ------------------------------ IMAGE UPLOADING -------------------------------
# HOW DO I SHIFT THIS STUFF INTO ANOTHER FILE (LIKE IMAGE_HANDLER.PY) WITHOUT
# WORRYING ABOUT CIRCULAR REFERENCES?


def make_response(status=200, content=None):
    """ Construct a response to an upload request.

    Success is indicated by a status of 200 and { "success": true }
    contained in the content.
    Also, content-type is text/plain by default since IE9 and below chokes
    on application/json. For CORS environments and IE9 and below, the
    content-type needs to be text/html.
    """

    return current_app.response_class(json.dumps(content,
                                      indent=None if request.is_xhr else 2),
                                      mimetype='text/plain')


def validate(attrs):
    """ No-op function which will validate the client-side data.
    Werkzeug will throw an exception if you try to access an
    attribute that does not have a key for a MultiDict.
    """
    print "I GOT HERE."
    try:
        #required_attributes = ('qquuid', 'qqfilename')
        #[attrs.get(k) for k,v in attrs.items()]
        return True
    except Exception, e:
        return False


def handle_delete(uuid):
    """ Handles a filesystem delete based on UUID."""
    location = os.path.join(app.config['UPLOAD_DIRECTORY'], uuid)
    print(uuid)
    print(location)
    shutil.rmtree(location)


def handle_upload(f, attrs):
    """ Handle a chunked or non-chunked upload.
    """

    # chunked = False
    print 'UPLOAD DIRECTORY:', UPLOAD_DIRECTORY
    dest_folder = os.path.join(UPLOAD_DIRECTORY, attrs['qquuid'])
    dest = os.path.join(dest_folder, attrs['qqfilename'])
    save_upload(f, dest)


def save_upload(f, path):
    """ Save an upload.
    Uploads are stored in static/images
    """
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'wb+') as destination:
        destination.write(f.read())


class UploadAPI(MethodView):
    """ View which will handle all upload requests sent by Fine Uploader.
    Handles POST and DELETE requests.
    """

    def post(self):
        """A POST request. Validate the form and then handle the upload
        based ont the POSTed data. Does not handle extra parameters yet.
        """
        if validate(request.form):
            handle_upload(request.files['qqfile'], request.form)
            filepath = 'static/images/{}/{}'.format(request.form['qquuid'], request.form['qqfilename'])
            session['img_upload_filepath'] = filepath
            return make_response(200, {"success": True})
        else:
            return make_response(400, {"error": "Invalid request"})

    def delete(self, uuid):
        """A DELETE request. If found, deletes a file with the corresponding
        UUID from the server's filesystem.
        """
        try:
            handle_delete(uuid)
            return make_response(200, {"success": True})
        except Exception, e:
            return make_response(400, {"success": False, "error": e.message})


upload_view = UploadAPI.as_view('upload_view')
app.add_url_rule('/upload', view_func=upload_view, methods=['POST', ])
app.add_url_rule('/upload/<uuid>', view_func=upload_view, methods=['DELETE', ])

# ------- END TESTING ------
