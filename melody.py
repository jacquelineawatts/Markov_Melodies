from model import connect_to_db, db
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import pysynth_b as ps
import music21
from user import User
from genre import Genre
from note import Note, Duration
from markov import Markov
import cPickle
from logistic_regression import ItemSelector, predict
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
    path_to_file = db.String(256)
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
    def generate_new_melody(cls, length, starter_notes, genres):

        new_melody = []
        # default_duration_id = db.session.query(Duration.duration_id).filter_by(duration=1.0).one()[0]

        # Grabs a random starter key and adds it to text string
        for starter_note in starter_notes:
            print 'STARTER NOTE:', starter_note, type(starter_note)
            note = Note.get_note(starter_note)

            new_melody.append(note)

        current_key = (new_melody[0], new_melody[1])
        print 'CURRENT KEY', current_key

        # Loop to grab random outcome according to weighted probability, append to
        # new melody, and shift key by one.
        while len(new_melody) < length:
            markov = Markov.get_markov_by_tuple(current_key, genres)
            if markov:
                outcome = markov.select_outcome()
                new_melody.append(outcome)
                current_key = (current_key[1], outcome)
            # Right now, just breaks out of loop if it reaches a key that doesn't have
            # any corresponding values. When real data is in here, check to see if this
            # will still be a problem.
            else:
                break

        return new_melody

    @classmethod
    def build_feature_dict_from_melody(cls, melody):

        features = {}
        notes_corpus, steps_corpus = [], []

        all_notes = ""
        all_steps = ""

        notes = []
        for note in melody:
            notes.append(note.pitch + str(note.octave))
            all_notes += note.pitch + " "

        notes_corpus.append(all_notes)

        for i in range(1, len(notes)):
            note_start = music21.note.Note(notes[i-1])
            note_end = music21.note.Note(notes[i])
            interval = music21.interval.Interval(noteStart=note_start, noteEnd=note_end)
            step = int((interval.cents)/100)
            all_steps += str(step) + ' '

        steps_corpus.append(all_steps)

        features['notes_freq'], features['steps_freq'] = notes_corpus, steps_corpus
        return features

    @classmethod
    def predict_mode(cls, melody):

        pipeline_file = open('static/pipeline.txt')
        pipeline = cPickle.load(pipeline_file)
        pipeline_file.close()

        features = Melody.build_feature_dict_from_melody(melody)
        is_major = predict(pipeline, features)
        return is_major

    @classmethod
    def save_melody_to_wav_file(cls, melody):
        """Takes list of note objects and outputs a wav file to the server."""

        #Generates a tuple of tuples in abc notation to pass to pysynth function
        notes_text = ()
        for note in melody:
            print 'NOTE: ', note, type(note)
            if note != 'None':
                print 'NOTE.pitch: ', note.pitch
                if note.pitch[-1] == '-':
                    note_for_ps = note.pitch[:-1].lower() + 'b'
                else:
                    note_for_ps = note.pitch.lower()
                notes_text += ((note_for_ps + str(note.octave), (float(note.duration.duration) ** -1) * 4),)

            # Still need to implement handling of rests
            else:
                pass

        print 'NOTES_TEXT:', notes_text
        # Saves newly generated tuple of tuples to wav file in static folder
        filepath = 'static/temp.wav'
        ps.make_wav(notes_text, fn=filepath)
        return filepath


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

if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."

    db.create_all()
