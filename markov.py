
from model import Markov, Outcome, Note, Genre, connect_to_db, db
from sqlalchemy.orm.exc import NoResultFound
import music21


def get_score_from_corpus(filepaths):
    """Returns list of score objects from music21 builtin corpus of MIDI files."""

    # filepaths = music21.corpus.getComposer(music21_library)
    # scores = []
    # for filepath in filepaths:
    #     score = music21.corpus.parse(filepath)
    #     scores.append(score)

    # return scores

    num_of_scores = len(filepaths)
    n = 0

    while n < num_of_scores:
        yield music21.corpus.parse(filepaths[n])
        n += 1


def add_new_genre(genre):
    """Adds a new genre row to the db."""

    try:
        Genre.query.filter_by(genre=genre).one()
    except NoResultFound:
        genre = Genre(genre=genre)
        db.session.add(genre)
        db.session.commit()
        print "Successfully added new genre."


def add_note_to_db(note):
    """Adds note to the db.

    Might need to remove duration for the time being, as duration is a music21
    object. Explore what attribute from this object would make the most sense to
    store in the db."""

    note = Note(pitch=note.name,
                octave=note.octave,
                )
    db.session.add(note)
    db.session.commit()
    print "Successfully added new note."


def convert_score_to_notes(score):
    """Converts score into list of notes."""

    notes = []
    for note in music21.alpha.theoryAnalysis.theoryAnalyzer.getNotes(score, 0):
        if note is not None:
            try:
                Note.query.filter_by(pitch=note.name, octave=note.octave).one()
            except NoResultFound:
                add_note_to_db(note)

            notes.append(note.nameWithOctave)

    return notes


def add_key_to_markov(first_note_id, second_note_id, genre_id):
    """Adds new markov chain key to the db. """

    markov = Markov(first_note_id=first_note_id,
                    second_note_id=second_note_id,
                    genre_id=genre_id,
                    )
    db.session.add(markov)
    db.session.commit()
    print "Successfully added new Markov key."

    return markov.markov_id


def add_outcome_to_markov(markov_id, outcome_note_id):
    """Adds new outcome instance to db."""

    outcome = Outcome(markov_id=markov_id,
                      note_id=outcome_note_id,
                      weight=1,
                      )
    db.session.add(outcome)
    db.session.commit()
    print "Successfully added new outcome."


def make_chains(melody, genre):
    """Takes input as a list of notes returns _dictionary_ of markov chains.

     A chain will be a key that consists of a tuple of (note1, note2)
    and the value would be a list of the note(s) that follow those two notes
     in the input melody.

    """

    key_note1, key_note2, outcome_note = 0, 1, 2
    try:
        genre_id = Genre.query.filter_by(genre=genre).one().genre_id
    except NoResultFound:
        pass

    while key_note2 < (len(melody) - 1):

        # Determines note_id for all notes in key + outcome
        first_note_id = Note.query.filter_by(pitch=melody[key_note1][0:-1], octave=melody[key_note1][-1]).one().note_id
        print first_note_id
        second_note_id = Note.query.filter_by(pitch=melody[key_note2][0:-1], octave=melody[key_note2][-1]).one().note_id
        print second_note_id
        outcome_note_id = Note.query.filter_by(pitch=melody[outcome_note][0:-1], octave=melody[outcome_note][-1]).one().note_id
        print outcome_note_id

        # Tests for presence of markov key and adds to db if not present.
        try:
            markov_id = Markov.query.filter_by(first_note_id=first_note_id,
                                               second_note_id=second_note_id,
                                               genre_id=genre_id
                                               ).one().markov_id

        except NoResultFound:
            markov_id = add_key_to_markov(first_note_id, second_note_id, genre_id)

        # Tests for presence of markov outcome and if there, increases weight by 1.
        try:
            outcome = Outcome.query.filter_by(markov_id=markov_id,
                                              note_id=outcome_note_id,
                                              ).one()
            outcome.weight += 1
            db.session.commit()

        # Adds to db if outcome not already present
        except NoResultFound:
            add_outcome_to_markov(markov_id, outcome_note_id)

        # Shifts key, value pair by 1 note in notes list.
        key_note1 += 1
        key_note2 += 1
        outcome_note += 1


def load_markov_chains(genre, corpus_name):
    """Loads markov chains into db."""

    add_new_genre(genre)

    # Could I make this into a generator to reduce the need to save all output
    # scores into a list?
    print "Start importing scores..."
    filepaths = music21.corpus.getComposer(corpus_name)
    print filepaths
    # scores = get_scores_from_corpus(corpus_name)
    # print "End importing scores."
    # print scores
    for score in (get_score_from_corpus(filepaths)):
        print '*' * 20
        print "Beginning score:", score
        print '*' * 20

        notes = convert_score_to_notes(score)
        make_chains(notes, genre)


# ------------------------------EXECUTABLE CODE -------------------------------


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    db.create_all()
    print "Connected to DB."

    # load_markov_chains('Celtic', 'ryansMammoth')
