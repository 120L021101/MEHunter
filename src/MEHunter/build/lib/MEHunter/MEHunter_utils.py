import pandas as pd
import os
import argparse
import logging
import sys
import time
import gc 
import pandas as pd  

def read_vcf(vcf_path):
    '''
    guarantee the safety of requesting the vcf file, e.g. existence
    '''
    column_names, insertions, deletions = None, None, None
    with open(file=vcf_path, mode='r', encoding='utf-8') as vcf_reader:

        for line in vcf_reader:
            if line.startswith('##'):
                # just a comment, skip it
                continue
            if line.startswith('#'):
                # header, record the column names
                column_names = line[1:].strip().split('\t')
                insertions = { column_name : [] for column_name in column_names }
                deletions = { column_name : [] for column_name in column_names }
                continue
            # detailed info about variants
            variant_info = line.strip().split('\t')
            variant_info = [ int(info) if info.isdigit() else info for info in variant_info ]

            is_INS, is_DEL = 'INS' in variant_info[2], 'DEL' in variant_info[2]
            for col, info in enumerate( variant_info ):
                if is_INS: insertions[column_names[col]].append(info)
                if is_DEL: deletions[column_names[col]].append(info)
        vcf_reader.close()
    # TODO: analyse cuteSV output and distinguish insertions and deletions from the result.
    insertions, deletions = pd.DataFrame(insertions), pd.DataFrame(deletions)
    return insertions, deletions, column_names