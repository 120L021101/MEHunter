import sys
import torch  
from transformers import AutoTokenizer, AutoModel  
from MEHunter.pre_classifier.model import SequenceClassificationModel, BinaryClassifier
from MEHunter.MEHunter_utils import function_wrapper
import logging
import os
os.environ['TOKENIZERS_PARALLELISM'] = 'FALSE' 
MAX_INPUT_SIZE = 1000
def clipping_data(batch_data):
    global MAX_INPUT_SIZE
    clipped_data = []; index_ls = []
    start = 0; end = 0
    for idx, data in enumerate(batch_data):
        s = 0; e = MAX_INPUT_SIZE
        while s < len(data):
            clipped_data.append(data[s : e])
            end += 1; s += MAX_INPUT_SIZE; e += MAX_INPUT_SIZE
        index_ls.append((start, end))
        start = end
    return clipped_data, index_ls

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")   
model = None

def load_module(args):
    global device, model
    model_path = args.DL_module
    pretrained_model_path = os.path.join(model_path, 'model')
    print(model_path)
    tokenizer = AutoTokenizer.from_pretrained(pretrained_model_path, trust_remote_code=True)  
    pretrained_model = AutoModel.from_pretrained(pretrained_model_path, trust_remote_code=True)  
    model_path = os.path.join(args.DL_module, 'model.pth')
    classifier = BinaryClassifier(768)
    classifier.load_state_dict(torch.load(model_path, map_location=device))

    model = SequenceClassificationModel(tokenizer, pretrained_model, classifier, device)  
    model = model.to(device)  

def infer(args):
    logFormat = "%(asctime)s [%(levelname)s] %(message)s"
    candidate_ME_readers = [
        open(file=os.path.join(args.work_dir, 'Candidate_MEIs.txt'), mode='r', encoding='utf-8'),
        open(file=os.path.join(args.work_dir, 'Candidate_MEDs.txt'), mode='r', encoding='utf-8')
    ]

    success_writers = [
        open(file=os.path.join(args.work_dir, 'Potential_MEIs.txt'), mode='w', encoding='utf-8'),
        open(file=os.path.join(args.work_dir, 'Potential_MEDs.txt'), mode='w', encoding='utf-8')
    ]

    failed_writers = [
        open(file=os.path.join(args.work_dir, 'Partial_MEIs.txt'), mode='w', encoding='utf-8'),
        open(file=os.path.join(args.work_dir, 'Partial_MEDs.txt'), mode='w', encoding='utf-8')
    ]

    for idx, (reader, writer, f_writer) in enumerate(zip(candidate_ME_readers, success_writers, failed_writers)):
        INSERTION_FLAG, DELETION_FLAG = idx == 0, idx == 1
        logging.basicConfig( stream=sys.stderr, level=logging.INFO, format=logFormat )
        logging.info("inferring {} clusters".format(
            "insertion" if INSERTION_FLAG else "deletion"
        ))
        batch_data = []; data = []; current_read = 0
        while True:
            line = reader.readline(); current_read += 1
            if current_read % 100 == 0:
                logging.basicConfig( stream=sys.stderr, level=logging.INFO, format=logFormat )
                logging.info("Sovled {} clusters".format(current_read))
            if not line or args.batch_size == len(batch_data):
                if len(batch_data) == 0: break
                clipped_batch_data, index_ls = clipping_data( batch_data )
                clipped_outputs = function_wrapper(model, clipped_batch_data)
                _, labels = torch.max( clipped_outputs, dim = 1 ); labels = labels.tolist()
                labels = [ 1 if sum(labels[ s : e ]) > 0 else 0 for (s, e) in index_ls]
                for idx, label in enumerate(labels):
                    if label == 1: # means an ME
                        writer.write(data[idx])
                        writer.flush()
                    else:
                        f_writer.write(data[idx])
                        f_writer.flush()
                if not line: break
                batch_data = []; data = []
            info_ls = eval(line.strip())
            data.append(line)
            batch_data.append(info_ls[3])

    
    candidate_ME_readers[0].close(); candidate_ME_readers[1].close()
    success_writers[0].close(); success_writers[1].close()
    failed_writers[0].close(); failed_writers[1].close()

def infer2(work_dir, batch_size):
    global model
    cluster_readers = [
        open(file=os.path.join(work_dir, 'failed_ins.cluster'), mode='r', encoding='utf-8'),
        open(file=os.path.join(work_dir, 'failed_del.cluster'), mode='r', encoding='utf-8')
    ]

    success_writers = [
        open(file=os.path.join(work_dir, 'dl_ins.fq'), mode='w', encoding='utf-8'),
        open(file=os.path.join(work_dir, 'dl_del.fq'), mode='w', encoding='utf-8')
    ]

    for (reader, writer) in zip(cluster_readers, success_writers):
        batch_data = []; data = []; current_read = 0
        while True:
            line = reader.readline(); current_read += 1
            if current_read % 100 == 0:
                print("READ {} clusters".format(current_read))
            if not line or batch_size == len(batch_data):
                clipped_batch_data, index_ls = clipping_data( batch_data )
                clipped_outputs = model(clipped_batch_data)
                _, labels = torch.max( clipped_outputs, dim = 1 ); labels = labels.tolist()
                labels = [ 1 if sum(labels[ s : e ]) > 0.5 * (e - s) else 0 for  (s, e) in index_ls]
                for idx, label in enumerate(labels):
                    if label == 1: # means an ME
                        writer.write(">{}|{}|{}\n".format(
                            data[idx][0], data[idx][1], data[idx][2]
                        ))
                        start = 0; end = 50
                        while start <= len(batch_data[idx]):
                            writer.write("{}\n".format(batch_data[idx][start : end]))
                            start += 50; end += 50
                if not line: break
                batch_data = []; data = []
            info_ls = line.strip().split('\t')
            data.append(info_ls)
            batch_data.append(info_ls[3])

    
    cluster_readers[0].close(); cluster_readers[1].close()
    success_writers[0].close(); success_writers[1].close()
    exit()


if __name__ == '__main__':
    # infer2('/data/3/zzj/HG002/MEHunterWork', 16)
    pass