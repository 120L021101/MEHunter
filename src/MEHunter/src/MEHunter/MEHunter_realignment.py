from MEHunter_pyNFA import Aligner
import os, sys, logging, random
from multiprocessing import Process
from MEHunter.MEHunter_utils import call

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
                    pick_family.seqs.append((''.join(seq)).encode())
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

def sw_algorith_main(*args):
    failed_writer, success_writer, variants, ME_families, process_id = args
    print("process {} starts".format(process_id))
    for variant in variants:
        variant_seq = variant[3].encode(); variant_length = len(variant[3])
        if variant_length < 100: continue
        
        if_failed = True
        for ME_family in ME_families:
            for sequence in ME_family.seqs:
                # print(insertion, sequence)
                standard = 0.7
                if abs(len(sequence) - variant_length) / max(len(sequence), variant_length) > 1 - standard:
                    continue
                if aligner.align( variant_seq, sequence, standard ) > standard:
                    variant.append(ME_family.family_name)
                    success_writer.write(str(variant) + '\n'); success_writer.flush()
                    if_failed = False; break
            if not if_failed: break

        if if_failed:
            failed_writer.write("{}\n".format( '\t'.join(variant) )); failed_writer.flush()

def re_alignment(args, MEI_writer, MED_writer):
    '''
    re_align ME labeled sequences to corresponding subfamily of ME
    '''
    (Alu, SVA, L1) = (MEfamily('Alu'), MEfamily('SVA'), MEfamily('L1'))

    ME_families = [Alu, SVA, L1]
    # load known sequences
    load_sequences(args, Alu, SVA, L1)
    insertions, deletions = load_cluster(args=args)
    failed_writers = [
        open(file=os.path.join(args.work_dir, 'failed_ins.cluster'), mode='w', encoding='utf-8'),
        open(file=os.path.join(args.work_dir, 'failed_del.cluster'), mode='w', encoding='utf-8')
    ]
    for flag, (variants, writer, failed_writer) in enumerate(zip([insertions, deletions], [MEI_writer, MED_writer], \
                                                    failed_writers)):
        INSERTION_FLAG, DELETION_FLAG = flag == 0, flag == 1
        process_variants = []
        for i in range(args.threads): process_variants.append([])
        pick_idx = 0
        for variant in variants:
            process_variants[pick_idx].append(variant)
            pick_idx = (pick_idx + 1) % args.threads 

        process_failed_writer = []; process_success_writer = []
        for i in range(args.threads):
            sv_type = 'ins' if INSERTION_FLAG else 'del'
            sub_failed_path  = os.path.join(args.work_dir, 'failed_{}{}.cluster').format(sv_type, i + 1)
            sub_success_path = os.path.join(args.work_dir, 'success_{}{}.cluster').format(sv_type, i + 1)
            process_failed_writer.append(open(file=sub_failed_path, mode='w', encoding='utf-8'))
            process_success_writer.append(open(file=sub_success_path, mode='w', encoding='utf-8'))
        process_list = []
        for i in range(args.threads):
            process_list.append(Process(target=sw_algorith_main, args=
                (process_failed_writer[i], process_success_writer[i], process_variants[i], ME_families, i)))
            process_list[i].start()
        for i in range(args.threads):
            process_list[i].join()
            process_failed_writer[i].close(); process_success_writer[i].close()

            sv_type = 'ins' if INSERTION_FLAG else 'del'
            sub_success_path = os.path.join(args.work_dir, 'success_{}{}.cluster').format(sv_type, i + 1)
            sub_success_reader = open(file=sub_success_path, mode='r', encoding='utf-8')
            for line in sub_success_reader:
                info_ls = eval(line.strip()); info_ls[1] = str(info_ls[1])
                writer.write("{}\n".format(info_ls))
            sub_success_reader.close()

            call('rm {}'.format(sub_success_path))

            sub_failed_path = os.path.join(args.work_dir, 'failed_{}{}.cluster').format(sv_type, i + 1)
            sub_failed_reader = open(file=sub_failed_path, mode='r', encoding='utf-8')
            for line in sub_failed_reader:
                failed_writer.write(line)
            sub_failed_reader.close()

            call('rm {}'.format(sub_failed_path))

    failed_writers[0].close(); failed_writers[1].close()
