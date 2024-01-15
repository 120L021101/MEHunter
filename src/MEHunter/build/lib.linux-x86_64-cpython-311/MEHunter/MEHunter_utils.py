import pandas as pd
import os
import argparse
import logging
import sys
import time
import gc
import subprocess
import pandas as pd  

def is_empty(file_path):
    with open(file=file_path, mode='r', encoding='utf-8') as try_file:
        ret_value = not try_file.readline()
    return ret_value

def function_wrapper(function, *args):
    import sys, io, os
    stdout_buffer = io.StringIO(); stderr_buffer = io.StringIO()
    stdout_old = sys.stdout; stderr_old = sys.stderr
    sys.stdout = stdout_buffer; sys.stderr = stderr_buffer
    ret_vals = function(*args)
    sys.stdout = stdout_old; sys.stderr = stderr_old
    stdout_buffer.close(); stderr_buffer.close()
    return ret_vals

def kill_output():
    import sys, io, os
    stdout_buffer = io.StringIO(); stderr_buffer = io.StringIO()
    stdout_old = sys.stdout; stderr_old = sys.stderr
    sys.stdout = stdout_buffer; sys.stderr = stderr_buffer
    return (stdout_old, stderr_old, stdout_buffer, stderr_buffer)

def activate_output(args):
    import sys
    (stdout_old, stderr_old, stdout_buffer, stderr_buffer) = args
    stdout_buffer.close(); stderr_buffer.close()
    sys.stdout = stdout_old; sys.stderr = stderr_old

def call(cmd):
    import sys, io, os
    cmd += ' 2> {}'.format(os.devnull)
    subprocess.call(cmd, shell=True)

def clear_workdir(args):
    path_ = os.path.join(args.work_dir, '*')
    cmd = 'rm -rf {}'.format(path_)
    call(cmd=cmd)

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
    insertions = insertions.head(200); deletions = deletions.head(200)
    return insertions, deletions, column_names
