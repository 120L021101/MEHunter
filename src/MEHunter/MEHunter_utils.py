import os
import logging
import sys
import subprocess

def is_empty(file_path):
    with open(file=file_path, mode='r', encoding='utf-8') as try_file:
        ret_value = not try_file.readline()
    return ret_value

def function_wrapper(function, *args):
    import sys, io
    stdout_buffer = io.StringIO(); stderr_buffer = io.StringIO()
    stdout_old = sys.stdout; stderr_old = sys.stderr
    sys.stdout = stdout_buffer; sys.stderr = stderr_buffer
    ret_vals = function(*args)
    sys.stdout = stdout_old; sys.stderr = stderr_old
    stdout_buffer.close(); stderr_buffer.close()
    return ret_vals

def kill_output():
    import sys, io
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
    import os
    cmd += ' 2> {}'.format(os.devnull)
    subprocess.call(cmd, shell=True)

def clear_workdir(args):
    path_ = os.path.join(args.work_dir, '*')
    cmd = 'rm -rf {}'.format(path_)
    call(cmd=cmd)

def cluster2fasta(args):
    logFormat = "%(asctime)s [%(levelname)s] %(message)s"
    cluster_readers = [
        open(file=os.path.join(args.work_dir, 'failed_ins.cluster'), mode='r', encoding='utf-8'),
        open(file=os.path.join(args.work_dir, 'failed_del.cluster'), mode='r', encoding='utf-8')
    ]

    success_writers = [
        open(file=os.path.join(args.work_dir, 'minimap2_ins.fq'), mode='w', encoding='utf-8'),
        open(file=os.path.join(args.work_dir, 'minimap2_del.fq'), mode='w', encoding='utf-8')
    ]

    for idx, (reader, writer) in enumerate(zip(cluster_readers, success_writers)):
        INSERTION_FLAG, DELETION_FLAG = idx == 0, idx == 1
        logging.basicConfig( stream=sys.stderr, level=logging.INFO, format=logFormat )
        logging.info("inferring {} clusters".format(
            "insertion" if INSERTION_FLAG else "deletion"
        ))
        for line in reader:
            info_ls = line.strip().split('\t')
            writer.write(">{}|{}|{}\n".format(
                info_ls[0], info_ls[1], info_ls[2]
            ))
            start = 0; end = 50
            while start < len(info_ls[3]):
                writer.write("{}\n".format(info_ls[3][start : end]))
                start += 50; end += 50
        continue

    cluster_readers[0].close(); cluster_readers[1].close()
    success_writers[0].close(); success_writers[1].close()

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
                insertions = []; deletions = []
                continue
            # detailed info about variants
            variant_info = line.strip().split('\t')
            variant_info = [ int(info) if info.isdigit() else info for info in variant_info ]

            is_INS, is_DEL = 'INS' in variant_info[2], 'DEL' in variant_info[2]
            if is_INS: insertions.append(variant_info)
            if is_DEL: deletions.append(variant_info)
            continue

            for col, info in enumerate( variant_info ):
                if is_INS: insertions[column_names[col]].append(info)
                if is_DEL: deletions[column_names[col]].append(info)
        vcf_reader.close()
    
    # TODO: analyse cuteSV output and distinguish insertions and deletions from the result.
    
    # insertions = insertions[:1000]; deletions = deletions[:1000]
    # insertions, deletions = pd.DataFrame(insertions), pd.DataFrame(deletions)
    # insertions = insertions.head(200); deletions = deletions.head(200)
    return insertions, deletions, column_names
