

cdef list seq2img_faster_cython(list seq_ls, int size = 256):
    cdef list imgs = []
    cdef dict transforms
    cdef list data
    cdef list r_data
    cdef int start
    cdef int end
    cdef int seq_len

    transforms = {
        'A' : 0,
        'C' : 1,
        'G' : 2,
        'T' : 3,
        'N' : 4
    }
    seq_ls = [[transforms.get(ch, transforms['N']) for ch in seq] for seq in seq_ls]
    for i, seq in enumerate(seq_ls):
        seq2 = seq
        while len(seq2) <= 2 * size:
            seq2 += [val + 2 for val in seq]
        seq_len = len(seq2) // 2
        start = 0
        end = size
        data = []
        for j in range(size):
            data.append(seq2[start : end] if start < end else seq2[start : end + seq_len])
            start += size
            end += size
            if start >= seq_len:
                for i, val in enumerate(seq2):
                    seq2[i] = val + 0.05
                start -= seq_len
            if end >= seq_len:
                end -= seq_len

        seq2.reverse()
        start = 0
        end = size
        r_data = []
        for j in range(size):
            r_data.append(seq2[start : end] if start < end else seq2[start : end + seq_len])
            start += size
            end += size
            if start >= seq_len:
                start -= seq_len
            if end >= seq_len:
                end -= seq_len
        imgs.append([data, r_data])

    return imgs

def seq2img_faster(list seq_ls, size=256):
    return seq2img_faster_cython(seq_ls, size=size)