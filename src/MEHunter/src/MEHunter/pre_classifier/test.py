import torch


a = torch.tensor([[1, 2], [3, 4]], dtype=torch.float, requires_grad=True)
a = a * 2
print(a)
with torch.no_grad():
    a = a * 2
a = a + 1
print(a)