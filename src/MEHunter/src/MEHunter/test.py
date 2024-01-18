import sys
import torch  
from transformers import AutoTokenizer, AutoModel  
from model import SequenceClassificationModel, BinaryClassifier
import os
os.environ['TOKENIZERS_PARALLELISM'] = 'FALSE' 
MAX_INPUT_SIZE = 1000
def clipping_data(batch_data):
    global MAX_INPUT_SIZE
    clipped_data = []; index_ls = []
    start = 0; end = 0
    for idx, data in enumerate(batch_data):
        s = 0; e = MAX_INPUT_SIZE
        while s < len(data):
            clipped_data.append(data[s : e])
            end += 1; s += MAX_INPUT_SIZE; e += MAX_INPUT_SIZE
        index_ls.append((start, end))
        start = end
    return clipped_data, index_ls

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")   

model_path = "/home/zzj/MEHunter/src/MEHunter/pre_classifier/model/model"
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)  
pretrained_model = AutoModel.from_pretrained(model_path, trust_remote_code=True)  

model_path = "/home/zzj/MEHunter/src/MEHunter/pre_classifier/model/model.pth"
classifier = BinaryClassifier(768)
classifier.load_state_dict(torch.load(model_path, map_location=device))

model = SequenceClassificationModel(tokenizer, pretrained_model, classifier, device)  
model = model.to(device)   

print(
    model(['ACGTGACTAGCAAAAAAAAAA']).shape
)
