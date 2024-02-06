import torch
# from rMETL2.Predictor.read_data import read_data
# from rMETL2.Predictor.shuffle_data import shuffle_data
# from rMETL2.Predictor.random_split import random_split
# from rMETL2.Predictor.batch_data import batch_data
# from rMETL2.Predictor.model import ME_Predictor
from MEHunter_seq2img import seq2img_faster
from MEHunter.Classifier import model

if torch.cuda.is_available():
    torch.cuda.set_device(1)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
predictor = model.ME_Predictor()
predictor.load_state_dict(torch.load('/home/zzj/rMETL2/src/rMETL2/Predictor/model.pth'))
predictor.eval()
# predictor = torch.load('src/rMETL2/Predictor/hello_net', map_location=device)

def train():
    global predictor
    epochs = 30
    learning_rate = 1e-5
    batch_size = 201

    datas, labels, label2idx, idx2label = read_data()
    print(label2idx)
    datas, labels = shuffle_data(datas=datas, labels=labels)

    train_datas, train_labels, test_datas, test_labels = random_split(datas=datas, labels=labels, ratio=0.9)

    batched_train_datas, batched_train_labels = batch_data(datas=train_datas, labels=train_labels, batch_size=batch_size)
    batched_test_datas, batched_test_labels = batch_data(datas=test_datas, labels=test_labels, batch_size=batch_size)


    # model = ME_Predictor().to(device)
    # model = torch.load('hello_net2').to(device)

    optimizer = torch.optim.Adam(
        predictor.parameters(),
        lr=learning_rate
    )
    loss_func = torch.nn.CrossEntropyLoss()
    print('start training')
    print(len(batched_train_labels))
    batched_train_datas = [torch.tensor(data=d, dtype=torch.float) for d in batched_train_datas]
    batched_train_labels = [torch.tensor(data=d) for d in batched_train_labels]
    for epoch in range(epochs):

        for i in range(len(batched_train_labels)):
            if len(batched_train_datas[i]) == 0: continue
            img = batched_train_datas[i].to(device)
            labels = batched_train_labels[i].to(device)

            pred = predictor(img)
            loss = loss_func(pred, labels)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if i % 10 == 0:
                print('epoch:{}, iter:{}, loss:{}'.format(epoch, i, loss.item()))
        print('epoch:{}, loss:{}'.format(epoch, loss.item()))

        right = 0
        all_num = 0
        for i in range(len(batched_test_labels)):
            if len(batched_test_datas[i]) == 0: continue
            img = torch.tensor(data=batched_test_datas[i], dtype=torch.float).to(device)
            labels = torch.tensor(data=batched_test_labels[i]).to(device)

            pred = predictor(img)
            pred_ls = [i for val in pred for i, v in enumerate(val) if v == max(val)]

            all_num += len(pred_ls)
            right += sum([1 if pred_ls[i] == labels[i] else 0 for i in range(len(labels))])
        
        img = torch.tensor(data=batched_test_datas[0][:][:10], dtype=torch.float).to(device)
        labels = batched_test_labels[0][:10]
        pred = predictor(img)
        pred_ls = [idx2label[i] for val in pred for i, v in enumerate(val) if v == max(val)]
        real_ls = [idx2label[i] for i in labels]
        print(pred_ls)
        print(real_ls)
        print('epoch:{}, acc:{}'.format(epoch, right / all_num))

    torch.save(predictor, 'hello_net')


def pred_file(read_file_path, output_file_path):
    global predictor
    labels2idx = {'Alu.SVA.': 0, 'L1.': 1, 'Alu.': 2, 'L1.SVA.': 3, 'SVA.': 4, 'L1.Alu.': 5, 'Non': 6}

    idx2label = {
        labels2idx[label] : label
        for label in labels2idx
    }
    pred_ls = []
    seq_ls = []
    with open(file=read_file_path, mode='r', encoding='utf-8') as reader:
        for line in reader:
            seq_ls.append(line.strip().split('\t\t')[-1])
    # print(seq_ls)
    print(len(seq_ls))
    imgs = seq2img_faster(seq_ls=seq_ls)
    batched_imgs, _ = batch_data(datas=imgs, labels=[], batch_size=32)
    for batched_data in batched_imgs:
        print(torch.tensor(batched_data, dtype=torch.float).to(device).shape)
        pred = predictor(torch.tensor(batched_data, dtype=torch.float).to(device))
        print(pred)
        pred_ls.extend([idx2label[i] for val in pred for i, v in enumerate(val) if v == max(val)])
    
    print(pred_ls)
    import re
    Line_rule_pattern = re.compile(r"(A{5,})")

    strand_Line_rule_pattern = re.compile(r"(T{5,})")
    def b2_ratio(seq):
        if len(seq) == 0: return 0
        count = {
            'A' : 0,
            'C' : 0,
            'G' : 0,
            'T' : 0
        }
        for ch in seq: 
            if ch in count: count[ch] += 1
        values = list(count.values())
        values.sort(reverse=True)
        return (values[0] + values[1]) / len(seq)
    is_L1 = []
    for seq in seq_ls:
        flag = len(Line_rule_pattern.findall(seq)) >= 10
        strand_flag = len(strand_Line_rule_pattern.findall(seq)) >= 10
        is_a_TSD = b2_ratio(seq) > 0.95
        if ((flag or strand_flag) and not is_a_TSD):
            is_L1.append(True)
        else: is_L1.append(False)
    print(is_L1)
    return pred_ls


def predict(seq_ls):

    labels2idx = {'SVA.Alu.': 0, 'L1.': 1, 'Alu.': 2, 'SVA.L1.': 3, 'SVA.': 4, 'Alu.L1.': 5, 'Non': 6}
    idx2label = {
        labels2idx[label] : label
        for label in labels2idx
    }
    pred_ls = []
    # imgs = seq2img_faster(seq_ls=seq_ls)
    # print(len(imgs))
    # batched_imgs, _ = batch_data(datas=imgs, labels=[], batch_size=32)
    # print(len(batched_imgs))
    batch_size = 256
    start, end = 0, batch_size
    # for i, batched_data in enumerate(batched_imgs):
    while start < len(seq_ls):
        batched_data = seq2img_faster(seq_ls=seq_ls[start : end])
        start += batch_size
        end += batch_size
        if len(batched_data) == 0: continue
        # print(start, end , batch_size, len(seq_ls), len(batched_data))
        print("DEEP LEARNING Progress: {}/{}".format(start // batch_size, 1 + len(seq_ls) // batch_size))
        # print(torch.tensor(batched_data, dtype=torch.float).to(device).shape)
        pred = predictor(torch.tensor(batched_data, dtype=torch.float).to(device))
        pred = torch.nn.Softmax()(pred)
        pred_ls.extend([(idx2label[i] , [float(a) for a in val]) for val in pred for i, v in enumerate(val) if v == max(val[:7])])
    return pred_ls

# train()
# pred_file(read_file_path='./test.txt', output_file_path=None)
if __name__ == '__main__':
    pred_file(read_file_path='./test.txt', output_file_path=None)