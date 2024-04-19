from typing import *
import time
import os
import logging
import sys
from MEHunter.MEHunter_description import VERSION

def write_to_vcf(insertions : Optional[Any], \
                 deletions  : Optional[Any], \
				 columns_name  : Optional[List], \
                 args, argv):

	logFormat = "%(asctime)s [%(levelname)s] %(message)s"
	logging.basicConfig( stream=sys.stderr, level=logging.ERROR, format=logFormat )
	logging.info("Overwrite to {}".format( args.output ))

	vcf_writer = open(file=args.output, mode='w', encoding='utf-8')
	
	vcf_writer.write("##fileformat=VCFv4.2\n")
	vcf_writer.write("##source=MEHunter-%s\n"%(VERSION))

	vcf_writer.write("##fileDate=%s\n"%(time.strftime('%Y-%m-%d %H:%M:%S %w-%Z',time.localtime())))
	# TODO: Read fastx to get contig information
	# for i in contiginfo:
	# 	vcf_writer.write("##contig=<ID=%s,length=%d>\n"%(i[0], i[1]))

	# Specific header
	# ALT
	vcf_writer.write("##ALT=<ID=MEI,Description=\"Mobile Element Insertion\">\n")
	vcf_writer.write("##ALT=<ID=MED,Description=\"Mobile Element Deletion\">\n")

	# INFO
	vcf_writer.write("##INFO=<ID=MEtype,Number=.,Type=String,Description=\"Name of Mobile Element Family, including Alu, SVA, L1\">\n")
	vcf_writer.write("##INFO=<ID=PRECISE,Number=0,Type=Flag,Description=\"Precise structural variant\">\n")
	vcf_writer.write("##INFO=<ID=IMPRECISE,Number=0,Type=Flag,Description=\"Imprecise structural variant\">\n")
	vcf_writer.write("##INFO=<ID=SVTYPE,Number=1,Type=String,Description=\"Type of structural variant\">\n")
	vcf_writer.write("##INFO=<ID=SVLEN,Number=1,Type=Integer,Description=\"Difference in length between REF and ALT alleles\">\n")
	vcf_writer.write("##INFO=<ID=CHR2,Number=1,Type=String,Description=\"Chromosome for END coordinate in case of a translocation\">\n")
	vcf_writer.write("##INFO=<ID=END,Number=1,Type=Integer,Description=\"End position of the variant described in this record\">\n")
	vcf_writer.write("##INFO=<ID=CIPOS,Number=2,Type=Integer,Description=\"Confidence interval around POS for imprecise variants\">\n")
	vcf_writer.write("##INFO=<ID=CILEN,Number=2,Type=Integer,Description=\"Confidence interval around inserted/deleted material between breakends\">\n")
	vcf_writer.write("##INFO=<ID=RE,Number=1,Type=Integer,Description=\"Number of read support this record\">\n")
	vcf_writer.write("##INFO=<ID=STRAND,Number=A,Type=String,Description=\"Strand orientation of the adjacency in BEDPE format (DEL:+-, DUP:-+, INV:++/--)\">\n")
	vcf_writer.write("##INFO=<ID=RNAMES,Number=.,Type=String,Description=\"Supporting read names of SVs (comma separated)\">\n")
	vcf_writer.write("##INFO=<ID=AF,Number=A,Type=Float,Description=\"Allele Frequency.\">\n")
	vcf_writer.write("##FILTER=<ID=q5,Description=\"Quality below 5\">\n")
	vcf_writer.write("##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">\n")
	vcf_writer.write("##FORMAT=<ID=DR,Number=1,Type=Integer,Description=\"# High-quality reference reads\">\n")
	vcf_writer.write("##FORMAT=<ID=DV,Number=1,Type=Integer,Description=\"# High-quality variant reads\">\n")
	vcf_writer.write("##FORMAT=<ID=PL,Number=G,Type=Integer,Description=\"# Phred-scaled genotype likelihoods rounded to the closest integer\">\n")
	vcf_writer.write("##FORMAT=<ID=GQ,Number=1,Type=Integer,Description=\"# Genotype quality\">\n")

	vcf_writer.write("##CommandLine=\"MEHunter %s\"\n"%(" ".join(argv)))
	
	MEtype_insert_idx = 2
	# columns_name.insert(MEtype_insert_idx, 'MEtype')
	# like #CHROM POS balabalabala
	vcf_writer.write("#{}\n".format("\t".join(columns_name)))

	MEI_paths = [
		os.path.join(args.work_dir, 'High_Quality_MEIs.txt'),
		os.path.join(args.work_dir, 'Potential_MEIs.txt'),
		os.path.join(args.work_dir, 'Partial_MEIs.txt')
	]
	MED_paths = [
		os.path.join(args.work_dir, 'High_Quality_MEDs.txt'),
		os.path.join(args.work_dir, 'Potential_MEDs.txt'),
		os.path.join(args.work_dir, 'Partial_MEDs.txt')
	]
	labels = ['High_Quality', 'Potential', 'Partial']
	for (MEI_path, MED_path, label) in zip(MEI_paths, MED_paths, labels):
		print(MEI_path, MED_path, label)
		ME_insertions = []; ME_deletions = []
		with open(file=MEI_path, mode='r', encoding='utf-8') as reader:
			for line in reader: ME_insertions.append(eval(line.strip()))
		with open(file=MED_path, mode='r', encoding='utf-8') as reader:
			for line in reader: ME_deletions.append(eval(line.strip()))
		
		ins_information = { insertion[0] : insertion[1:] for insertion in ME_insertions }
		del_information = { deletion[0] : deletion[1:] for deletion in ME_deletions }
		del ME_insertions, ME_deletions

		for idx, (variants, information) in enumerate(zip([insertions, deletions],
										[ins_information, del_information])):
			INSERTION_FLAG, DELETION_FLAG = idx == 0, idx == 1	
			for idx_, variant in enumerate(variants):
				variant_id = variant[2]
				if variant_id not in information:
					continue
				# print(information[variant[2]]); print(variant); break
				vcf_writer.write('{}\t'.format(
					'\t'.join([ str(variant[column]) for column in range(MEtype_insert_idx)])
				))
				vcf_writer.write('{}_\"{}\"'.format(
					variant_id, label
				))
				# vcf_writer.write('\"{}\"'.format(
				# 	label + '_' + information[variant_id][-1]
				# ))
				for idx__, column in enumerate(columns_name[MEtype_insert_idx + 1:]):
					idx__ = idx__ + MEtype_insert_idx + 1
					if INSERTION_FLAG and column == 'ALT':
						vcf_writer.write('\t{}'.format(
							information[variant_id][2]
						)); continue
					if DELETION_FLAG and column == 'REF':
						vcf_writer.write('\t{}'.format(
							information[variant_id][2]
						)); continue
					vcf_writer.write('\t{}'.format(variant[idx__]))
				vcf_writer.write('\n')