"""This script will take in a list of filenames for convertion of its notes
(including rests) to a text file. Data is saved in the format of a list of notes,
ex. ['G2', D3, 'B3', None, 'A3', 'B3']. Txt files can then be used directly in
Markov.py to convert frequency of notes to Markov chains.

Run the following in CLI to get txt file including list of filenames:
>>> ls MIDI\ test\ files/Cello\ solos/ > sample_files.txt

"""

import music21


files = open('sample_files.txt').read().split('\n')

for filename in files:
    score = music21.converter.parse('MIDI test files/Cello solos/' + filename)

    data_file = open('Txt test files/Cello solos/' + filename[:-3] + 'txt', 'w')

    notes = ""
    for note in music21.alpha.theoryAnalysis.theoryAnalyzer.getNotes(score, 0):
        if note == None:
            notes = ','.join([notes, 'None'])
        else:
            notes = ','.join([notes, note.name + str(note.octave)])

    data_file.write(notes[1:])
