from model import connect_to_db, db
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from note import Note
from duration import Duration


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
