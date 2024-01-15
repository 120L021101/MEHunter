import pandas as pd
from typing import *
import time
import os
import logging
import sys

def write_to_vcf(ME_insertions : Optional[pd.DataFrame], \
                 ME_deletions  : Optional[pd.DataFrame], \
				 columns_name  : Optional[List], \
                 args, argv):
	VERSION = '1.0.0' # this variable is previously declared in MEIHunter_description, meaning the version of this software
	logFormat = "%(asctime)s [%(levelname)s] %(message)s"
	if os.path.exists(args.output):
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

	vcf_writer.write("##CommandLine=\"cuteSV %s\"\n"%(" ".join(argv)))
	
	# like #CHROM POS balabalabala
	vcf_writer.write("#{}\n".format("\t".join(columns_name)))

	vcf_writer.close()
