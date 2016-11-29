import music21
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin
import cPickle


class Analyzer(object):

    def __init__(self, name, pickle_file, features, parameters=None):
        self.name = name
        self.pickle_file = pickle_file
        self.features = features
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
        """Loads pickle for given analyzer, and makes proba prediction for a melody."""

        self.load_pickle()
        features = Analyzer.build_features_from_melody(melody)
        probabilities_ndarray = self.pipeline.predict_proba(features)

        return probabilities_ndarray

    def calculate_probability_of_mode(self, melody, mode):
        """Returns only prediction probability relevant to our users mode input."""

        probabilities_ndarray = self.predict_mode(melody)
        if mode is True:
            probability = probabilities_ndarray.tolist()[0][1]
        else:
            probability = probabilities_ndarray.tolist()[0][0]

        return probability

    @classmethod
    def build_comparison(cls, all_analyzers, melody, mode):
        """Crafts analyzer comparison dictionary for all analyzers and outcomes."""

        all_probabilities = []
        analyzer_comparison = {"Logistic Regression": {'Notes': None,
                                                       'Steps': None,
                                                       'Both': None,
                                                       },
                               "Naive Bayes": {'Notes': None,
                                               'Steps': None,
                                               'Both': None,
                                               },
                               "Support Vector Classification": {'Notes': None,
                                                                 'Steps': None,
                                                                 'Both': None,
                                                                 },
                               }

        print "Beginning to iterate over analyzers..."
        for analyzer in all_analyzers:
            probability = analyzer.calculate_probability_of_mode(melody, mode)
            analyzer_comparison[analyzer.name][analyzer.features] = probability

            all_probabilities.append(probability)

        return analyzer_comparison, all_probabilities

    @staticmethod
    def build_chart_data(analyzer_comparison):
        """Crafts dictionary of classifier/feature vector outcomes for ChartJS. """

        chart_data = {"labels": ["Linear Regression", "Multinomial NB", "Support Vector Classification"],
                      "datasets": [{"data": [analyzer_comparison['Logistic Regression']['Notes'],
                                             analyzer_comparison['Naive Bayes']['Notes'],
                                             analyzer_comparison['Support Vector Classification']['Notes'],
                                             ],
                                    "backgroundColor": ['#ff9900', '#ff9900', '#ff9900'],
                                    "hoverBackgroundColor": ['#ffd699', '#ffd699', '#ffd699'],
                                    "label": "Notes Only",
                                    },
                                   {"data": [analyzer_comparison['Logistic Regression']['Steps'],
                                             analyzer_comparison['Naive Bayes']['Steps'],
                                             analyzer_comparison['Support Vector Classification']['Steps'],
                                             ],
                                    "backgroundColor": ['#0066ff', '#0066ff', '#0066ff'],
                                    "hoverBackgroundColor": ['#99c2ff', '#99c2ff', '#99c2ff'],
                                    "label": "Steps Only",
                                    },
                                   {"data": [analyzer_comparison['Logistic Regression']['Both'],
                                             analyzer_comparison['Naive Bayes']['Both'],
                                             analyzer_comparison['Support Vector Classification']['Both']],
                                    "backgroundColor": ['#339966', '#339966', '#339966'],
                                    "hoverBackgroundColor": ['#9fdfbf', '#9fdfbf', '#9fdfbf'],
                                    "label": "Both Notes + Steps",
                                    }
                                   ]
                      }

        return chart_data


# THIS SHOULD EVENTUALLY BY PART OF DB. FOR NOW SEED DATA UPLOADED EACH TIME APP STARTS.
lr_notes = Analyzer('Logistic Regression', 'pipelines/pipeline_lr_notes.txt', 'Notes')
lr_steps = Analyzer('Logistic Regression', 'pipelines/pipeline_lr_steps.txt', 'Steps')
lr_both = Analyzer('Logistic Regression', 'pipelines/pipeline_lr_both.txt', 'Both')

nb_notes = Analyzer('Naive Bayes', 'pipelines/pipeline_nbm_notes.txt', 'Notes')
nb_steps = Analyzer('Naive Bayes', 'pipelines/pipeline_nbm_steps.txt', 'Steps')
nb_both = Analyzer('Naive Bayes', 'pipelines/pipeline_nbm_both.txt', 'Both')

svc_notes = Analyzer('Support Vector Classification', 'pipelines/pipeline_svc_notes.txt', 'Notes')
svc_steps = Analyzer('Support Vector Classification', 'pipelines/pipeline_svc_steps.txt', 'Steps')
svc_both = Analyzer('Support Vector Classification', 'pipelines/pipeline_svc_both.txt', 'Both')
all_analyzers = [lr_notes, lr_steps, lr_both, nb_notes, nb_steps, nb_both, svc_notes, svc_steps, svc_both]
# all_analyzers = [lr_notes, lr_steps, lr_both]
