import random

decoder = {
    0 : 'A',
    1 : 'C',
    2 : 'G',
    3 : 'T'
}

def create_short_seq():
    ch_ls = [random.randint(0, 3) for i in range(random.randint(0, 20))]
    return ch_ls

def create_fake_seq():
    ch_ls = [random.randint(0, 3) for i in range(random.randint(30, 50))]
    return ch_ls

def create_non():
    ch_ls = [random.randint(0, 3) for i in range(random.randint(200, 2000))]
    return ch_ls

def create_fake_data(datas, labels):

    labels_ls = ['L1.', 'Alu.', 'SVA.']
    label2data = {

    }
    for i in range(len(labels)):
        if labels[i] not in label2data:
            label2data[labels[i]] = []
        label2data[labels[i]].append(datas[i])
    # for key in label2data:
    #     print("{} : {}".format(key, len(label2data[key])))
    data_size = len(labels)
    sample_size = data_size // 3

    for i in range(len(labels_ls) - 1):
        for j in range(i + 1, len(labels_ls)):
            # print(i, j)
            label1 = labels_ls[i]
            label2 = labels_ls[j]
            combine_label = label1 + label2
            for k in range(sample_size):
                idx1 = random.randint(0, len(label2data[label1]) - 1)
                idx2 = random.randint(0, len(label2data[label2]) - 1)
                combine_data = []
                combine_data.extend(label2data[label1][idx1])
                combine_data.extend(create_short_seq())
                combine_data.extend(label2data[label2][idx2])
                combine_data.extend(create_short_seq())
                # combine_data = [label2data[label1][idx1], create_short_seq(), label2data[label2][idx2], create_short_seq()]
                datas.append(combine_data)
                labels.append(combine_label)
    
    # print('-------------------------')
    # label2data = {

    # }
    # for i in range(len(labels)):
    #     if labels[i] not in label2data:
    #         label2data[labels[i]] = []
    #     label2data[labels[i]].append(datas[i])
    # for key in label2data:
    #     print("{} : {}".format(key, len(label2data[key])))
    # print('-------------------------')

    for i in range(len(labels_ls)):
        label = labels_ls[i]
        for k in range(sample_size // 3):
            idx1 = random.randint(0, len(label2data[label]) - 1)
            idx2 = random.randint(0, len(label2data[label]) - 1)
            combine_data = []
            combine_data.extend(label2data[label][idx1])
            combine_data.extend(create_short_seq())
            combine_data.extend(label2data[label][idx2])
            combine_data.extend(create_short_seq())
            # combine_data = [label2data[label][idx1] , create_short_seq() , label2data[label][idx2] , create_short_seq()]
            datas.append(combine_data)
            labels.append(label)

    # labels_ls = ['Alu.SVA.', 'L1.Alu.', 'Alu.', 'SVA.', 'L1.SVA.', 'L1.']
    # label2data = {

    # }
    # for i in range(len(labels)):
    #     if labels[i] not in label2data:
    #         label2data[labels[i]] = []
    #     label2data[labels[i]].append(datas[i])
    
    # for label in label2data:
    #     for data in label2data[label]:
    #         fake_data = []
    #         fake_data.extend(create_short_seq())
    #         fake_data.extend(data)
    #         fake_data.extend(create_short_seq())

    #         # fake_data = [create_short_seq() , data , create_fake_seq()]
    #         datas.append(fake_data)
    #         labels.append(label)
    
    sample_size = data_size // 3
    for i in range(sample_size):
        datas.append(create_non())
        labels.append('Non')

    # print('-------------------------')
    # label2data = {

    # }
    # for i in range(len(labels)):
    #     if labels[i] not in label2data:
    #         label2data[labels[i]] = []
    #     label2data[labels[i]].append(datas[i])
    # for key in label2data:
    #     print("{} : {}".format(key, len(label2data[key])))
    # print('-------------------------')