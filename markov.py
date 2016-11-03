"""This script builds Markov chains from txt files."""


def read_file(midi_filename):

    if midi_filename:
        txt_filename = midi_filename[:-3] + 'txt'
        notes_string = open('Txt test files/Cello solos/' + txt_filename).read()
        return notes_string.split(',')


def make_chains(chains, melody):
    """Takes input as a list of notes for a given melody; returns _dictionary_ of
    markov chains. A chain will be a key that consists of a tuple of (note1, note2)
    and the value would be a list of the note(s) that follow those two notes
     in the input melody.

    # For example:
    #     >>> make_chains("hi there mary hi there juanita")
    #     {('hi', 'there'): ['mary', 'juanita'], ('there', 'mary'): ['hi'], ('mary', 'hi': ['there']}
    """

    key_note1 = 0
    key_note2 = 1
    value_note = 2

    while key_note2 < (len(melody) - 1):

        key = (melody[key_note1], melody[key_note2])

        if key not in chains:
            chains[key] = []

        chains[key].append(melody[value_note])

        key_note1 += 1
        key_note2 += 1
        value_note += 1

    return chains

# ------------------------------EXECUTABLE CODE -------------------------------

# Opens + reads txt file containing all filenames of sample MIDI files.
filenames = open('test_files.txt').read().split('\n')

# Saves all melodies into a list of lists (each list being its own melody)
# (Eventually link this up to the File_converter script, so don't need to store on harddrive.)
all_melodies = []
for filename in filenames:
    notes_list = read_file(filename)
    all_melodies.append(notes_list)

# Add to the Markov chain dictionary for each melody
chains = {}
for melody in all_melodies:
    chains = make_chains(chains, melody)
