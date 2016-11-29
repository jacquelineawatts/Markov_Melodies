from model import connect_to_db, db
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import pysynth_b as ps
import music21
from user import User
from genre import Genre, MelodyGenre
from note import Note, Duration
from markov import Markov
from analyzer import Analyzer, all_analyzers
import cPickle
import timeit
from logic.logistic_regression import ItemSelector, predict
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin


class Melody(db.Model):
    """Class for generated Melodies"""

    __tablename__ = "melodies"

    melody_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(30))
    is_major = db.Column(db.Boolean)
    key = db.Column(db.String(10))
    time_signature = db.Column(db.Float)
    path_to_file = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    user = db.relationship('User', backref='melodies')

    genres = db.relationship("Genre",
                             secondary="melodies_genres",
                             backref='melodies')

    def __repr__(self):
        return "<Melody ID: {}, Title: {}, Key: {}>".format(self.melody_id,
                                                            self.title,
                                                            self.key,
                                                            )

    @classmethod
    def add_melody_to_db(cls, user_id, title, current_melody):
        """If user signed in, adds most recently generated melody to the db."""

        title_for_filepath = '_'.join(title.split(' '))
        filepath = 'static/melodies/{}_{}.wav'.format(title_for_filepath, user_id)
        ps.make_wav(current_melody['notes'], fn=filepath)
        is_major = bool(current_melody['is_major'])

        try:
            melody = Melody.query.filter_by(user_id=user_id, title=title).one()
            # Need to put in handling for if user tries to save another melody with the same title

        except NoResultFound:
            melody = Melody(title=title,
                            is_major=is_major,
                            path_to_file=filepath,
                            user_id=user_id,
                            )

            db.session.add(melody)
            db.session.commit()
            print "Added new melody object to db."

            MelodyNote.iterate_over_melody(melody.melody_id, current_melody['notes'])
            MelodyGenre.add_melody_genre_to_db(melody.melody_id, current_melody['genres'])

        return melody

    @classmethod
    def generate_new_melody(cls, length, starter_notes, genres):
        """Generates a new melody based on user preferences from homepage.

        Given length as int, starter notes as tuple of abc notation strings
        (i.e 'f#4', 'g4'), and genres as list of strings, outputs markov generated
        melody as a list of note objects."""

        new_melody = []
        # default_duration_id = db.session.query(Duration.duration_id).filter_by(duration=1.0).one()[0]

        # Grabs a random starter key and adds it to text string
        for starter_note in starter_notes:
            print 'STARTER NOTE:', starter_note, type(starter_note)
            note = Note.get_note(starter_note)

            new_melody.append(note)

        # Loop to grab random outcome according to weighted probability, append to
        # new melody, and shift key by one.
        while len(new_melody) < length:

            current_key = (new_melody[-2], new_melody[-1])
            print 'CURRENT KEY', current_key

            markov = Markov.get_markov_by_tuple(current_key, genres)
            print "MY MARKOV: ", markov
            if markov:
                print "Selecting an outcome..."
                outcome = markov.select_outcome()
                new_melody.append(outcome)
            else:
                break

        return new_melody

    @classmethod
    def add_ending(cls, generated_melody):
        """If ending is abrupt, adds longer duration ending note to end of melody."""

        end_note = generated_melody[-1]
        print "END NOTE DURATION: ", end_note.duration.duration
        if end_note.duration.duration < 1.0:
            duration_ids = db.session.query(Duration.duration_id).filter(Duration.duration >= 1.0).all()
            try:
                new_end = Note.query.filter((Note.pitch == end_note.pitch) &
                                            (Note.octave == end_note.octave) &
                                            (Note.duration_id.in_(duration_ids))).first()

            except NoResultFound:
                note = end_note.pitch + str(end_note.octave)
                note_music21_obj = music21.note.Note(note)
                new_end = Note.add_note_to_db(note_music21_obj, 4.0)

            generated_melody.append(new_end)
        else:
            pass

        return generated_melody

    @classmethod
    def convert_for_print(cls, notes_abc_notation):
        """Converts notes from abc notation to Array notation for VexFlow. """

        notes_array = []

        print notes_abc_notation
        for note_tuple in notes_abc_notation:
            note = note_tuple[0].encode('latin-1')
            pitch, octave = note[:-1], note[-1]
            pitch_octave = pitch + '/' + octave
            if int(octave) >= 4:
                clef = 'treble'
            else:
                clef = 'bass'

            duration = int(note_tuple[1])
            # Poor edge case handling in the VexFlow library, this is a fix
            # until I find a better library.
            if duration not in [1, 2, 4, 8, 16]:
                if duration > 16:
                    duration = "16"
                elif duration == 5:
                    duration = '4'
                elif duration == 12 or duration == 10:
                    duration = '8'
                else:
                    duration = '4'
            else:
                duration = str(duration)

            note_for_print = [clef, pitch_octave, duration]
            print note_for_print
            notes_array.append(note_for_print)

        return notes_array

    @classmethod
    def save_melody_to_wav_file(cls, melody, filepath):
        """Takes list of note objects and outputs wav file to the server."""

        #Generates a tuple of tuples in abc notation to pass to pysynth function
        notes_abc = ()
        for note in melody:
            print 'NOTE: ', note, type(note)
            if note != 'None':
                print 'NOTE.pitch: ', note.pitch
                if note.pitch[-1] == '-':
                    note_for_ps = note.pitch[:-1].lower() + 'b'
                else:
                    note_for_ps = note.pitch.lower()
                notes_abc += ((note_for_ps + str(note.octave), Duration.convert_duration_db_to_abc(float(note.duration.duration))),)

            else:
                pass

        print 'NOTES_ABC:', notes_abc

        # Saves newly generated tuple of tuples to wav file in static folder
        ps.make_wav(notes_abc, fn=filepath)
        return notes_abc

    @classmethod
    def make_melody(cls, length, input_notes, genres, mode):
        """Controller for melody generating activities.

        Initiates generation of a new melody, check if suitable length, adds ending,
        compares outcome to mode requested by user, regenerates if needed. When fits
        the criteria, saves to .wav file and composes analyzer comparison dictionary."""

        start_time = timeit.default_timer()
        while True:
            generated_melody = Melody.generate_new_melody(length - 1, input_notes, genres)
            if len(generated_melody) <= 2:
                return None, None, None

            else:
                melody = Melody.add_ending(generated_melody)

                print "Beginning analysis..."
                analyzer_comparison, all_probabilities = Analyzer.build_comparison(all_analyzers, melody, mode)
                high_probs = [prob for prob in all_probabilities if prob > 0.7]
                print high_probs

                if (max(all_probabilities)) > 0.90 or len(high_probs) > (len(all_probabilities) / 3):
                    print "YAY IT'S A MATCH!"

                    temp_filepath = 'static/temp.wav'
                    notes_abc_notation = Melody.save_melody_to_wav_file(melody, temp_filepath)
                    break

            # is_major = Analyzer.predict_mode(melody)
            # print 'PREDICTION OF NEW MELODY: ', is_major, type(is_major)
            # print 'THE USERS PREFERENCE WAS: ', mode, type(mode)
            # if bool(is_major) == bool(mode):
        elapsed = timeit.default_timer() - start_time
        print "TIME REQUIRED TO MAKE MELODY: ", elapsed
        return temp_filepath, notes_abc_notation, analyzer_comparison


class MelodyNote(db.Model):
    """Middle table associating a melody with its corresponding notes. Additional
    relevant fields include sequence (order of notes within a melody)."""

    __tablename__ = "melody_notes"

    melodynote_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    melody_id = db.Column(db.Integer, db.ForeignKey('melodies.melody_id'))
    note_id = db.Column(db.Integer, db.ForeignKey('notes.note_id'))
    sequence = db.Column(db.Integer)

    melody = db.relationship('Melody', backref='melody_notes')
    note = db.relationship('Note', backref='melody_notes', order_by='MelodyNote.sequence')

    def __repr__(self):
        return "<MelodyNote ID: {}, Melody: {}, Note: {}, Sequence: {} >".format(self.melodynote_id,
                                                                                 self.melody,
                                                                                 self.note,
                                                                                 self.sequency,
                                                                                 )

    @classmethod
    def add_melody_note_to_db(cls, note_id, melody_id, sequence):
        """Adds a melodyNote instance to the db. """

        try:
            melody_note = MelodyNote.query.filter_by(note_id=note_id,
                                                     melody_id=melody_id,
                                                     sequence=sequence,
                                                     ).one()
        except NoResultFound:
            melody_note = MelodyNote(melody_id=melody_id,
                                     note_id=note_id,
                                     sequence=sequence,
                                     )
            db.session.add(melody_note)
            db.session.commit()

    @classmethod
    def iterate_over_melody(cls, melody_id, notes_abc_notation):
        """ Iterates thru notes in abc notation melody.

        Given a list of notes that comprise a melody('g4', 8.0)"""

        sequence = 0
        for note in notes_abc_notation:
            pitch = str(note[0][0:-1]).upper()
            print pitch, type(pitch)
            octave = int(note[0][-1])
            print octave, type(octave)
            duration = Duration.query.filter_by(duration=Duration.convert_duration_abc_to_db(note[1])).one()
            print duration.duration_id

            try:
                note = Note.query.filter_by(pitch=pitch, octave=octave, duration_id=duration.duration_id).one()

                MelodyNote.add_melody_note_to_db(note_id=note.note_id,
                                                 melody_id=melody_id,
                                                 sequence=sequence,
                                                 )
            except NoResultFound:
                print "This note cannot be found in the db."

            sequence += 1


# if __name__ == "__main__":

#     from server import app
#     connect_to_db(app)
#     print "Connected to DB."

    # db.create_all()
