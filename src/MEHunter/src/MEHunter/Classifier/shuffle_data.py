import random
def shuffle_data(datas, labels):
    idx_ls = list(range(len(datas)))
    random.shuffle(idx_ls)
    datas = [datas[i] for i in idx_ls]
    labels = [labels[i] for i in idx_ls]
    return datas, labels