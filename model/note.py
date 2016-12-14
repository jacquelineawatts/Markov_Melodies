from model import connect_to_db, db
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from random import choice

class Note(db.Model):
    """Class for notes """

    __tablename__ = "notes"

    note_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pitch = db.Column(db.String(3))
    octave = db.Column(db.Integer)
    duration_id = db.Column(db.Integer, db.ForeignKey('durations.duration_id'))

    duration = db.relationship('Duration', backref='notes')

    def __repr__(self):
        return "<Note ID: {}, Note: {}{}>".format(self.note_id,
                                                  self.pitch,
                                                  self.octave,
                                                  )

    def show_name_with_octave(self):
        """For a given note object, return as pitch with octave notation."""

        return (self.pitch + str(self.octave)).encode('latin-1')

    @classmethod
    def add_note_to_db(cls, note, duration):
        """Given a music21 note object, adds note attributes to the db.

        Might need to remove duration for the time being, as duration is a music21
        object. Explore what attribute from this object would make the most sense to
        store in the db."""

        try:
            note = Note.query.filter_by(pitch=note.name, octave=note.octave, duration_id=duration.duration_id).one()

        except NoResultFound:
            note = Note(pitch=note.name,
                        octave=note.octave,
                        duration_id=duration.duration_id
                        )

            db.session.add(note)
            db.session.commit()
            print "Added new note object to db."

        return note

    @classmethod
    def get_note(cls, nameWithOctave):
        """Given str nameWithOctave returns note object.

        This is for starter notes only and therefore no duration is taken into
        account. Originally set a default duration, but ran into issues
        guaranteeing that there be a Markov key fit."""

        pitch = nameWithOctave[:-1]
        octave = nameWithOctave[-1]

        try:
            all_notes = Note.query.filter_by(pitch=pitch, octave=int(octave)).all()
            note = choice(all_notes)

        except IndexError:
            print "No note found."
            note = None

        return note

    @classmethod
    def get_all_notes(cls):

        # Why does sorted() work here but not .sort()??
        # return sorted([note[0].encode('latin-1') for note in db.session.query(Note.pitch.distinct()).all()])
        notes = set()
        for note_tuple in db.session.query(Note.pitch, Note.octave).all():
            note = note_tuple[0].encode('latin-1') + str(note_tuple[1])
            notes.add(note)

        return list(sorted(notes))

    @staticmethod
    def convert_from_input(input_note):
        """Convert from keyboard input format to db format.

        Takes input from html5 library as format: 2As (second octave, A sharp)
        And outputs appropriate format for db and music21: A#2. """

        octave = input_note[0]
        pitch = input_note[1:]

        if pitch[-1] == "s":
            return pitch[:-1] + "#" + octave
        else:
            return pitch + octave


# if __name__ == "__main__":

#     from server import app
#     connect_to_db(app)
#     print "Connected to DB."

    # db.create_all()
