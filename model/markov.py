from model import connect_to_db, db
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from note import Note
import numpy as np
from genre import Genre
from note import Note, Duration


class Markov(db.Model):
    """This class contains all attributes and functionality for building and
    referencing the Markov chain keys. See Outcomes class for corresponding values."""

    __tablename__ = "markovs"

    markov_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_note_id = db.Column(db.Integer, db.ForeignKey('notes.note_id'))
    second_note_id = db.Column(db.Integer, db.ForeignKey('notes.note_id'))
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.genre_id'))

    first_note = db.relationship('Note', foreign_keys=[first_note_id])
    second_note = db.relationship('Note', foreign_keys=[second_note_id])
    genre = db.relationship("Genre", backref='markovs')

    def __repr__(self):
        return "<Markov ID: {}, Bi-gram: {}, {}>".format(self.markov_id,
                                                         self.first_note.pitch + str(self.first_note.octave),
                                                         self.second_note.pitch + str(self.second_note.octave),
                                                         )

    def select_outcome(self):
        """For a given Markov key object, selects an outcome based on weights.

        Uses numpy random module in order to pass probabilities in addition to
        potential outcomes. Outputs a random note object."""

        # Switch this to a dictionary instead of two parallel lists?
        potential_outcomes = [(outcome, outcome.weight) for outcome in self.outcomes]
        outcomes = [outcome[0] for outcome in potential_outcomes]
        weights = [outcome[1] for outcome in potential_outcomes]
        total = float(sum(weights))
        probability = [weight/total for weight in weights]

        outcome_note = np.random.choice(outcomes, 1, p=probability)
        print 'OUTCOME NOTE: ', outcome_note

        return outcome_note[0].note

    @classmethod
    def add_markov_to_db(cls, first_note_id, second_note_id, genre_id):
        """Adds new markov chain key to the db."""

        markov = Markov(first_note_id=first_note_id,
                        second_note_id=second_note_id,
                        genre_id=genre_id,
                        )
        db.session.add(markov)
        db.session.commit()
        print "Added new Markov key object to db."

        return markov

    @classmethod
    def find_related_markov(cls, first_note, second_note, genre_ids):
        """Finds a related markov key if get_markov_by_tuple query returns empty."""

        print "FINDING A NEW MARKOV...."
        i = 0
        for note in [first_note, second_note]:
            potential_replacements = Note.query.filter_by(pitch=note.pitch,
                                                          octave=note.octave).all()

            for note in potential_replacements:
                if i == 0:
                    markov = Markov.get_markov(note, second_note, genre_ids)
                else:
                    markov = Markov.get_markov(first_note, note, genre_ids)

                if markov:
                    print "MARKOV FOUND!!"
                    return markov
                else:
                    continue
            i += 1

        if not markov:
            return False

    @classmethod
    def get_markov(cls, first_note, second_note, genre_ids):
        """FIND WERE THIS IS USED, AND REPLACE IT WITH BELOW!"""

        markov = Markov.query.filter((Markov.first_note_id == first_note.note_id) &
                                     (Markov.second_note_id == second_note.note_id) &
                                     (Markov.genre_id.in_(genre_ids))).first()

        return markov

    @classmethod
    def get_markov_by_tuple(cls, notes_tuple, genres):
        """Given note objects as a tuple, and given multiple genre obj, returns markov obj.

        For instance where no Markov obj fits the criteria, finds a related obj
        using find_related_markov."""

        print 'NOTES TUPLE:', notes_tuple
        first_note = notes_tuple[0]
        print 'FIRST NOTE:', first_note
        second_note = notes_tuple[1]
        print 'SECOND NOTE:', second_note
        genre_ids = [Genre.get_genre(genre).genre_id for genre in genres]
        print 'GENRE IDS:', genre_ids

        markov = Markov.query.filter((Markov.first_note_id == first_note.note_id) &
                                     (Markov.second_note_id == second_note.note_id) &
                                     (Markov.genre_id.in_(genre_ids)))
        try:
            markov = markov.one()

        except NoResultFound:
            print "No Markov key for that tuple."
            markov = Markov.find_related_markov(first_note, second_note, genre_ids)

        except MultipleResultsFound:
            print "Mult Markov keys found for that tuple."
            markov = markov.first()

        return markov


class Outcome(db.Model):
    """Class for potential Markov values and their associated weights. See
    Markov class for the corresponding keys."""

    __tablename__ = "outcomes"

    outcome_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    markov_id = db.Column(db.Integer, db.ForeignKey('markovs.markov_id'))
    note_id = db.Column(db.Integer, db.ForeignKey('notes.note_id'))
    weight = db.Column(db.Integer)

    markov = db.relationship('Markov', backref='outcomes')
    note = db.relationship('Note', backref='outcomes')

    def __repr__(self):
        return "<Outcome ID: {}, Markov: {}, Note: {}, Weight: {}>".format(self.outcome_id,
                                                                           self.markov,
                                                                           self.note,
                                                                           self.weight,
                                                                           )

    @classmethod
    def add_outcome_to_db(cls, markov_id, outcome_note_id):
        """Adds new outcome instance to db."""

        outcome = Outcome(markov_id=markov_id,
                          note_id=outcome_note_id,
                          weight=1,
                          )
        db.session.add(outcome)
        db.session.commit()
        print "Added new outcome object to db."


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."

    # db.create_all()
