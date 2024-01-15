def batch_data(datas, labels, batch_size):

    batched_datas = []
    batched_labels = []
    start = 0
    end = batch_size
    
    while end <= len(datas):
        batched_datas.append(datas[start : end])
        batched_labels.append(labels[start : end])

        start += batch_size
        end += batch_size
    
    if end > len(datas):
        batched_datas.append(datas[start : ])
        batched_labels.append(labels[start : ])
    
    return batched_datas, batched_labels