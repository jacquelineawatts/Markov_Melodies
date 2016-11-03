"""This script generates new melodies using the Markov chains previously built 
from sample MIDI files. """

from random import choice
from markov import chains
import music21


def generate_melody(length, starter_notes):

    new_melody = []

    # Grabs a random starter key and adds it to text string
    current_key = starter_notes
    for note in current_key:
        new_melody.append(note)

    # Runs loop to: 1)Grab random value, append to text string, and reassign new key
    # Limits text string to 1000 char
    while len(new_melody) < length:
        if current_key in chains:
            value = choice(chains[current_key])
            new_melody.append(value)
            current_key = (current_key[1], value)
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
    notes_stream.show('text')
    return notes_text



# ------------------------------EXECUTABLE CODE -------------------------------

# generated_melody = generate_melody(48, ('D4', 'A3'))
# show_stream(generated_melody)
