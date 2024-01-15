# distutils: language = c++
# cython: language_level=3
from MEHunter.Aligner.NFA_header cimport align_c

class Aligner():
    def __init__(self, min_score = 0.7) -> None:
        self.min_score = min_score

    def align(self, seq1, seq2, min_score = 0.7):
        '''
        this is an adapter
        '''
        return align_c(seq1=seq1.encode(), seq2=seq2.encode(), min_score=min_score)
