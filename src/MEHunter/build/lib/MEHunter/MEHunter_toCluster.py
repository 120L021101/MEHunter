import pandas as pd
import pysam
from typing import *
import logging
import sys
import os
import pyfastx

logFormat = "%(asctime)s [%(levelname)s] %(message)s"

def consensus_abPOA(sequences : Optional[List]) -> Optional[AnyStr]:
    '''
    using abPOA to calculate consensus of sequences and return it.
    '''
    import pyabpoa as pa
    a = pa.msa_aligner()
    res=a.msa(sequences, out_cons=True, out_msa=True) # perform multiple sequence alignment 
    for seq in res.cons_seq:
        return seq # return the first result
    return ''

def sigs2cluster(insertions : Optional[pd.DataFrame], \
                 deletions  : Optional[pd.DataFrame], \
				 args):
    '''
    this procedure produces 'ins.cluster' and 'del.cluster' in MEHunter's workdir
    '''  
    bam_file = pysam.AlignmentFile(args.alignment, "rb")  

    for flag, variants in enumerate([insertions, deletions]):
        INSERTION_FLAG, DELETION_FLAG = flag == 0, flag == 1

        sig_path = os.path.join( args.cuteSV_workdir, 'INS.sigs' ) if INSERTION_FLAG \
                else os.path.join( args.cuteSV_workdir, 'DEL.sigs' )
        
        if not os.path.isfile(args.reference):
            logging.basicConfig( stream=sys.stderr, level=logging.ERROR, format=logFormat )
            logging.error("No Such File: {}, have you kept workdir of cuteSV? if not, add --retain_work_dir".format(sig_path))
            exit()

        cluster_path = os.path.join( args.work_dir, 'ins.cluster' ) if INSERTION_FLAG \
                else os.path.join( args.work_dir, 'del.cluster' )

        if DELETION_FLAG:
            # open fastx to get variant sequence of DEL
            reference_genome = pyfastx.Fasta(args.reference, build_index = True)

        with open(file=sig_path, mode='r', encoding='utf-8') as sig_reader:
            sigs = []
            for line in sig_reader:
                info_ls = line.strip().split('\t')
                if INSERTION_FLAG:
                    if len(info_ls) != 6: continue
                    info_ls = [ int(info) if info.isdigit() else info for info in info_ls ]
                if DELETION_FLAG:
                    info_ls = [ int(info) if info.isdigit() else info for info in info_ls ]
                    info_ls.append(
                        reference_genome[info_ls[1]][(info_ls[2]) : (info_ls[2] + info_ls[3])]
                    )
                sigs.append(info_ls)

            with open(file=cluster_path, mode='w', encoding='utf-8') as cluster_writer:
                for index, variant in variants.iterrows():
                    chromosome, start_position = str(variant['CHROM']), variant['POS']
                    end_position = start_position + 1
                    reads = bam_file.fetch(chromosome, start_position, end_position)  
                    names = { read.query_name for read in reads}

                    # TODO: windows algorithm, performance need to be optimized 
                    start, end, best_record, best_length = 0, 0, (0, 0), 0
                    length_of_sigs = len(sigs)
                    while end <= length_of_sigs:
                        if end == length_of_sigs or (str(sigs[end][1]) != chromosome and best_length != 0):
                            if (end - start) > best_length:
                                best_record = (start, end)
                                best_length = end - start
                            break
                        if sigs[end][4] not in names:
                            if (end - start) > best_length:
                                best_record = (start, end)
                                best_length = end - start
                            (start, end) = (end + 1, end + 1); continue
                        end = end + 1
                    
                    # fail to find supporting reads, in fact I guess it may be a bug.
                    if best_length == 0: continue

                    seqs = [ sigs[i][5] for i in range(best_record[0], best_record[1]) ]
                    consensus = consensus_abPOA( seqs )
                    cluster_writer.write(
                        "{}\n".format("\t".join(
                            [ chromosome, str(start_position), consensus ] # information items list
                        ))
                    )
    bam_file.close()