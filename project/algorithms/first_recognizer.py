from project.algorithms.extract_recognizer import ExtractRecognizer


class FirstRecognizer(ExtractRecognizer):
    def recognize(self, extract, candidates):
        return range(len(candidates) - 1, -1, -1)
