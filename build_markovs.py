from server import app
from model.model import connect_to_db, db
from sqlalchemy.orm.exc import NoResultFound
from psycopg2 import ProgrammingError
import music21
from model.note import Note, Duration
from model.genre import Genre
from model.markov import Markov, Outcome


def score_generator(filepaths):
    """Returns list of score objects from music21 builtin corpus of MIDI files."""

    num_scores = len(filepaths)
    n = 0

    while n < num_scores:
        yield music21.corpus.parse(filepaths[n])
        n += 1


def part_generator(score):
    """Return list of part objects that are part of a music21 score."""

    parts = [part for part in score.parts]
    num_parts = len(parts)
    n = 0

    while n < num_parts:
        yield n
        n += 1


def convert_part_to_notes(score, n):
    """Converts score into list of notes."""

    notes = []

    for note in music21.alpha.theoryAnalysis.theoryAnalyzer.getNotes(score, n):
        if note is not None:
            try:
                duration = Duration.query.filter_by(duration=float(note.duration.quarterLength)).one()

            except NoResultFound:
                duration = Duration.add_duration_to_db(float(note.duration.quarterLength))

            try:
                Note.query.filter_by(pitch=note.name,
                                     octave=note.octave,
                                     duration_id=duration.duration_id).one()
            except NoResultFound:
                Note.add_note_to_db(note, duration)

            notes.append((note.nameWithOctave, duration.duration_id))

    return notes


def make_chains(notes, genre):
    """Takes input as a list of note, duration tuples, adds markovs + outcomes to db.

     A chain will be a key that consists of a tuple of (note1, note2)
    and the value would be a list of the note(s) that follow those two notes
     in the input notes.

    """

    key_note1, key_note2, outcome_note = 0, 1, 2
    try:
        genre_id = Genre.query.filter_by(genre=genre).one().genre_id
    except NoResultFound:
        genre_id = None

    while key_note2 < (len(notes) - 1):

        # Determines note_id for all notes in key + outcome
        first_note_id = Note.query.filter_by(pitch=notes[key_note1][0][0:-1],
                                             octave=notes[key_note1][0][-1],
                                             duration_id=notes[key_note1][1]
                                             ).one().note_id
        second_note_id = Note.query.filter_by(pitch=notes[key_note2][0][0:-1],
                                              octave=notes[key_note2][0][-1],
                                              duration_id=notes[key_note2][1]
                                              ).one().note_id
        outcome_note_id = Note.query.filter_by(pitch=notes[outcome_note][0][0:-1],
                                               octave=notes[outcome_note][0][-1],
                                               duration_id=notes[outcome_note][1]
                                               ).one().note_id

        # Tests for presence of markov key and adds to db if not present.
        try:
            markov = Markov.query.filter_by(first_note_id=first_note_id,
                                            second_note_id=second_note_id,
                                            genre_id=genre_id
                                            ).one()

        except NoResultFound:
            markov = Markov.add_markov_to_db(first_note_id, second_note_id, genre_id)

        # Tests for presence of markov outcome and if there, increases weight by 1.
        try:
            outcome = Outcome.query.filter_by(markov_id=markov.markov_id,
                                              note_id=outcome_note_id,
                                              ).one()
            outcome.weight += 1
            db.session.commit()

        # Adds to db if outcome not already present
        except NoResultFound:
            Outcome.add_outcome_to_db(markov.markov_id, outcome_note_id)

        # Shifts key, value pair by 1 note in notes list.
        key_note1 += 1
        key_note2 += 1
        outcome_note += 1


def load_markov_chains(genre, corpus_name):
    """Loads markov chains into db."""

    Genre.add_genre_to_db(genre)

    print "Start importing scores..."
    filepaths = music21.corpus.getComposer(corpus_name)

    for score in (score_generator(filepaths)):
        print "Beginning new score: ", score

        for n in (part_generator(score)):
            notes = convert_part_to_notes(score, n)
            make_chains(notes, genre)


# ------------------------------EXECUTABLE CODE -------------------------------


if __name__ == "__main__":

    connect_to_db(app)
    db.create_all()
    print "Connected to DB."

    # load_markov_chains('Classical', 'bach')
