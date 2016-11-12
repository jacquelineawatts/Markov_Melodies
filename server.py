from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db
from jinja2 import StrictUndefined
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


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
            melody_filepath = Melody.save_melody_to_wav_file(generated_melody)
            break

    return render_template('results.html', melody_file=melody_filepath)


@app.route('/profile/<user_id>')
def show_profile(user_id):
    """Displays a users profile. """

    user = User.query.get(user_id)
    melodies = User.melodies

    return render_template('profile.html', user=user, melodies=melodies)


@app.route('/signup', methods=['GET'])
def get_signup_form():

    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def process_signup():

    email = request.form.get('email')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')

    emails = db.session.query(User.email).all()

    if email in emails:
        return redirect('/login')

    else:
        user = User(email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    )

        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.user_id

        return redirect('/profile/{}'.format(user.user_id))


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
            return redirect('/profile/{}'.format(user.user_id))
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


if __name__ == "__main__":

    from user import User, Connection, Like
    from melody import Melody, MelodyNote
    from note import Note, Duration
    from markov import Markov, Outcome
    from genre import Genre, MelodyGenre
    from logistic_regression import ItemSelector, predict


    app.debug = True
    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(host='0.0.0.0')
