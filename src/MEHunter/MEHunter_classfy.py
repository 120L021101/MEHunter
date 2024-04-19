
import logging
import pysam
import subprocess, os, sys
from typing import *
from MEHunter.pre_classifier.utils import infer, load_module
from MEHunter.MEHunter_utils import call, is_empty

logFormat = "%(asctime)s [%(levelname)s] %(message)s"

def activate_BERT(args): load_module(args)
def BERT_classify(args): infer(args)

def load_cluster(work_dir):
    insertions = []; deletions = []
    for i, name in enumerate(['ins', 'del']):
        INSERTION_FLAG, DELETION_FLAG = i == 0, i == 1
        cluster_path = os.path.join( work_dir, "{}.cluster".format(name) )
        with open(file=cluster_path, mode='r', encoding='utf-8') as cluster_loader:
            for line in cluster_loader:
                info_ls = line.strip().split('\t')
                if INSERTION_FLAG: insertions.append(info_ls)
                if DELETION_FLAG:  deletions.append (info_ls)
    return insertions, deletions


def re_re_alignment(args) -> Optional[List] and Optional[List]:
    MEI_path = os.path.join(args.work_dir, 'Candidate_MEIs.txt'); MED_path = os.path.join(args.work_dir, 'Candidate_MEDs.txt')
    MEI_writer = open(file=MEI_path, mode='w', encoding='utf-8'); MED_writer = open(file=MED_path, mode='w', encoding='utf-8')   

    INS_ABNORMAL = is_empty(os.path.join(args.work_dir, 'minimap2_{}.fq'.format('ins')))
    DEL_ABNORMAL = is_empty(os.path.join(args.work_dir, 'minimap2_{}.fq'.format('del')))
    print(INS_ABNORMAL, DEL_ABNORMAL)


    for task in ['ins', 'del']:
        if INS_ABNORMAL and task == 'ins': continue
        if DEL_ABNORMAL and task == 'del': continue
        arguments = [
            args.known_ME, # input arg 1
            os.path.join(args.work_dir, 'minimap2_{}.fq'.format(task)), # input arg 2
            os.path.join(args.work_dir, 'align_{}_c2m.sam'.format(task)) # output 
        ]
        cmd = "minimap2 -a {} {} > {}".format(*arguments)
        call(cmd)

        arguments = [
            os.path.join(args.work_dir, 'minimap2_{}.fq'.format(task)), # input arg 1
            args.known_ME, # input arg 2
            os.path.join(args.work_dir, 'align_{}_m2c.sam'.format(task)) # output 
        ]
        cmd = "minimap2 -a {} {} > {}".format(*arguments)
        call(cmd)

        logging.basicConfig( stream=sys.stderr, level=logging.INFO, format=logFormat )
        logging.info("minimap2 finished the task of {}".format(task))
    
    ME_insertion_align, ME_deletion_align = {}, {}

    for (task, variant_align) in zip(['ins', 'del'], (ME_insertion_align, ME_deletion_align)):
        if INS_ABNORMAL and task == 'ins': continue
        if DEL_ABNORMAL and task == 'del': continue

        with pysam.AlignmentFile(
            filename=os.path.join(args.work_dir, 'align_{}_c2m.sam'.format(task)),
            mode='r') as align_file:

            for read in align_file:
                if not read.reference_name: continue
                ME_family_name = read.reference_name.split('.')[0]
                key_word = read.query_name.split('|')[0]
                variant_align[key_word] = ME_family_name

        with pysam.AlignmentFile(
            filename=os.path.join(args.work_dir, 'align_{}_m2c.sam'.format(task)),
            mode='r') as align_file:

            for read in align_file:
                if not read.reference_name: continue
                ME_family_name = read.query_name.split('.')[0]
                key_word = read.reference_name.split('|')[0]
                variant_align[key_word] = ME_family_name

    insertions, deletions = load_cluster(args.work_dir)
    for variants, variant_align, writer in zip((insertions, deletions), 
                                    (ME_insertion_align, ME_deletion_align),
                                    (MEI_writer, MED_writer)):
        for variant in variants:
            id_of_variant = variant[0]
            if not id_of_variant in variant_align: continue
            variant.append(variant_align[id_of_variant])
            writer.write("{}\n".format(variant))
            writer.flush()
            
    MEI_writer.close(); MED_writer.close()

def re_re_alignment2(work_dir, known_ME) -> Optional[List] and Optional[List]:
    
    for task in ['ins', 'del']:
        arguments = [
            known_ME, # input arg 1
            os.path.join(work_dir, 'dl_{}.fq'.format(task)), # input arg 2
            os.path.join(work_dir, 'align_{}_c2m.sam'.format(task)) # output 
        ]
        cmd = "minimap2 -a {} {} > {}".format(*arguments)
        res = subprocess.call(cmd, shell=True)

        arguments = [
            os.path.join(work_dir, 'dl_{}.fq'.format(task)), # input arg 1
            known_ME, # input arg 2
            os.path.join(work_dir, 'align_{}_m2c.sam'.format(task)) # output 
        ]
        cmd = "minimap2 -a {} {} > {}".format(*arguments)
        res = subprocess.call(cmd, shell=True)

        logging.basicConfig( stream=sys.stderr, level=logging.INFO, format=logFormat )
        logging.info("minimap2 finished the task of {}".format(task))
    
    ME_insertion_align, ME_deletion_align = {}, {}

    for (task, variant_align) in zip(['ins', 'del'], (ME_insertion_align, ME_deletion_align)):
        with pysam.AlignmentFile(
            filename=os.path.join(work_dir, 'align_{}_c2m.sam'.format(task)),
            mode='r') as align_file:

            for read in align_file:
                if not read.reference_name: continue
                ME_family_name = read.reference_name.split('.')[0]
                key_word = read.query_name.split('|')[0]
                ME_insertion_align[key_word] = ME_family_name

        with pysam.AlignmentFile(
            filename=os.path.join(work_dir, 'align_{}_m2c.sam'.format(task)),
            mode='r') as align_file:

            for read in align_file:
                if not read.reference_name: continue
                ME_family_name = read.query_name.split('.')[0]
                key_word = read.reference_name.split('|')[0]
                ME_insertion_align[key_word] = ME_family_name

    insertions, deletions = load_cluster(work_dir)
    ME_insertions, ME_deletions = [], []
    for variants, variant_align, records in zip((insertions, deletions), 
                                    (ME_insertion_align, ME_deletion_align),
                                    (ME_insertions, ME_deletions)):
        for variant in variants:
            id_of_variant = variant[0]
            if not id_of_variant in variant_align: continue
            variant.append(variant_align[id_of_variant])
            records.append(variant)

    return ME_insertions, ME_deletions

if __name__ == '__main__':
    print(re_re_alignment('/data/3/zzj/HG002/MEHunterWork', '/data/3/zzj/ME_data/ME.fq'))

