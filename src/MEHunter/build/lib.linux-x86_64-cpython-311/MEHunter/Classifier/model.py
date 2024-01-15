import torch
from torch import nn

class ME_Predictor(nn.Module):

    def __init__(self) -> None:
        super(ME_Predictor, self).__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_channels=2, out_channels=16, kernel_size=(3, 3), stride=(1, 1), padding=1),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(16, 32, 3, 1, 1),
            nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(131072, 512),
            nn.ReLU(),
            nn.Linear(512,10)
        )
    
    def forward(self, x):
        return self.net(x)

if __name__ == '__main__':
    data0 = torch.zeros((64, 2, 256, 256))
    model = ME_Predictor()
    print(model(data0))