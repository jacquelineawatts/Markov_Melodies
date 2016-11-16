import music21
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin
import cPickle


class Analyzer(object):

    def __init__(self, name, pickle_file, analyzes_notes, analyzes_steps, parameters=None):
        self.name = name
        self.pickle_file = pickle_file
        self.analyzes_notes = analyzes_notes
        self.analyzes_steps = analyzes_steps
        self.parameters = parameters
        self.pipeline = None


    def load_pickle(self):
        pipeline_file = open(self.pickle_file)
        pipeline = cPickle.load(pipeline_file)
        pipeline_file.close()

        self.pipeline = pipeline

    @classmethod
    def build_notes_corpus(cls, melody):
        """Takes in melody and preprocesses notes_freq for vectorization."""

        notes_corpus = []
        all_notes = ""

        notes = []
        for note in melody:
            notes.append(note.pitch + str(note.octave))
            all_notes += note.pitch + " "

        notes_corpus.append(all_notes)

        return notes_corpus, notes

    @classmethod
    def build_steps_corpus(cls, melody, notes):
        """Takes in melody and preprocesses steps_freq for vectorization."""

        steps_corpus = []
        all_steps = ""

        for i in range(1, len(notes)):
            note_start = music21.note.Note(notes[i-1])
            note_end = music21.note.Note(notes[i])
            interval = music21.interval.Interval(noteStart=note_start, noteEnd=note_end)
            step = int((interval.cents)/100)
            all_steps += str(step) + ' '

        steps_corpus.append(all_steps)
        return steps_corpus

    @classmethod
    def build_features_from_melody(cls, melody):
        """Builds feature dictionary to pass to pipeline."""

        features = {}
        features['notes_freq'], notes = Analyzer.build_notes_corpus(melody)
        features['steps_freq'] = Analyzer.build_steps_corpus(melody, notes)
        return features

    def predict_mode(self, melody):
        """Given a melody """

        self.load_pickle()
        features = Analyzer.build_features_from_melody(melody)
        probabilities = self.pipeline.predict_proba(features)

        return probabilities

    def construct_outcome_dict(self, melody, mode):

        outcome_dict = {}
        probability_ndarray = self.predict_mode(melody)
        if mode is True:
            probability = probability_ndarray.tolist()[0][1]
        else:
            probability = probability_ndarray.tolist()[0][0]
        outcome_dict['probability'] = probability
        outcome_dict['melody'] = melody

        return outcome_dict

    @classmethod
    def build_comparison(cls, all_analyzers, melody, mode):

        all_probabilities = []
        analyzer_comparison = {"Logistic Regression": {(True, False): {},
                                                       (False, True): {},
                                                       (True, True): {},
                                                       },
                               "Naive Bayes": {(True, False): {},
                                               (False, True): {},
                                               (True, True): {},
                                               },
                               "Support Vector Classification": {(True, False): {},
                                                                 (False, True): {},
                                                                 (True, True): {},
                                                                 },
                               }

        for analyzer in all_analyzers:
            features_tuple = (analyzer.analyzes_notes, analyzer.analyzes_steps)
            outcomes_dict = analyzer.construct_outcome_dict(melody, mode)
            analyzer_comparison[analyzer.name][features_tuple] = outcomes_dict

            all_probabilities.append(outcomes_dict['probability'])

        return analyzer_comparison, all_probabilities


lr_notes = Analyzer('Logistic Regression', 'static/pipeline.txt', True, False)
lr_steps = Analyzer('Logistic Regression', 'static/pipeline.txt', False, True)
lr_both = Analyzer('Logistic Regression', 'static/pipeline.txt', True, True)

nb_notes = Analyzer('Naive Bayes', 'static/pipeline.txt', True, False)
nb_steps = Analyzer('Naive Bayes', 'static/pipeline.txt', False, True)
nb_both = Analyzer('Naive Bayes', 'static/pipeline.txt', True, True)

svc_notes = Analyzer('Support Vector Classification', 'static/pipeline.txt', True, False)
svc_steps = Analyzer('Support Vector Classification', 'static/pipeline.txt', False, True)
svc_both = Analyzer('Support Vector Classification', 'static/pipeline.txt', True, True)
all_analyzers = [lr_notes, lr_steps, lr_both, nb_notes, nb_steps, nb_both, svc_notes, svc_steps, svc_both]
