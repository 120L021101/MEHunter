a = [1, 2, 3]
b = [1, 2, 2]

print(sum([1 if a[i] == b[i] else 0 for i in range(len(a))]))

import torch
arr = torch.tensor([
    [1, 2, 3],
    [3, 2, 1],
    [2, 3, 1]
])
pred_ls = [
    i for val in arr for i, v in enumerate(val) if v == max(val) 
]
print(pred_ls)