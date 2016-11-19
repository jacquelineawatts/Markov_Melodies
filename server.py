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
from logistic_regression import ItemSelector, predict
# from image_handler import UploadAPI

# ----- FOR TESTING IMG UPLOADER ------
from flask.views import MethodView
import json
import os
import os.path
import shutil
# ------- END TESTING ------

# ------ FOR TESTING REDIRECT ANIMATION STUFF ------
import time
# ---------- END TESTING


app = Flask(__name__)
app.secret_key = "%ri*.\xab\x12\x81\x9b\x14\x1b\xd3\x86\xcaK\x8b\x87\t\x8c\xaf\x9d\x14\x87\x8a"
app.jinja_env.undefined = StrictUndefined
BASE_DIRECTORY = os.path.dirname(__file__)
STATIC_DIRECTORY = os.path.join(BASE_DIRECTORY, 'static')
UPLOAD_DIRECTORY = os.path.join(STATIC_DIRECTORY, 'images')


@app.route('/')
def index():
    """Shows homepage. """

    notes = Note.get_all_notes()
    # notes = ['A-4', 'A4', 'A#4', 'B-4', 'B4', 'C4', 'C#4', 'D-4', 'D4', 'D#4',
    #          'E-4', 'E4', 'F4', 'F#4', 'G-4', 'G4', 'G#4']

    return render_template('index.html', notes=notes)


@app.route('/add_melody', methods=['POST'])
def adds_melody():
    """Adds a new melody to db."""

    user_id = session['user_id']
    title = request.form.get('title').encode('latin-1')
    current_melody = session['current_melody']

    melody = Melody.add_melody_to_db(user_id, title, current_melody)
    flash("You've successfully added a melody to your account.")

    return redirect('/user/{}'.format(user_id))


# @app.route('/testing')
# def test():
#     time.sleep(5)
#     return str(request.args)


@app.route('/results', methods=['POST'])
def show_results():
    """Shows results of a generated melody."""

    note1 = request.form.get('note1').encode('latin-1')
    note2 = request.form.get('note2').encode('latin-1')
    input_notes = (note1, note2)
    length = int(request.form.get('length'))
    mode = bool(request.form.get('mode'))
    genres = [genre.encode('latin-1') for genre in request.form.getlist('genres')]
    temp_filepath, notes_abc_notation, analyzer_comparison = Melody.make_melody(length, input_notes, genres, mode)

    if temp_filepath is None:
        flash("I'm sorry, there's no melody for that combination of seed notes. Please start over.")
        return redirect('/')

    else:
        session['analyzer_data'] = analyzer_comparison
        session['current_melody'] = {'is_major': mode,
                                     'notes': notes_abc_notation,
                                     'wav_filepath': temp_filepath,
                                     'genres': genres}

        return render_template('results.html', melody_file=temp_filepath, analyzer_comparison=analyzer_comparison)


@app.route('/analyzer_data.json')
def construct_chart_data():

    analyzer_comparison = session['analyzer_data']

    chart_data = {"labels": ["Linear Regression", "Multinomial NB", "Support Vector Classification"],
                  "datasets": [{"data": [analyzer_comparison['Logistic Regression']['Notes'],
                                         analyzer_comparison['Naive Bayes']['Notes'],
                                         analyzer_comparison['Support Vector Classification']['Notes'],
                                         ],
                                "backgroundColor": ['#ff9900', '#ff9900', '#ff9900'],
                                "hoverBackgroundColor": ['#ffd699', '#ffd699', '#ffd699'],
                                },
                               {"data": [analyzer_comparison['Logistic Regression']['Steps'],
                                         analyzer_comparison['Naive Bayes']['Steps'],
                                         analyzer_comparison['Support Vector Classification']['Steps'],
                                         ],
                                "backgroundColor": ['#0066ff', '#0066ff', '#0066ff'],
                                "hoverBackgroundColor": ['#99c2ff', '#99c2ff', '#99c2ff'],
                                },
                               {"data": [analyzer_comparison['Logistic Regression']['Both'],
                                         analyzer_comparison['Naive Bayes']['Both'],
                                         analyzer_comparison['Support Vector Classification']['Both']],
                                "backgroundColor": ['#339966', '#339966', '#339966'],
                                "hoverBackgroundColor": ['#9fdfbf', '#9fdfbf', '#9fdfbf'],
                                }
                               ]
                  }

    return jsonify(chart_data)


@app.route('/users')
def show_all_users():
    """Display all users."""

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

    following = {}
    for user in user.following:
        last_melody_id = user.find_last_melody()
        if last_melody_id:
            last_melody = Melody.query.get(last_melody_id)
        else:
            last_melody = None
        following[user.user_id] = [user, last_melody]

    return render_template('user.html',
                           user=user,
                           melodies=melodies,
                           is_current_user=is_current_user,
                           likes=likes,
                           following=following,
                           )


@app.route('/follow_user/<user_id>')
def add_connection(user_id):
    """Create new follower-following connection."""

    follower_user_id = session['user_id']
    following_user_id = user_id

    Connection.add_connection_to_db(follower_user_id, following_user_id)

    return redirect('/user/{}'.format(following_user_id))


@app.route('/unfollow/<user_id>')
def delete_connection(user_id):

    follower_user_id = session['user_id']
    following_user_id = user_id

    Connection.delete_connection(follower_user_id, following_user_id)

    return redirect('/users')


@app.route('/add_like/<melody_id>')
def add_like_to_melody(melody_id):

    melody = Melody.query.get(melody_id)
    melody_user_id = melody.user.user_id
    current_user_id = session['user_id']
    Like.add_like(current_user_id, melody_id)

    return redirect('/user/{}'.format(melody_user_id))


@app.route('/unlike/<melody_id>')
def delete_like_from_melody(melody_id):

    melody = Melody.query.get(melody_id)
    melody_user_id = melody.user.user_id
    current_user_id = session['user_id']
    Like.delete_like(current_user_id, melody_id)

    return redirect('/user/{}'.format(melody_user_id))


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
        flash("You already have an account. Please sign in.")
        session['img_upload_filepath'] = None
        return redirect('/login')

    else:
        user = User.add_user_to_db(email, password, first_name, last_name, profile_img)
        flash("Thank you for signing up for an account.")
        session['user_id'] = user.user_id
        session['img_upload_filepath'] = None

        return redirect('/user/{}'.format(user.user_id))

# ------------------------------- LOGGING IN/OUT -------------------------------


@app.route('/login', methods=['GET'])
def shows_login():

    return render_template('login.html')


@app.route('/login', methods=['POST'])
def process_login():

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
    """ """

    session['user_id'] = None
    session['current_melody'] = None
    session['analyzer_data'] = None
    flash("You've successfully logged out!")
    return redirect('/')


# ------------------------------ STARTING SERVER -------------------------------
if __name__ == "__main__":

    app.debug = True
    connect_to_db(app)
    # DebugToolbarExtension(app)
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(host='0.0.0.0')
