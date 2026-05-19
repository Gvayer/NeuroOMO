import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import LabelEncoder
from sentence_transformers import SentenceTransformer
import joblib
from transformers import pipeline
import os
from threading import Thread, Event
import ExecutingLAB


# ------------------------------
# Загрузка модели классификации команд
# ------------------------------
MODEL_PATH = "command_model.pth"
ENCODER_PATH = "label_encoder.pkl"

if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODER_PATH):
    raise FileNotFoundError("Сначала обучите модель командой NeuroTRAIN.py")

# энкодер меток
le = joblib.load(ENCODER_PATH)

# модель эмбеддингов
embedder = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')  # или DeepPavlov/rubert-base-cased
print("Модель эмбеддингов загружена.")

# архитектура классификатора как при обучении
class CommandClassifier(nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.fc = nn.Linear(input_dim, num_classes)

    def forward(self, x):
        return self.fc(x)

#размерность эмбеддингов
input_dim = embedder.get_sentence_embedding_dimension()
num_classes = len(le.classes_)

model = CommandClassifier(input_dim, num_classes)
# Загружка сохранённых весов
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
model.eval()
print("Модель классификации загружена.")


# ------------------------------
# Функция предсказания команды
# ------------------------------
def predict_command(text, threshold=0.6):
    emb = embedder.encode([text])
    emb_t = torch.tensor(emb, dtype=torch.float32)

    with torch.no_grad():
        logits = model(emb_t)
        probs = torch.softmax(logits, dim=1)
        # Для отладки выводим все вероятности
        max_prob, pred_idx = torch.max(probs, dim=1)
        max_prob = max_prob.item()
        pred_idx = pred_idx.item()

    if max_prob < threshold:
        return None, max_prob
    else:
        command_name = le.inverse_transform([pred_idx])[0]
        return command_name, max_prob


# ------------------------------
# Загрузка NER-модели
# ------------------------------
NER_MODEL_PATH = "./ner_model/final"
if os.path.exists(NER_MODEL_PATH):
    ner_pipeline = pipeline("ner", model=NER_MODEL_PATH, tokenizer=NER_MODEL_PATH, aggregation_strategy="simple")
    print("NER-модель загружена.")
else:
    print("Предупреждение: NER-модель не найдена. Извлечение сущностей отключено.")
    ner_pipeline = None

def extract_entities(text):
    if ner_pipeline is None:
        return {}
    results = ner_pipeline(text)
    entities = {}
    for ent in results:
        entity_type = ent['entity_group']
        word = ent['word']
        if entity_type not in entities:
            entities[entity_type] = word
        else:
            entities[entity_type] += " " + word
    return entities


# ----------------------------------------
# Функция проверки обязательных аргументов
# ----------------------------------------
def required_args_present(command, args):
    required = {
        "turn_on": ["object"],
        "turn_off": ["object"],
        "timer": ["duration_num", "duration_unit"],
        "alarm": ["time"],
        "volume": [],  # можно без аргументов (тогда действие по умолчанию)
        "notes": [],   # можно без текста (тогда, например, создать пустую заметку)
        "search": [],  # допускаю без агрумента, как страховочный круг
        "temperature": [],
        "time": [],
        "humidity": [],
        "sound": [],
        "thanks": [],
        "news": [],
        "token": [],
        "work": [],
        "newyear": [],
        "block": [],
        "telesend": [],
        "raspconnect": [],
        "interface": [],
    }
    req_list = required.get(command, [])
    for arg in req_list:
        if arg not in args or args[arg] is None:
            return False
    return True


# ------------------------------
#     Интерактивный цикл
# ------------------------------

def define_command(user_input):
    command, confidence = predict_command(user_input)
    if command is not None:
        print(f"✅ Распознана команда: '{command}' (уверенность {confidence:.2f})")
        entities = extract_entities(user_input)
        # Преобразует сущности в аргументы для команды
        args = {}
        if command in ["turn_on", "turn_off"]:
            args["object"] = entities.get("OBJECT")
            args["color"] = entities.get("COLOR")
            args["location"] = entities.get("LOCATION")
        elif command == "timer":
            args["duration_num"] = entities.get("DURATION_NUM")
            args["duration_unit"] = entities.get("DURATION_UNIT")
        elif command == "alarm":
            args["time"] = entities.get("TIME")
        elif command == "volume":
            args["value"] = entities.get("VALUE")
            args["direction"] = entities.get("DIRECTION")
        elif command == "notes":
            args["text"] = entities.get("NOTE_TEXT")
        elif command in ["search"]:
            args["query"] = entities.get("QUERY")
        elif command == "temperature":
            args["location"] = entities.get("LOCATION")
        elif command == "notes":
            args["note"] = entities.get("NOTE_TEXT")
        
        if required_args_present(command, args):
            return ExecutingLAB.execute_command(command, args)
        else:
            return "Не хватает параметров. Уточните, пожалуйста."
    else:
        print(f"❌ Уверенность ({confidence:.2f}) — считаем общим вопросом.")
        threadGPT = Thread(target=ExecutingLAB.chatGPT_callback, args = (user_input,))
        threadGPT.start()