
"""
This is currently testing logistic regression...

CURRENT FEATURES INCLUDE:
(MINIMAL UP-FRONT COMPUTATION)
1. Counts on all intervals/step if bi-grams and tri-grams
(NOT pre-seeding data with 0,3,7 for minor vs. 0,4,7 for major patterns)
2. Counts of note frequency


QUESTION FOR HENRY:
The second prediction for steps frequency is not working. Should I save training
data feature columns names to build a set vocabulary for the testing set? That way
all features will still be represented even if no count present in testing data.

Error message:
ValueError: X has 1395 features per sample; expecting 1812
"""
###############################################

import music21
import pandas as pd
import numpy as np
# from pandas.tools.plotting import scatter_matrix
# import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion

def build_feature_corpus(filenames):
    """Takes MIDI files and creates feature arrays to be used for training."""

    notes_corpus = []
    steps_corpus = []
    mode_corpus = []

    # Iterating through every other file; for early trials using 1/2 files as training set, and other 1/2 to test
    for filename in filenames:

        # Convert MIDI file to score and iterate over notes in score
        # Save relevant individual Note attributes into list, including Note obj (used to calc interval) and name
        score = music21.converter.parse('MIDI test files/Cello solos/' + filename)
        note_attributes = []
        for note in music21.alpha.theoryAnalysis.theoryAnalyzer.getNotes(score, 0):
            if note == None:
                pass
            else:
                note_attributes.append([note, note.name])
        print "Note attributes for file {} completed".format(filename)

        # Creates string of all notes in a score and appends to notes_corpus
        all_notes = ""
        for note in note_attributes:
            all_notes += note[1] + " "

        notes_corpus.append(all_notes)

        # Creates string of all steps in a score and appends to steps_corpus
        all_steps = ""
        for i in range(1, len(note_attributes)):
            interval = music21.interval.Interval(noteStart=note_attributes[i-1][0], noteEnd=note_attributes[i][0])
            step = int((interval.cents)/100)
            all_steps += str(step) + ' '

        steps_corpus.append(all_steps)

        # Determines the mode (major or minor) and assigns to output corpus
        # Note: At the moment, this doesn't take into account changes b/w major + minor w/in a score
        mode_at_measure_0 = music21.alpha.theoryAnalysis.theoryAnalyzer.getKeyAtMeasure(score, 0).mode
        is_major = (mode_at_measure_0 == 'major')
        mode_corpus.append(is_major)

    return notes_corpus, steps_corpus, mode_corpus


def build_notes_feature_vector_and_fit_model(notes_corpus, mode_corpus):

    notes_vectorizer = TfidfVectorizer(min_df=1, analyzer='word', stop_words=None, token_pattern=r'\w#?-?')

    X_train = notes_vectorizer.fit_transform(notes_corpus)
    y_train = np.ravel(mode_corpus)

    classifier = LogisticRegression()
    classifier.fit(X_train, y_train)
    print "TRAINING SET SCORE: ", classifier.score(X_train, y_train)

    return notes_vectorizer, classifier


def build_steps_feature_vector_and_fit_model(steps_corpus, mode_corpus):

    steps_vectorizer = TfidfVectorizer(min_df=1, analyzer='word', stop_words=None, ngram_range=(2, 3), token_pattern=r'\d\d?')

    X_train = steps_vectorizer.fit_transform(steps_corpus)
    y_train = np.ravel(mode_corpus)

    classifier = LogisticRegression()
    classifier.fit(X_train, y_train)
    print "TRAINING SET SCORE: ", classifier.score(X_train, y_train)

    return steps_vectorizer, classifier


def build_test_feature_vector_and_predict(vectorizer, classifier, test_corpus, mode_corpus):

    X_test = vectorizer.transform(test_corpus)
    print type(X_test), X_test.shape
    print "TESTING VECTOR: ", X_test
    print ""
    prediction = classifier.predict(X_test)
    print 'PREDICTION:', prediction
    print type(prediction)
    print ""

# ------------------------------Executable Code --------------------------------

# read test files and construct columns
filenames = open('test_files.txt').read().split('\n')

# Build training feature vectors and classifiers from input midi files
notes_corpus_training, steps_corpus_training, mode_corpus_training = build_feature_corpus(filenames[::2])
notes_vectorizer, notes_classifier = build_notes_feature_vector_and_fit_model(notes_corpus_training, mode_corpus_training)
steps_vectorizer, steps_classifier = build_steps_feature_vector_and_fit_model(steps_corpus_training, mode_corpus_training)

# Predict testing data using notes classifier
notes_corpus_testing, steps_corpus_testing, mode_corpus_testing = build_feature_corpus(filenames[1::2])
build_test_feature_vector_and_predict(notes_vectorizer, notes_classifier, notes_corpus_testing, mode_corpus_testing)
build_test_feature_vector_and_predict(steps_vectorizer, steps_classifier, steps_corpus_testing, mode_corpus_testing)


# ------------------------- OLD CODE, DELETE THIS ------------------------------


# def fit_and_transform_feature_vectors(notes_corpus, steps_corpus):

#     # Creates weighted vector of note frequency for each score
#     notes_vectorizer = TfidfVectorizer(min_df=1, analyzer='word', stop_words=None, token_pattern=r'\w#?-?')
#     note_freq_vectors = notes_vectorizer.fit_transform(notes_corpus)
#     # print note_freq_vectors

#     # Creates weighted vector of step frequency for each score
#     steps_vectorizer = TfidfVectorizer(min_df=1, analyzer='word', stop_words=None, ngram_range=(2, 3), token_pattern=r'\d\d?')
#     step_freq_vectors = steps_vectorizer.fit_transform(steps_corpus)
#     # print step_freq_vectors

#     return note_freq_vectors, step_freq_vectors


## run logistic regression on training set:
# def run_log_regression(training_vector, output_vector):
#     """Runs logistic regression on training feature vectors with provided outcomes."""

#     X_train = training_vector
#     y_train = np.ravel(output_vector)

#     # # Creating classifiers
#     lr = LogisticRegression()

#     # # Fit model to the training data
#     model = lr.fit(X_train, y_train)
#     print model.score(X_train, y_train)

#     return model


# def transform_feature_vectors(notes_corpus, steps_corpus):

#     # Creates weighted vector of note frequency for each score
#     notes_vectorizer = TfidfVectorizer(min_df=1, analyzer='word', stop_words=None, token_pattern=r'\w#?-?')
#     note_freq_vectors = notes_vectorizer.transform(notes_corpus)
#     # print note_freq_vectors

#     # Creates weighted vector of step frequency for each score
#     steps_vectorizer = TfidfVectorizer(min_df=1, analyzer='word', stop_words=None, ngram_range=(2, 3), token_pattern=r'\d\d?')
#     step_freq_vectors = steps_vectorizer.transform(steps_corpus)
#     # print step_freq_vectors

#     return note_freq_vectors, step_freq_vectors


# def predict_outcomes(lr_model, testing_vector, outcomes):
#     """Taking the logistic regression model and new testing data, predict mode outcomes."""
#     print testing_vector.shape

#     count = 0
#     for i in range(testing_vector.shape[0]):
#         print i, testing_vector[i].shape
#         prediction = lr_model.predict(testing_vector[i])
#         actual_outcome = outcomes[i]
#         print prediction, actual_outcome
#         if prediction == actual_outcome:
#             print "SUCCESS!"
#             count += 1

#     print "Of {} testing files, this model predicted {} correctly.".format(len(testing_vector), count)

