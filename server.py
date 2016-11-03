from flask import Flask, jsonify, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
# from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

# from model import connect_to_db, db
# from model import User, Melody, Note, MelodyNote, Markov, Outcome, Connection, Like
import melody_generator

app = Flask(__name__)
app.secret_key = "%ri*.\xab\x12\x81\x9b\x14\x1b\xd3\x86\xcaK\x8b\x87\t\x8c\xaf\x9d\x14\x87\x8a"
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Shows homepage. """

    notes = ['A-4', 'A4', 'A#4', 'B-4', 'B4', 'C4', 'C#4', 'D-4', 'D4', 'D#4',
             'E-4', 'E4', 'F4', 'F#4', 'G-4', 'G4', 'G#4']

    return render_template('index.html', notes=notes)


@app.route('/add_melody', methods=['POST'])
def adds_melody():
    """Adds a new melody to db."""

    return redirect('/results')


@app.route('/results', methods=['POST'])
def show_results():
    """Shows results of a generated melody."""

    note1 = request.form.get('note1').encode('latin-1')
    note2 = request.form.get('note2').encode('latin-1')
    input_notes = (note1, note2)

    # Need to put some js form validation on frontend for length input,
    # otherwise comes in as None and throws app into infinite loop...
    length = int(request.form.get('length'))
    mode = request.form.get('mode')

    generated_melody = melody_generator.generate_melody(length, input_notes)
    melody_text = melody_generator.show_stream(generated_melody)

    return render_template('results.html', melody=melody_text)


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
