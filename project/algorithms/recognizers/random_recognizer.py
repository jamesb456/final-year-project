import random

from project.algorithms.recognizers.extract_recognizer import ExtractRecognizer


class RandomRecognizer(ExtractRecognizer):
    def recognize(self, extract, candidates):
        return map(lambda __: random.uniform(0.0, 1.0), candidates)
