import random

def random_split(datas, labels, ratio):
    train_datas = []
    train_labels = []
    test_datas = []
    test_labels = []

    for i in range(len(datas)):
        flag = random.random()
        if flag <= ratio:
            train_datas.append(datas[i])
            train_labels.append(labels[i])
        else:
            test_datas.append(datas[i])
            test_labels.append(labels[i])
    
    return train_datas, train_labels, test_datas, test_labels