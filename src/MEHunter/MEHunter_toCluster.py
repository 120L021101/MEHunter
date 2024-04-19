from typing import *
import logging
import sys
import os
import pyfastx
import pyabpoa as pa
from multiprocessing import Process
from MEHunter.MEHunter_utils import call

def find_similar_seqs(seqs, MAX_seqs = 20):
    if len(seqs) <= MAX_seqs: return seqs
    avg_length = sum([len(seq) for seq in seqs]) / len(seqs)
    ls_ = [((abs(len(seq)) - avg_length, idx), idx) for idx, seq in enumerate(seqs)]
    ls_.sort(key=lambda x : x[0])
    return [ seqs[idx] for (dis, idx) in ls_[:MAX_seqs] ]

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

def extract_sigs_with_reads(sigs : Optional[Dict], \
                            info : Optional[Tuple]):
    (chromosome, index, supporting_reads) = info
    sig_seqs = []
    for read_name in supporting_reads:
        closest_distance = None; closest_idx = None
        if read_name not in sigs: 
            continue
            assert False
        for idx, (_, _, pos, _, r_name, seq) in enumerate(sigs[read_name]):
            pos = int(pos); index = int(index)
            current_distance = abs(pos - index)
            if (closest_distance is None) or current_distance < closest_distance:
                closest_distance = current_distance
                closest_idx = idx
        if closest_idx is not None:
            sig_seqs.append(sigs[read_name][closest_idx][-1])
        else:
            assert False
    return sig_seqs

def extract_supporting_signatures(variant  : Optional[List], \
                                  sigs     : Optional[Dict], \
                                  position : Optional[Tuple]) -> Optional[List]:
    extract_sigs = { } 
    (chromosome, index) = position
    support_reads = variant['INFO']
    for read_name in sigs:
        if read_name not in support_reads: 
            # print(read_name, support_reads)
            assert False
        for (_, _, pos, _, read_name, seq) in sigs[read_name]:
            if read_name not in extract_sigs:
                extract_sigs[read_name] = (pos, seq)
            else:
                (its_pos, its_seq) = extract_sigs[read_name]
                if abs(its_pos - index) > abs(pos - index):
                    extract_sigs[read_name] = (pos, seq)
    return [ extract_sigs[key][1] for key in extract_sigs ]    

def process_func(*args):
    args, sigs, cluster_writer, variants = args
    Solved_chromomosome = set()
    for index, variant in enumerate(variants):
        chromosome, pos, this_id = str(variant[0]), variant[1], variant[2]
        supporting_reads = variant[-3].split('RNAMES=')[1].split(';AF=')[0].split('#####')
        if chromosome not in Solved_chromomosome:
            Solved_chromomosome.add(chromosome)
            # logging.basicConfig( stream=sys.stderr, level=logging.INFO, format=logFormat )
            # logging.info("Solving Chromosome {}".format(chromosome))
        if chromosome not in sigs: continue
        seqs = extract_sigs_with_reads(
            sigs[chromosome], ( chromosome, pos, supporting_reads )
        )
        abortion_flag = False
        for seq in seqs:
            if len(seq) > 10000: 
                abortion_flag = True
                break
        if abortion_flag: continue
        consensus = consensus_abPOA( find_similar_seqs(seqs, args.MAX_seqs) )
        cluster_writer.write(
            "{}\n".format("\t".join(
                [ this_id, chromosome, str(pos), consensus, str(len(seqs)) ] # information items list
            ))
        ); cluster_writer.flush()

def sigs2cluster(insertions : Optional[pd.DataFrame], \
                 deletions  : Optional[pd.DataFrame], \
				 args):
    '''
    this procedure produces 'ins.cluster' and 'del.cluster' in MEHunter's workdir
    '''  
    for flag, variants in enumerate([insertions, deletions]):
        INSERTION_FLAG, DELETION_FLAG = flag == 0, flag == 1
        logging.basicConfig( stream=sys.stderr, level=logging.INFO, format=logFormat )
        logging.info("Start extracting and clustering {} signals".format(
            "insertion" if INSERTION_FLAG else "deletion"
        ))        
        if not os.path.isdir(args.cuteSV_workdir):
            logging.basicConfig( stream=sys.stderr, level=logging.ERROR, format=logFormat )
            logging.error("No Such File: {}, have you kept workdir of cuteSV? if not, add --retain_work_dir".format(args.cuteSV_workdir))
            exit()

        sig_path = os.path.join( args.cuteSV_workdir, 'INS.sigs' ) if INSERTION_FLAG \
            else os.path.join( args.cuteSV_workdir, 'DEL.sigs' )
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
                        str(reference_genome[str(info_ls[1])][(info_ls[2]) : (info_ls[2] + info_ls[3])])
                    )
                read_name = info_ls[4]; chromosome = str(info_ls[1])
                if chromosome not in sigs: sigs[chromosome] = { }

                if read_name not in sigs[chromosome]: sigs[chromosome][read_name] = [info_ls]
                else: sigs[chromosome][read_name].append(info_ls)

            process_cluster_writers = []; process_variants = []; process_ls = []

            for i in range(args.threads):
                process_writer_path = os.path.join( args.work_dir, 'ins{}.cluster'.format(i + 1) ) if INSERTION_FLAG \
                    else os.path.join( args.work_dir, 'del{}.cluster'.format(i + 1) )
                process_cluster_writers.append(
                    open(file=process_writer_path, mode='w', encoding='utf-8')
                )
                process_variants.append([])
            
            pick_idx = 0
            for variant in variants:
                process_variants[pick_idx].append(variant)
                pick_idx = (pick_idx + 1) % args.threads

            for i in range(args.threads):
                process_ls.append(Process(target=process_func, 
                                        args=(args, sigs, process_cluster_writers[i], process_variants[i])))
                process_ls[-1].start()
            for i in range(args.threads):
                process_ls[i].join()
                process_cluster_writers[i].close()

            cluster_path = os.path.join( args.work_dir, 'ins.cluster' ) if INSERTION_FLAG \
                    else os.path.join( args.work_dir, 'del.cluster' )

            with open(file=cluster_path, mode='w', encoding='utf-8') as cluster_writer:
                for i in range(args.threads):
                    sub_cluster_path = os.path.join( args.work_dir, 'ins{}.cluster'.format(i + 1) ) if INSERTION_FLAG \
                        else os.path.join( args.work_dir, 'del{}.cluster'.format(i + 1) )
                    with open(file=sub_cluster_path, mode='r', encoding='utf-8') as sub_cluster_reader:
                        for line in sub_cluster_reader:
                            cluster_writer.write(line); cluster_writer.flush()
                    call("rm {}".format(sub_cluster_path))