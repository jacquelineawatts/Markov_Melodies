
"""
This is currently testing logistic regression with both notes + steps feature vectors.
See additional trials in machine_learning_tests directory.

CURRENT FEATURES INCLUDE:
1. Counts on all intervals/step if bi-grams and tri-grams
(NOT pre-seeding data with 0,3,7 for minor vs. 0,4,7 for major patterns)
2. Counts of note frequency, both single notes and bi-grams

Current score:
Current outcome on validation data: 83.74%

Next steps:
1. Calculate precision vs. recall using metrics submodule.
        Consider plotting this curve and playing w/threshold
2. Look up cross-validation module to better balance input datasets
3. Run K-nearest neighbors for baseline.
4. Consider SVM for more complex comparison
        Tho this typically needs more parameter fine-tuning...

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
from sklearn.base import BaseEstimator, TransformerMixin
import cPickle


class ItemSelector(BaseEstimator, TransformerMixin):

    def __init__(self, key):
        self.key = key

    def fit(self, x, y=None):
        return self

    def transform(self, data_dict):
        return data_dict[self.key]


def build_feature_corpus(corpus):
    """Takes MIDI files and creates feature arrays to be used for training."""

    features = {}
    notes_corpus, steps_corpus, mode_corpus = [], [], []

    # Convert MIDI file to score and iterate over notes in score
    # Save relevant individual Note attributes into list, including Note obj (used to calc interval) and name
    for score in corpus:
        score = music21.corpus.parse(score)
        all_notes = ""
        notes = []
        for note in music21.alpha.theoryAnalysis.theoryAnalyzer.getNotes(score, 0):
            if note == None:
                pass
            else:
                notes.append(note)
                all_notes += note.name + " "

        notes_corpus.append(all_notes)

        # Creates string of all steps in a score and appends to steps_corpus
        all_steps = ""
        for i in range(1, len(notes)):
            interval = music21.interval.Interval(noteStart=notes[i-1], noteEnd=notes[i])
            step = int((interval.cents)/100)
            all_steps += str(step) + ' '

        steps_corpus.append(all_steps)

        mode_at_measure_0 = music21.alpha.theoryAnalysis.theoryAnalyzer.getKeyAtMeasure(score, 0).mode
        mode_corpus.append((mode_at_measure_0 == 'major'))

    features['notes_freq'], features['steps_freq'], features['outcomes'] = notes_corpus, steps_corpus, mode_corpus
    return features


def build_feature_vector_and_fit_model(features):

    pipeline = Pipeline([
        ('features', FeatureUnion(
            transformer_list=[
                ('notes', Pipeline([
                    ('selector', ItemSelector(key='notes_freq')),
                    ('tfidf', TfidfVectorizer(min_df=1, analyzer='word', stop_words=None, ngram_range=(1, 2), token_pattern=r'\w#?-?')),
                ])),
                ('steps', Pipeline([
                    ('selector', ItemSelector(key='steps_freq')),
                    ('tfidf', TfidfVectorizer(min_df=1, analyzer='word', stop_words=None, ngram_range=(2, 3), token_pattern=r'\d\d?'))
                ])),
            ])),

        ('classifier', LogisticRegression()),
        ])

    pipeline.fit(features_and_outcomes_dict, np.ravel(features_and_outcomes_dict['outcomes']))

    return pipeline


def predict(pipeline, validation_features):
    """Takes notes_corpus as a list of test scores (each a string of notes)."""

    predictions = pipeline.predict(validation_features)
    # outcomes = validation_features['outcomes']
    print 'PREDICTION:', predictions
    # print ""
    # print 'ACTUAL OUTCOMES: ', outcomes

    # count = 0
    # for i in range(len(predictions)):
    #     if predictions[i] == outcomes[i]:
    #         count += 1

    # print '{} correct predictions out of {} sample test files'.format(count, len(outcomes))
    # print float(count)/len(outcomes) * 100

    return predictions[0]


# ------------------------------Executable Code --------------------------------

if __name__ == "__main__":
    # read test files and construct training vs validation datasets
    scores = music21.corpus.getComposer('ryansMammoth')

    training_files = scores[::2]
    validation_files = scores[1::2]

    # Build training features from input midi files
    features_and_outcomes_dict = build_feature_corpus(training_files)
    trained_pipeline = build_feature_vector_and_fit_model(features_and_outcomes_dict)

    # Build features for validation data set of midi files.
    validation_features = build_feature_corpus(validation_files)
    predict(trained_pipeline, validation_features)

    # PLACING ITEMSELECTOR CLASS IN PICKLE HERE IS NOT WORKING, DOESN'T ALLOW
    # FILE TO LOAD IN MELODY.PY FILE.

    pipeline_file = open('static/pipeline.txt', 'w')
    cPickle.dump(trained_pipeline, pipeline_file)
    print "Pickled the pipeline to /static/pipeline.txt."
    pipeline_file.close()
