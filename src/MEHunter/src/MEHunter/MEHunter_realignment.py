from MEHunter_pyNFA import Aligner
import os, sys, logging
from multiprocessing import Process

logFormat = "%(asctime)s [%(levelname)s] %(message)s"
aligner = Aligner()

class MEfamily:

    def __init__(self, family_name) -> None:
        self.family_name = family_name
        self.seqs = []

def load_sequences(args, Alu, SVA, L1):
    if not os.path.isfile(args.known_ME):
        logging.basicConfig( stream=sys.stderr, level=logging.ERROR, format=logFormat )
        logging.error("No Such File: {}, check positional param known_ME".format(args.known_ME))
        exit()
    with open(file=args.known_ME, mode='r', encoding='utf-8') as sequences_loader:
        pick_family = None; seq = []
        for line in sequences_loader:
            if line.startswith('>'):
                if pick_family:
                    pick_family.seqs.append(''.join(seq))
                    seq = []; pick_family = None
                if 'Alu' in line: pick_family = Alu
                if 'SVA' in line: pick_family = SVA
                if 'L1'  in line: pick_family = L1
            else:
                seq.append(line.strip().upper())

def load_cluster(args):
    insertions = []; deletions = []
    for i, name in enumerate(['ins', 'del']):
        INSERTION_FLAG, DELETION_FLAG = i == 0, i == 1
        cluster_path = os.path.join( args.work_dir, "{}.cluster".format(name) )
        with open(file=cluster_path, mode='r', encoding='utf-8') as cluster_loader:
            for line in cluster_loader:
                info_ls = line.strip().split('\t')
                if INSERTION_FLAG: insertions.append(info_ls)
                if DELETION_FLAG:  deletions.append (info_ls)
    return insertions, deletions

def re_alignment(args):
    '''
    re_align ME labeled sequences to corresponding subfamily of ME
    '''
    (Alu, SVA, L1) = (MEfamily('Alu'), MEfamily('SVA'), MEfamily('L1'))
    ME_families = [Alu, SVA, L1]
    # load known sequences
    load_sequences(args, Alu, SVA, L1)
    insertions, deletions = load_cluster(args=args)
    ME_insertions, ME_deletions = [], []
    failed_writers = [
        open(file=os.path.join(args.work_dir, 'failed_ins.cluster'), mode='w', encoding='utf-8'),
        open(file=os.path.join(args.work_dir, 'failed_del.cluster'), mode='w', encoding='utf-8')
    ]
    for (variants, records, failed_writer) in zip([insertions, deletions], [ME_insertions, ME_deletions], \
                                                    failed_writers):
        for variant in variants:
            if_failed = True
            for ME_family in ME_families:
                for sequence in ME_family.seqs:
                    if len(variant[3]) < 20: continue
                    # print(insertion, sequence)
                    if aligner.align( variant[3], sequence ) > 0.7:
                        variant.append(ME_family.family_name)
                        records.append(variant)
                        if_failed = False; break
                if not if_failed: break
            if if_failed:
                failed_writer.write(
                    "{}\n".format( '\t'.join(variant) )
                )
    failed_writers[0].close(); failed_writers[1].close()
    return ME_insertions, ME_deletions