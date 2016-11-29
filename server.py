from flask import Flask, render_template, redirect, request, flash, session, current_app, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model.model import connect_to_db, db
from jinja2 import StrictUndefined
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from model.user import User, Connection, Like
from model.melody import Melody, MelodyNote
from model.note import Note, Duration
from model.markov import Markov, Outcome
from model.genre import Genre, MelodyGenre
from model.analyzer import Analyzer
from logic.logistic_regression import ItemSelector, predict


app = Flask(__name__)
app.secret_key = "%ri*.\xab\x12\x81\x9b\x14\x1b\xd3\x86\xcaK\x8b\x87\t\x8c\xaf\x9d\x14\x87\x8a"
app.jinja_env.undefined = StrictUndefined
# BASE_DIRECTORY = os.path.dirname(__file__)
# STATIC_DIRECTORY = os.path.join(BASE_DIRECTORY, 'static')
# UPLOAD_DIRECTORY = os.path.join(STATIC_DIRECTORY, 'images')


# ------------------------------ COVER + HOMEPAGE ------------------------------

@app.route('/')
def show_cover_page():

    return render_template('cover.html')


@app.route('/melody')
def make_melody():
    """Shows homepage. """

    notes = Note.get_all_notes()

    return render_template('index.html', notes=notes)


# ------------------------------ RESULTS PAGE ----------------------------------

@app.route('/results', methods=['POST'])
def show_results():
    """Shows results of a generated melody."""

    note1 = Note.convert_from_input(request.form.get('note1').encode('latin-1'))
    print note1
    note2 = Note.convert_from_input(request.form.get('note2').encode('latin-1'))
    print note2
    input_notes = (note1, note2)
    length = int(request.form.get('length'))
    mode = bool(request.form.get('mode'))
    genres = [genre.encode('latin-1') for genre in request.form.getlist('genres')]
    temp_filepath, notes_abc_notation, analyzer_comparison = Melody.make_melody(length, input_notes, genres, mode)

    if temp_filepath is None:
        flash("I'm sorry, there's no melody for that combination of seed notes. Please start over.")
        return redirect('/melody')

    else:
        session['analyzer_data'] = analyzer_comparison
        session['current_melody'] = {'is_major': mode,
                                     'notes': notes_abc_notation,
                                     'wav_filepath': temp_filepath,
                                     'genres': genres}

        notes_array = Melody.convert_for_print(notes_abc_notation)

        return render_template('results.html', melody_file=temp_filepath, analyzer_comparison=analyzer_comparison, notesArray=notes_array)


@app.route('/analyzer_data.json')
def construct_chart_data():
    """Constructs data for ChartJS viz of ML classifier outcomes on results page."""

    analyzer_comparison = session['analyzer_data']
    chart_data = Analyzer.build_chart_data(analyzer_comparison)

    return jsonify(chart_data)


@app.route('/add_melody', methods=['POST'])
def adds_melody():
    """Instantiates new melody associated with current user."""

    user_id = session['user_id']
    title = request.form.get('title').encode('latin-1')
    current_melody = session['current_melody']

    melody = Melody.add_melody_to_db(user_id, title, current_melody)
    flash("You've successfully added a melody to your account.")

    return redirect('/user/{}'.format(user_id))


# ----------------------------- USER PROFILES ----------------------------------

@app.route('/users')
def show_all_users():
    """Displays all users."""

    current_user = User.query.get(session['user_id'])
    all_users = User.query.filter(User.user_id != current_user.user_id).all()
    current_user_following = current_user.following

    return render_template('users.html', users=all_users, following=current_user_following)


@app.route('/user/<user_id>')
def show_user_profile(user_id):
    """Displays a users profile. """

    user = User.query.get(user_id)
    melodies = user.melodies
    current_user = session['user_id']
    is_current_user = (user.user_id == current_user)
    likes = Like.check_for_likes(melodies, current_user)

    user_following = {}
    for following in user.following:
        last_melody_id = following.find_last_melody()
        if last_melody_id:
            last_melody = Melody.query.get(last_melody_id)
        else:
            last_melody = None
        user_following[following.user_id] = [following, last_melody]

    return render_template('user.html',
                           user=user,
                           melodies=melodies,
                           is_current_user=is_current_user,
                           likes=likes,
                           following=user_following,
                           )

# ------------------------ FOLLOWING/UNFOLLOWING A USER ------------------------

@app.route('/follow_user/<user_id>')
def add_connection(user_id):
    """Creates new follower-following connection."""

    follower_user_id = session['user_id']
    following_user_id = user_id

    Connection.add_connection_to_db(follower_user_id, following_user_id)

    return redirect('/users')


@app.route('/unfollow/<user_id>')
def delete_connection(user_id):
    """Deletes a follower-following connection."""

    follower_user_id = session['user_id']
    following_user_id = user_id

    Connection.delete_connection(follower_user_id, following_user_id)

    return redirect('/users')

# ------------------------- ADDING/DELETING LIKES ------------------------------

@app.route('/add_like/<melody_id>')
def add_like_to_melody(melody_id):
    """Creates a new like associated with a user and another users melody. """

    melody = Melody.query.get(melody_id)
    melody_user_id = melody.user.user_id
    current_user_id = session['user_id']
    Like.add_like(current_user_id, melody_id)

    return redirect('/user/{}'.format(melody_user_id))


@app.route('/unlike/<melody_id>')
def delete_like_from_melody(melody_id):
    """Deletes a like. """

    melody = Melody.query.get(melody_id)
    melody_user_id = melody.user.user_id
    current_user_id = session['user_id']
    Like.delete_like(current_user_id, melody_id)

    return redirect('/user/{}'.format(melody_user_id))


# --------------------------- PROFILE REGISTRATION -----------------------------


@app.route('/signup', methods=['GET'])
def get_signup_form():
    """Displays signup page for a new user."""

    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def process_signup():
    """Processes signup page form input to add a new user to the db. """

    email = request.form.get('email')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    profile_img = session['img_upload_filepath']

    emails = db.session.query(User.email).all()

    if email in emails:
        flash("You already have an account. Please sign in.")
        session['img_upload_filepath'] = None
        return redirect('/#login')

    else:
        user = User.add_user_to_db(email, password, first_name, last_name, profile_img)
        flash("Thank you for signing up for an account.")
        session['user_id'] = user.user_id
        session['img_upload_filepath'] = None

        return redirect('/melody')
        # return redirect('/user/{}'.format(user.user_id))

# ------------------------------- LOGGING IN/OUT -------------------------------


@app.route('/login', methods=['GET'])
def shows_login():
    """Displays login page for an existing user."""

    return render_template('login.html')


@app.route('/login', methods=['POST'])
def process_login():
    """Processes login form input to validate a user login."""

    email = request.form.get('email')
    password = request.form.get('password')

    user_query = User.query.filter_by(email=email)
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
    """Processes a user logging out and resets any associated session keys."""

    session['user_id'] = None
    session['current_melody'] = None
    session['analyzer_data'] = None
    flash("You've successfully logged out!")
    return redirect('/')

# ------------------------------- OAUTH HANDLING -------------------------------


@app.route('/post_oauth', methods=['POST'])
def get_oauth_data():

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    profile_img = request.form['profile_img']
    password = 'test'

    print 'USER INFO: ', first_name, last_name, email, profile_img

    user_query = User.query.filter_by(email=email)

    try:
        user = user_query.one()
    except NoResultFound:
        user = User.add_user_to_db(email, password, first_name, last_name)

    except MultipleResultsFound:
        print "Multiple user instances found for this email in db."
        user = user_query.first()

    if user:
        # STILL ISSUES SETTING THE USER ID VAR IN SESSION...
        session['user_id'] = user.user_id
        print "USER ID: ", session['user_id']

    return redirect('/melody')

    emails = db.session.query(User.email).all()
    if email in emails:
        current_user_id = db.session.query(User.user_id).filter_by(email=email).one()
        session['user_id'] = current_user_id
        return redirect('/melody')

    else:
        user = User.add_user_to_db(email, password, first_name, last_name, profile_img)
        flash("Thank you for signing up for an account.")
        session['user_id'] = user.user_id
        session['img_upload_filepath'] = None

        return redirect('/melody')

# ------------------------------ STARTING SERVER -------------------------------
if __name__ == "__main__":

    app.debug = True
    connect_to_db(app)
    # DebugToolbarExtension(app)
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(host='0.0.0.0')
