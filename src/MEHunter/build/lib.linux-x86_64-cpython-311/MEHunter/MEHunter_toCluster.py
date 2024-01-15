import pandas as pd
import pysam
from typing import *
import logging
import sys
import os
import pyfastx
import pyabpoa as pa

logFormat = "%(asctime)s [%(levelname)s] %(message)s"

def consensus_abPOA(sequences : Optional[List]) -> Optional[AnyStr]:
    '''
    using abPOA to calculate consensus of sequences and return it.
    '''
    a = pa.msa_aligner()
    res=a.msa(sequences, out_cons=True, out_msa=True) # perform multiple sequence alignment 
    for seq in res.cons_seq:
        return seq # return the first result
    return ''

def extract_supporting_signatures(variant  : Optional[List], \
                                  sigs     : Optional[Dict], \
                                  position : Optional[Tuple]) -> Optional[List]:
    extract_sigs = { } 
    (chromosome, index) = position
    support_reads = variant['INFO']
    for read_name in sigs:
        if read_name not in support_reads: continue
        for (_, _, pos, _, read_name, seq) in sigs[read_name]:
            if read_name not in extract_sigs:
                extract_sigs[read_name] = (pos, seq)
            else:
                (its_pos, its_seq) = extract_sigs[read_name]
                if abs(its_pos - index) > abs(pos - index):
                    extract_sigs[read_name] = (pos, seq)
    return [ extract_sigs[key][1] for key in extract_sigs ]    

def sigs2cluster(insertions : Optional[pd.DataFrame], \
                 deletions  : Optional[pd.DataFrame], \
				 args):
    '''
    this procedure produces 'ins.cluster' and 'del.cluster' in MEHunter's workdir
    '''  
    bam_file = pysam.AlignmentFile(args.alignment, "rb")  

    for flag, variants in enumerate([insertions, deletions]):
        INSERTION_FLAG, DELETION_FLAG = flag == 0, flag == 1
        logging.basicConfig( stream=sys.stderr, level=logging.INFO, format=logFormat )
        logging.info("Start extracting and clustering {} signals".format(
            "insertion" if INSERTION_FLAG else "deletion"
        ))
        sig_path = os.path.join( args.cuteSV_workdir, 'INS.sigs' ) if INSERTION_FLAG \
                else os.path.join( args.cuteSV_workdir, 'DEL.sigs' )
        
        if not os.path.isdir(args.cuteSV_workdir):
            logging.basicConfig( stream=sys.stderr, level=logging.ERROR, format=logFormat )
            logging.error("No Such File: {}, have you kept workdir of cuteSV? if not, add --retain_work_dir".format(sig_path))
            exit()

        cluster_path = os.path.join( args.work_dir, 'ins.cluster' ) if INSERTION_FLAG \
                else os.path.join( args.work_dir, 'del.cluster' )

        if DELETION_FLAG:
            # open fastx to get variant sequence of DEL
            reference_genome = pyfastx.Fasta(args.reference, build_index = True)

        with open(file=sig_path, mode='r', encoding='utf-8') as sig_reader:
            sigs = {  } # read_name -> [ sig1, sig2 ..... ]
            for line in sig_reader:
                info_ls = line.strip().split('\t')
                if INSERTION_FLAG:
                    if len(info_ls) != 6: continue
                    info_ls = [ int(info) if info.isdigit() else info for info in info_ls ]
                if DELETION_FLAG:
                    info_ls = [ int(info) if info.isdigit() else info for info in info_ls ]
                    info_ls.append(
                        reference_genome[str(info_ls[1])][(info_ls[2]) : (info_ls[2] + info_ls[3])]
                    )
                read_name = info_ls[4]; chromosome = str(info_ls[1])
                if chromosome not in sigs: sigs[chromosome] = { }

                if read_name not in sigs[chromosome]: sigs[chromosome][read_name] = [info_ls]
                else: sigs[chromosome][read_name].append(info_ls)

            Solved_chromomosome = set()
            with open(file=cluster_path, mode='w', encoding='utf-8') as cluster_writer:
                for index, variant in variants.iterrows():
                    chromosome, pos, this_id = str(variant['CHROM']), variant['POS'], variant['ID']
                    supporting_reads = variant['FORMAT'].split('RNAMES=')[1].split('AF=')[0].split('#####')
                    print(supporting_reads)
                    if chromosome not in Solved_chromomosome:
                        Solved_chromomosome.add(chromosome)
                        logging.basicConfig( stream=sys.stderr, level=logging.INFO, format=logFormat )
                        logging.info("Solving Chromosome {}".format(chromosome))
                    if chromosome not in sigs: continue
                    seqs = extract_supporting_signatures( 
                        variant, sigs[chromosome], ( chromosome, pos )
                    )
                    abortion_flag = False
                    for seq in seqs:
                        if len(seq) > 15000: 
                            abortion_flag = True
                            break
                    if abortion_flag: continue
                    # abPOA的算法对长度的内存开销是非线性的
                    # 序列太长的话，内存会爆掉，这个没办法try except，只能根据经验限制
                    # 家丑不可外扬，就不用英格力士了

                    consensus = consensus_abPOA( seqs )
                    cluster_writer.write(
                        "{}\n".format("\t".join(
                            [ this_id, chromosome, str(pos), consensus, str(len(seqs)) ] # information items list
                        ))
                    )
    bam_file.close()