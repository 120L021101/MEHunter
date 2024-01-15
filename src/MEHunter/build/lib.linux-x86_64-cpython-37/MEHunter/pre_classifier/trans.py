import torch  
import torch.nn as nn  
from transformers import AutoTokenizer, AutoModel  

model_path = "/home/zzj/MEHunter/src/MEHunter/pre_classifier/model/model"
# 加载tokenizer和预训练模型  
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True, local_files_only=True)  
pretrained_model = AutoModel.from_pretrained(model_path, trust_remote_code=True)  
  
# 定义新的模型类，包括预训练模型和分类头  
class SequenceClassificationModel(nn.Module):  
    def __init__(self, pretrained_model, num_labels):  
        super(SequenceClassificationModel, self).__init__()  
        self.pretrained_model = pretrained_model  
        self.classifier = nn.Linear(self.pretrained_model.config.hidden_size, num_labels)  
  
    def forward(self, input_ids, attention_mask=None):  
        # 获取预训练模型的最后一个隐藏层的输出  
        last_hidden_state = self.pretrained_model(input_ids, attention_mask=attention_mask)[0]  
        # 如果使用的是BERT或类似模型，通常取第一个token（即CLS token）的输出用于分类  
        cls_token = last_hidden_state[:, 0, :]  # 假设CLS token在序列的第一个位置  
        logits = self.classifier(cls_token)  # 通过分类头得到logits  
        return logits  
  
# 实例化新模型，设置分类类别数为2  
num_labels = 2  
model = SequenceClassificationModel(pretrained_model, num_labels)  
  
# 输入序列  
dna = ["ACGTAGCATCGGATCTATCTATCGACACTTGGTTATCGATCTACGAGCATCTCGTTAGC", 'CGTGACTAGCTACTAGC']
inputs = tokenizer(dna, return_tensors='pt', padding=True, truncation=True)  # 添加padding和truncation以处理不同长度的序列  
input_ids = inputs['input_ids']
print(input_ids.shape)  
attention_mask = inputs['attention_mask']  # 如果序列被padding，则忽略padding部分的注意力权重  
# 前向传播，得到分类结果  
logits = model(input_ids, attention_mask=attention_mask)  # [1, num_labels]  
predictions = torch.softmax(logits, dim=-1)  # 应用softmax得到概率分布  
print(predictions)  # 输出每个类别的概率