"""This script generates new melodies using the Markov chains previously built
from sample MIDI files. """

from model import Markov, Note, Outcome, get_markov_by_tuple
import music21
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


def generate_melody(length, starter_notes):

    new_melody = []

    # Grabs a random starter key and adds it to text string
    current_key = starter_notes
    for note in current_key:
        new_melody.append(note)

    # Loop to grab random outcome according to weighted probability, append to
    # new melody, and shift key by one.
    while len(new_melody) < length:
        markov = get_markov_by_tuple(current_key)
        if markov:
            outcome = markov.select_outcome().note.show_name_with_octave()
            new_melody.append(outcome)
            current_key = (current_key[1], outcome)
        # Right now, just breaks out of loop if it reaches a key that doesn't have
        # any corresponding values. When real data is in here, check to see if this
        # will still be a problem.
        else:
            break

    return new_melody


def show_stream(generated_melody):

    # Creates an empty stream (stream is a place to story object; parent class of Score)
    notes_stream = music21.stream.Stream()
    notes_text = []
    # Iterate thru notes generated from Markov chain and append them to stream
    for note in generated_melody:
        if note != 'None':
            note = music21.note.Note(note)
            notes_stream.append(note)
            notes_text.append(note.nameWithOctave)

        # Still need to implement handling of rests
        else:
            pass

    # show() displays the stream in Finale Notepad
    # save to disk, actually generate midi file
    # Save to session while user is playing around with results, not commit to db
    # until user decides to save
    # notes_stream.show('midi')
    return notes_text


# ------------------------------EXECUTABLE CODE -------------------------------

# generated_melody = generate_melody(48, ('D4', 'A3'))
# show_stream(generated_melody)

# ------------------------------EXECUTABLE CODE -------------------------------

if __name__ == "__main__":

    connect_to_db(app)
    db.create_all()
    print "Connected to DB."
