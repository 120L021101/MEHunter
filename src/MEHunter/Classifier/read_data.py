import torch
# from PIL import Image
import numpy
import matplotlib.pyplot as plt
from MEHunter.Classifier.fake_data import create_fake_data
from MEHunter.Classifier.seq2img import seq2img_faster
transforms = {
    'A' : 0,
    'C' : 1,
    'G' : 2,
    'T' : 3,
    'N' : 4
}

def read_data(size = 256, data_path = 'Predictor/short_fact.embl', transforms = transforms):

    datas = []
    labels = []
    short_datas = []
    with open(file=data_path, mode='r', encoding='utf-8') as data_reader:

        Alu, SVA, L1 = False, False, False

        label = None

        while True:
            line = data_reader.readline()
            if not line: break

            if line.startswith('KW'):
                    # ME_info_ls.append(line)
                label = line.strip().split('   ')[1].split('; ')[-1].split('/')[1]

            if line.startswith('SQ'):
                seq_ls = []
                while True:
                    
                    line = data_reader.readline()
                    if line.startswith('/'):
                        seq = ''.join(seq_ls)
                        break
                    seq_ls.append(''.join(line.strip().split(' ')[:-1]).upper())

                short_datas.append(seq)
                
                labels.append(label) 

                if 'Alu' in label:
                    for i in range(6):
                        short_datas.append(seq)
                        labels.append(label) 
                if 'SVA' in label:
                    for i in range(200):
                        short_datas.append(seq)                    
                        labels.append(label)  

        data_reader.close()
    
    # print(short_datas[0])
    create_fake_data(datas=short_datas, labels=labels)
    label_count = {

    }
    for label in labels:
        label_count[label] = label_count.get(label, 0) + 1
    print(label_count)
    # exit()
    datas = seq2img_faster(short_datas)
    labels2idx = {'Alu.SVA.': 0, 'L1.': 1, 'Alu.': 2, 'L1.SVA.': 3, 'SVA.': 4, 'L1.Alu.': 5, 'Non': 6}
    idx2label = {
        labels2idx[label] : label
        for label in labels2idx
    }
    labels = [labels2idx[l] for l in labels]
    
    sample_pic = set()
    for i, label in enumerate(labels):
        if label not in sample_pic:
            sample_pic.add(label)
            plt.imshow(numpy.array(datas[i][0]), cmap='gray')
            plt.savefig("./{}.png".format(idx2label[label]))
            print("print{}".format(idx2label[label]))
    return datas, labels, labels2idx, idx2label

if __name__ == '__main__':
    import os
    datas, labels, label2idx, idx2label = read_data()
    print(idx2label)
    labels_sample = {}
    for i in range(len(datas)):
        
        img = datas[i][0]
        label = idx2label[labels[i]]
        if label in labels_sample and labels_sample[label] >= 21:
            labels_sample[label] += 1
            continue
        if label not in labels_sample:
            labels_sample[label] = 1
            cmd = "mkdir {}".format(label)
            os.system(cmd)
        plt.imshow(numpy.array(img), cmap='gray')
        plt.savefig("./{}/{}.png".format(label, labels_sample[label]))
        labels_sample[label] += 1
    print(labels_sample)