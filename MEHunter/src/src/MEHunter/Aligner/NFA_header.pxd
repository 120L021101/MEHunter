from libcpp.string cimport string

cdef extern from "NFA_c.h" namespace "NFA_space":
    float align_c(string seq1, string seq2, float min_score)