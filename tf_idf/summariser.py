import spacy
import textwrap
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest

punctuation += '\n'
stopwords = list(STOP_WORDS)
nlp_pl = spacy.load('en_core_web_sm')

class summariser:
    def __init__(self):
        self.reduction_rate = 0.5
        self.document = ''
        self.word_frequencies = {}
        self.sentence_tokens = []
        self.sentence_scores = {}
        self.relation_value = False

    def set_text(self, txt):
        self.document = nlp_pl(txt)  # doc object

    def set_reduction_rate(self, rate):
        self.reduction_rate = rate

    def set_relation_value(self, rel):
        self.relation_value = rel

    def set_sentence_token(self):
        self.sentence_tokens = [sent for sent in self.document.sents]

    def get_tokens(self):
        tokens = [token.text for token in self.document]  # tokenized text
        return tokens

    def get_word_frequencies(self):
        for word in self.document:
            if word.text.lower() not in stopwords:
                if word.text.lower() not in punctuation:
                    if word.text not in self.word_frequencies.keys():
                        self.word_frequencies[word.text] = 1
                    else:
                        self.word_frequencies[word.text] += 1

    def normalize_word_frequencies(self):
        max_frequency = max(self.word_frequencies.values())
        for word in self.word_frequencies.keys():
            self.word_frequencies[word] = self.word_frequencies[word] / max_frequency

    def get_sentence_scores(self):
        for sent in self.sentence_tokens:
            word_count = 0
            for word in sent:
                if word.text.lower() in self.word_frequencies.keys():
                    word_count += 1
                    if sent not in self.sentence_scores.keys():
                        self.sentence_scores[sent] = self.word_frequencies[word.text.lower()]
                    else:
                        self.sentence_scores[sent] += self.word_frequencies[word.text.lower()]
            if self.relation_value and word_count != 0:
                self.sentence_scores[sent] = self.sentence_scores[sent] / word_count

    def get_summary(self):
        summary_length = int(len(self.sentence_scores) * self.reduction_rate)
        summary = nlargest(summary_length, self.sentence_scores, key=self.sentence_scores.get)
        final_summary = [word.text for word in summary]
        summary = ' '.join(final_summary)
        return summary

    def get_summarised_text(self):
        self.get_word_frequencies()
        self.normalize_word_frequencies()
        self.set_sentence_token()
        self.get_sentence_scores()
        summary = self.get_summary()
        if summary == "":
            # print('hi')
            self.reduction_rate = 1.0
            return self.get_summary()
        else: return summary

    def set_obj_null(self):
        self.reduction_rate = 0.5
        self.document = ''
        self.word_frequencies = {}
        self.sentence_tokens = []
        self.sentence_scores = {}
        self.relation_value = False