import argparse
import sys
import torch  
import torch.nn as nn  

class SequenceClassificationModel(nn.Module):  
    def __init__(self, tokenizer, pretrained_model, classifier, device):  
        super(SequenceClassificationModel, self).__init__()  
        self.tokenizer = tokenizer
        self.pretrained_model = pretrained_model  
        self.classifier = classifier
        self.device = device
 
    def forward(self, input_ids):
        inputs = self.tokenizer(input_ids, return_tensors='pt', padding=True, truncation=True)  # 添加padding和truncation以处理不同长度的序列  
        input_ids = inputs['input_ids'].to(self.device)  
        attention_mask = inputs['attention_mask'].to(self.device)
        last_hidden_state = self.pretrained_model(input_ids, attention_mask=attention_mask)[0]  
        cls_token = last_hidden_state[:, 0, :]
        return cls_token
        
        logits = self.classifier(cls_token)   
        
        return logits  

class BinaryClassifier(nn.Module):  
    def __init__(self, input_dim):  
        super(BinaryClassifier, self).__init__()  
        self.fc1 = nn.Linear(input_dim, 256)  
        self.relu = nn.ReLU()  
        self.fc2 = nn.Linear(256, 64)  
        self.fc3 = nn.Linear(64, 2)  
          
    def forward(self, x):  
        x = self.fc1(x)  
        x = self.relu(x)  
        x = self.fc2(x)  
        x = self.relu(x)  
        x = self.fc3(x)  
        return x 
