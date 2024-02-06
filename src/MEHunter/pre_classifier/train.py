import torch  
import torch.nn as nn  
from torch.optim import Adam  
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset  
from transformers import AutoTokenizer, AutoModel  
from sklearn.model_selection import train_test_split  
from torch.utils.data import Dataset  
from model import BinaryClassifier, SequenceClassificationModel

MAX_INPUT_SIZE = 1000

class CustomDataset(Dataset):  
    def __init__(self, data, targets, transform=None):  
        self.data = data  
        self.targets = targets  
        self.transform = transform  
  
    def __len__(self):  
        return len(self.data)  
  
    def __getitem__(self, idx):  
        sample = self.data[idx]  
        label = self.targets[idx]  
        if self.transform:  
            sample = self.transform(sample)  
        return sample, label

model_path = "/home/zzj/MEHunter/src/MEHunter/pre_classifier/model/model"
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True, local_files_only=True)  
pretrained_model = AutoModel.from_pretrained(model_path, trust_remote_code=True)  
model_path = "/home/zzj/MEHunter/src/MEHunter/pre_classifier/model/model.pth"
classifier = BinaryClassifier(768)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")   
model = SequenceClassificationModel(tokenizer, pretrained_model, classifier, device)  
model = model.to(device)   


datas, labels = [], []
with open(file='trained_model/datas.txt', mode='r', encoding='utf-8') as data_loader:
    for line in data_loader:
        info_ls = line.strip().split('\t')
        seq = info_ls[0]; label = int(info_ls[1])
        start = 0; end = MAX_INPUT_SIZE
        while start < len(seq):
            datas.append(seq[start : end])
            labels.append(label)
            start += MAX_INPUT_SIZE; end += MAX_INPUT_SIZE

print(datas[:3], labels[:3])

optimizer = Adam(model.parameters(), lr=1e-5)   
criterion = nn.CrossEntropyLoss()  


train_inputs, validation_inputs, train_labels, validation_labels = train_test_split(datas, labels, test_size=0.2)  
  
train_dataset = CustomDataset(train_inputs, train_labels)  
train_dataloader = DataLoader(train_dataset, sampler=RandomSampler(train_dataset), batch_size=2)  
  
validation_dataset = CustomDataset(validation_inputs, validation_labels)  
validation_dataloader = DataLoader(validation_dataset, sampler=SequentialSampler(validation_dataset), batch_size=2)  

  
epochs = 5   
for epoch in range(epochs):  
    model.train()   
    total_loss = 0.0   
    for batch in train_dataloader:   
        # batch = tuple(t.to(device) for t in batch)   
        data, labels = batch
        data = list(data)  
        optimizer.zero_grad()   
        outputs = model(data)   
        labels = torch.tensor( labels, dtype=torch.long ).to(device)    
        loss = criterion(outputs, labels)   
        total_loss += loss.item()   
        loss.backward()   
        optimizer.step()   
    avg_loss = total_loss / len(train_dataloader)   
    print(f"Epoch {epoch+1} - Training Loss: {avg_loss:.4f}")   
      
    model.eval()   
    total_eval_loss = 0.0   
    total_eval_accuracy = 0.0   
    with torch.no_grad():   
        for batch in validation_dataloader:   
            batch = tuple(t.to(device) for t in batch)   
            data, labels = batch   
            outputs = model(data)   
            loss = criterion(outputs, labels)   
            total_eval_loss += loss.item()   
            preds = torch.argmax(outputs, dim=1)   
            accuracy = (preds == labels).float().mean()   
            total_eval_accuracy += accuracy.item() * len(labels)   
    avg_eval_loss = total_eval_loss / len(validation_dataloader)   
    avg_eval_accuracy = total_eval_accuracy / len(validation_inputs)   
    print(f"Epoch {epoch+1} - Validation Loss: {avg_eval_loss:.4f}, Validation Accuracy: {avg_eval_accuracy:.4f}")   