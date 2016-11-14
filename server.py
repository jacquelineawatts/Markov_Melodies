from flask import Flask, render_template, redirect, request, flash, session, current_app, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db
from jinja2 import StrictUndefined
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from user import User, Connection, Like
from melody import Melody, MelodyNote
from note import Note, Duration
from markov import Markov, Outcome
from genre import Genre, MelodyGenre
from logistic_regression import ItemSelector, predict
# from image_handler import UploadAPI

# ----- FOR TESTING IMG UPLOADER ------
from flask.views import MethodView
import json
import os
import os.path
import shutil
# ------- END TESTING ------


app = Flask(__name__)
app.secret_key = "%ri*.\xab\x12\x81\x9b\x14\x1b\xd3\x86\xcaK\x8b\x87\t\x8c\xaf\x9d\x14\x87\x8a"
app.jinja_env.undefined = StrictUndefined
BASE_DIRECTORY = os.path.dirname(__file__)
STATIC_DIRECTORY = os.path.join(BASE_DIRECTORY, 'static')
UPLOAD_DIRECTORY = os.path.join(STATIC_DIRECTORY, 'images')


@app.route('/')
def index():
    """Shows homepage. """

    notes = ['A-4', 'A4', 'A#4', 'B-4', 'B4', 'C4', 'C#4', 'D-4', 'D4', 'D#4',
             'E-4', 'E4', 'F4', 'F#4', 'G-4', 'G4', 'G#4']

    return render_template('index.html', notes=notes)


@app.route('/add_melody', methods=['POST'])
def adds_melody():
    """Adds a new melody to db."""

    user_id = session['user_id']
    title = request.form.get('title').encode('latin-1')
    current_melody = session['current_melody']

    melody = Melody.add_melody_to_db(user_id, title, current_melody)

    return redirect('/user/{}'.format(user_id))


@app.route('/results', methods=['POST'])
def show_results():
    """Shows results of a generated melody."""

    note1 = request.form.get('note1').encode('latin-1')
    note2 = request.form.get('note2').encode('latin-1')
    input_notes = (note1, note2)
    length = int(request.form.get('length'))
    mode = request.form.get('mode')
    genres = request.form.get('genres')

    while True:
        generated_melody = Melody.generate_new_melody(length, input_notes, genres)
        is_major = Melody.predict_mode(generated_melody)
        print 'PREDICTION OF NEW MELODY: ', is_major, type(is_major)
        print 'THE USERS PREFERENCE WAS: ', mode, type(mode)
        if bool(is_major) == bool(mode):
            print "YAY IT'S A MATCH!"
            temp_filepath = 'static/temp.wav'
            notes_abc_notation = Melody.save_melody_to_wav_file(generated_melody, temp_filepath)
            session['current_melody'] = {'is_major': mode, 'notes': notes_abc_notation, 'wav_filepath': temp_filepath}
            break

    return render_template('results.html', melody_file=temp_filepath)


@app.route('/users')
def show_all_users():
    """Display all users."""

    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/user/<user_id>')
def show_user_profile(user_id):
    """Displays a users profile. """

    user = User.query.get(user_id)
    melodies = user.melodies

    return render_template('user.html', user=user, melodies=melodies)


# ------------------------------ IMAGE UPLOADING -------------------------------
# HOW DO I SHIFT THIS STUFF INTO ANOTHER FILE (LIKE IMAGE_HANDLER.PY) WITHOUT
# WORRYING ABOUT CIRCULAR REFERENCES?

# ----- FOR TESTING IMG UPLOADER ------
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

# --------------------------- PROFILE REGISTRATION -----------------------------

@app.route('/signup', methods=['GET'])
def get_signup_form():

    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def process_signup():

    email = request.form.get('email')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    profile_img = session['img_upload_filepath']

    emails = db.session.query(User.email).all()

    if email in emails:
        return redirect('/login')

    else:
        user = User(email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    profile_img=profile_img,
                    )

        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.user_id

        return redirect('/user/{}'.format(user.user_id))

# ------------------------------- LOGGING IN/OUT -------------------------------

@app.route('/login', methods=['GET'])
def shows_login():

    return render_template('login.html')


@app.route('/login', methods=['POST'])
def process_login():

    email = request.form.get('email')
    password = request.form.get('password')

    user_query = db.session.query(User).filter_by(email=email)
    try:
        user = user_query.one()
    except NoResultFound:
        print "No user instance found for this email in db."
        user = None
    except MultipleResultsFound:
        print "Multiple user instances found for this email in db."
        user = user_query.first()

    if user:
        if user.password == password:
            flash("You've successfully logged in!")
            session['user_id'] = user.user_id
            return redirect('/user/{}'.format(user.user_id))
        else:
            flash("I'm sorry that password is incorrect. Please try again.")
            return redirect('/login')

    else:
        flash("""I'm sorry that email is not in our system. Please try again
                or go to our registration page to create a new account.""")
        return redirect('/login')


@app.route('/logout')
def processes_logout():
    """ """

    session['user_id'] = None
    flash("You've successfully logged out!")
    return redirect('/')


# ------------------------------ STARTING SERVER -------------------------------
if __name__ == "__main__":

    app.debug = True
    connect_to_db(app)
    # DebugToolbarExtension(app)

    app.run(host='0.0.0.0')
