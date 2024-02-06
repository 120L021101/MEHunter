import time
def get_seed(seq, kmer):
    start = 0
    end = kmer
    seeds = set()
    while end <= len(seq):
        seeds.add(seq[start : end])
        start += 1
        end += 1
    return seeds


def align(seq1, seq2, min_score = 0.7):
    kmer = 6
    seq2_seeds = get_seed(seq=seq2, kmer=kmer)    
    best_start = 0
    start = 0
    end = len(seq2)
    score = 0
    #冷启动
    s, e = 0, kmer
    while e <= end:
        if seq1[s : e] in seq2_seeds:
            score += 1
        s += 1
        e += 1
    #启动
    max_score = score
    ano_score = (epsilon_NFA(seq1=seq1[:10], seq2=seq2[:10]) + epsilon_NFA(seq1=seq1[:len(seq2)][-10:], seq2=seq2[-10:])) / 2
    while end < len(seq1):
        end += 1
        remove_kmer = seq1[start : start + kmer]
        if remove_kmer in seq2_seeds:
            score -= 1
        add_kmer = seq1[end - kmer : end]
        if add_kmer in seq2_seeds:
            score += 1
        start += 1
        if score > max_score:
            cur_seq = seq1[start : start + len(seq2)]
            a_score = (epsilon_NFA(seq1=cur_seq[:10], seq2=seq2[:10]) + epsilon_NFA(seq1=cur_seq[-10:], seq2=seq2[-10:])) / 2
            if a_score >= ano_score:
                max_score = score
                best_start = start
                ano_score = a_score

    return epsilon_NFA(seq1=seq1[best_start : best_start + len(seq2)], seq2=seq2, min_score=min_score)



def epsilon_NFA(seq1, seq2, min_score = 0.7, window_size = 2000):
    # print(len(seq1), len(seq2))
    window_size = int( len(seq2) * (1 - min_score) ) + 1
    max_epochs = int( len(seq2) * (2 - min_score) ) + 1
    epoch = 0 # epoch also refers to the biggest index of all activated states
    states = [ -1 ] * (len(seq1) + 1)
    states[0] = 0

    while epoch < max_epochs:
        # print(epoch, states)
        for s_idx in range(min(len(seq1), epoch), max(0, epoch - window_size) - 1, -1):
            if s_idx == len(seq1):
                states[s_idx] += 1
                continue
            if states[s_idx] < len(seq2) and seq1[s_idx] == seq2[states[s_idx]]:
                states[s_idx + 1] = max(
                    states[s_idx + 1],
                    states[s_idx] + 1
                )
            else:
                states[s_idx + 1] = max(
                    states[s_idx + 1],
                    states[s_idx]
                )
            states[s_idx] += 1

        epoch += 1 
        if states[-1] == len(seq2): break
    
    if epoch == max_epochs:
        return 0
    # print(epoch, len(seq1), len(seq2))
    return max(0, min(1 - abs(epoch - len(seq2)) / len(seq2), 1 - abs(epoch - len(seq1)) / len(seq1)))

def epsilon_NFA2(seq1, seq2, min_score = 0.7):
    pass

class Aligner():
    def __init__(self, min_score = 0.7) -> None:
        self.aligner = align
        self.min_score = min_score

    def align(self, seq1, seq2):
        '''
        this is an adapter
        '''
        return self.aligner(seq1=seq1, seq2=seq2, min_score=self.min_score)

if __name__ == "__main__":
    strand_dict = {
        'A' : 'T',
        'T' : 'A',
        'C' : 'G',
        'G' : 'C'
    }
    seq1='''
GGCCGGGCGCGGTGGCTCACGCTTGTAATCCCAGCACTTTGGGAGGCCGAGGCGGGCGGATCACGAGGTCAGGAGATCGAGACCATCCTG
GCTAACACGGTGAAACCCCGTCTCTACTAAAAATACAAAAAATTAGCCGGGCGTGATGGCGGGCGCCTGTAGTCCCAGCTACTCGGGAGG
CTGAGGCAGGAGAATGGCGTGAACCCGGGAGGCGGAGCTTGCAGTGAGCCGAGATTGCGCCACTGCACTCCCGCCTGGGCCACAGAGCGA
GACTCCGTCTCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
'''.replace('\n', '')
    seq2='''
TATTACTGCTTTTTTTTTTTTTTTTTTTTTTTTTTGAGACGGAGTCTCGCTCTGTGGCCCAGGCGGGAGTGCAGTGGCGCAATCTCGGCTCACTGCAAGCTCCGCCTCCCGGGTTCACGCCATTCTCCTGCCTCAGCCTCCCGAGTAGCTAGGACTACAGGCGCCCACCATCACGCCCGGCTAATTTTTTTGTATTTTTTTTAGTAGAGACGGGGTTTCACCGTGTTAGCCAGGATGGTCTCGATCTCCTGACCTCGTGATCCGCCCACCTCGGCCTCCCAAAGTGCTGGGATTACAAGCGTGAGCCACCGCGCCCGGCCCN
'''.replace('\n', '')
    print(align(seq1=seq1, seq2=seq2, min_score=0.3))
    seq1 = ''.join([strand_dict.get(ch, ch) for ch in seq1])[::-1]
    print(seq1)
    print(align(seq1=seq1, seq2=seq2, min_score=0.3))
    exit()