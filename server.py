from flask import Flask, jsonify, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
# from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

# from model import connect_to_db, db
# from model import User, Melody, Note, MelodyNote, Markov, Outcome, Connection, Like


app = Flask(__name__)
app.secret_key = "%ri*.\xab\x12\x81\x9b\x14\x1b\xd3\x86\xcaK\x8b\x87\t\x8c\xaf\x9d\x14\x87\x8a"
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Shows homepage. """

    notes = ['A-flat', 'A', 'A#', 'B-flat', 'B', 'C', 'C#', 'D-flat', 'D', 'D#', 'E-flat', 'E', 'F', 'F#', 'G-flat', 'G', 'G#']

    return render_template('index.html', notes=notes)


@app.route('/new_melody', methods=['POST'])
def generate_new_melody():
    """Handles form input for generating a new melody."""

    note1 = request.form.get('note1')
    note2 = request.form.get('note2')
    mode = request.form.get('mode')


    return redirect('/results')


@app.route('/results')
def show_results():
    """Shows results of a generated melody."""

    return render_template('results.html')


@app.route('/profile/<user_id>')
def show_profile(user_id):
    """Displays a users profile. """

    user = User.query.get(user_id)

    return render_template('profile.html', user=user)


@app.route('/signup', methods=['GET'])
def get_signup_form():

    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def process_signup():

    pass


@app.route('/login', methods=['GET'])
def shows_login():

    pass


@app.route('/login', methods=['POST'])
def process_login():

    pass


@app.route('/logout')
def processes_logout():
    """ """

    pass


if __name__ == "__main__":

    app.debug = True
    # connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(host='0.0.0.0')
