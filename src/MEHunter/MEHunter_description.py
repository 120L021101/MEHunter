''' 
 * All rights Reserved, Designed By HIT-Bioinformatics   
 * @Title:  MEHunter_description.py
 * @author: Zuji Zhou
 * @date: Dec 12th 2023
 * @version V1.0.0
'''
import argparse

VERSION = '1.0.0'

class MEHunterdp(object):
	'''
	Detailed descriptions of MEHunter version and its parameters.
	'''

	USAGE="""\
		
	Current version: v%s
	Author: Zuji Zhou
	Contact: hitzzj@outlook.com

	If you use MEHunter in your work, please cite:
		Zuji Zhou et al. MeHunter: Long-read based mobile element variant detection through deep learning and modified Smith-Waterman algorithm

	"""%(VERSION)

	# MinSizeDel = 'For current version of MEHunter, it can detect deletions larger than this size.'

def parseArgs(argv):
	parser = argparse.ArgumentParser(prog="MEHunter", 
		description=MEHunterdp.USAGE, 
		formatter_class=argparse.RawDescriptionHelpFormatter)

	parser.add_argument('--version', '-v', 
		action = 'version', 
		version = '%(prog)s {version}'.format(version=VERSION))

	# **************Parameters of input******************
	parser.add_argument("input", 
		metavar="[VCF]", 
		type = str, 
		help = "vcf format file, also cuteSV's output")
	parser.add_argument("alignment", 
		metavar="[BAM]", 
		type = str, 
		help = "bam format file, maybe minimap2's output")
	parser.add_argument("cuteSV_workdir",
		type=str,
		help = "cuteSV workdir, note that add --retain_work_dir while running cuteSV, MEHunter needs its sigs files"
    )
	parser.add_argument("reference",  
		type = str, 
		help ="The reference genome in fasta format.")
	parser.add_argument("known_ME",
		type = str,
		help = "known ME dataset, fq format"				 
	)
	parser.add_argument('work_dir', 
		type = str, 
		help = "Work-directory for distributed jobs")
	parser.add_argument('output', 
		type = str, 
		help = "Output VCF format file.")
	parser.add_argument('--DL_module',
		help='dir of DNABERT',
		type=str,
		default='/home/zzj/MEHunter/src/MEHunter/pre_classifier/model/')
	# ************** Other Parameters******************
	parser.add_argument('-t', '--threads', 
		help = "Number of threads to use.[%(default)s]", 
		default = 8, 
		type = int)
	
	parser.add_argument('--retain_work_dir',
		help = "Enable to retain temporary folder and files.",
		default=False,
		action='store_true'
	)

	parser.add_argument('--batch_size',
		help = "size of batch, for deep learning",
		type = int,
		default = 16
	)

	parser.add_argument('--MAX_seqs',
		help = "max seq num for consensus",
		type = int,
		default = 20
	)

	parser.add_argument('--MIN_Consensus_length',
		help = "min length of Consensus",
		type = int,
		default = 100
	)

	
	# GroupSignaturesCollect = parser.add_argument_group('Collection of SV signatures')
	# GroupSignaturesCollect.add_argument('-p', '--max_split_parts', 
	# 	help = "Maximum number of split segments a read may be aligned before it is ignored. All split segments are considered when using -1. \
	# 		(Recommand -1 when applying assembly-based alignment.)[%(default)s]", 
	# 	default = 7, 
	# 	type = int)

	args = parser.parse_args(argv)
	return args

def Generation_VCF_header(file, contiginfo, sample, argv):
	# General header
	file.write("##fileformat=VCFv4.2\n")
	file.write("##source=MEHunter-%s\n"%(VERSION))
	import time
	file.write("##fileDate=%s\n"%(time.strftime('%Y-%m-%d %H:%M:%S %w-%Z',time.localtime())))
	for i in contiginfo:
		file.write("##contig=<ID=%s,length=%d>\n"%(i[0], i[1]))

	# Specific header
	# ALT
	file.write("##ALT=<ID=INS,Description=\"Insertion of novel sequence relative to the reference\">\n")
	file.write("##ALT=<ID=DEL,Description=\"Deletion relative to the reference\">\n")
	file.write("##ALT=<ID=DUP,Description=\"Region of elevated copy number relative to the reference\">\n")
	file.write("##ALT=<ID=INV,Description=\"Inversion of reference sequence\">\n")
	file.write("##ALT=<ID=BND,Description=\"Breakend of translocation\">\n")

	# INFO
	file.write("##INFO=<ID=PRECISE,Number=0,Type=Flag,Description=\"Precise structural variant\">\n")
	file.write("##INFO=<ID=IMPRECISE,Number=0,Type=Flag,Description=\"Imprecise structural variant\">\n")
	file.write("##INFO=<ID=SVTYPE,Number=1,Type=String,Description=\"Type of structural variant\">\n")
	file.write("##INFO=<ID=SVLEN,Number=1,Type=Integer,Description=\"Difference in length between REF and ALT alleles\">\n")
	file.write("##INFO=<ID=CHR2,Number=1,Type=String,Description=\"Chromosome for END coordinate in case of a translocation\">\n")
	file.write("##INFO=<ID=END,Number=1,Type=Integer,Description=\"End position of the variant described in this record\">\n")
	file.write("##INFO=<ID=CIPOS,Number=2,Type=Integer,Description=\"Confidence interval around POS for imprecise variants\">\n")
	file.write("##INFO=<ID=CILEN,Number=2,Type=Integer,Description=\"Confidence interval around inserted/deleted material between breakends\">\n")
	# file.write("##INFO=<ID=MATEID,Number=.,Type=String,Description=\"ID of mate breakends\">\n")
	file.write("##INFO=<ID=RE,Number=1,Type=Integer,Description=\"Number of read support this record\">\n")
	file.write("##INFO=<ID=STRAND,Number=A,Type=String,Description=\"Strand orientation of the adjacency in BEDPE format (DEL:+-, DUP:-+, INV:++/--)\">\n")
	file.write("##INFO=<ID=RNAMES,Number=.,Type=String,Description=\"Supporting read names of SVs (comma separated)\">\n")
	file.write("##INFO=<ID=AF,Number=A,Type=Float,Description=\"Allele Frequency.\">\n")
	file.write("##FILTER=<ID=q5,Description=\"Quality below 5\">\n")
	# FORMAT
	# file.write("\n")
	file.write("##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">\n")
	file.write("##FORMAT=<ID=DR,Number=1,Type=Integer,Description=\"# High-quality reference reads\">\n")
	file.write("##FORMAT=<ID=DV,Number=1,Type=Integer,Description=\"# High-quality variant reads\">\n")
	file.write("##FORMAT=<ID=PL,Number=G,Type=Integer,Description=\"# Phred-scaled genotype likelihoods rounded to the closest integer\">\n")
	file.write("##FORMAT=<ID=GQ,Number=1,Type=Integer,Description=\"# Genotype quality\">\n")

	file.write("##CommandLine=\"MEHunter %s\"\n"%(" ".join(argv)))
