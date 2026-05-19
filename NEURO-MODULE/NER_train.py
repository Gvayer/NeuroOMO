import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer
from datasets import Dataset
import numpy as np
from seqeval.metrics import classification_report, f1_score

# Загружаем токенизатор
model_name = "DeepPavlov/rubert-base-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Читаем размеченные данные из файла CoNLL
def read_conll(filepath):
    sentences = []
    labels = []
    with open(filepath, 'r', encoding='utf-8') as f:
        words = []
        tags = []
        for line in f:
            line = line.strip()
            if line.startswith('-DOCSTART-'):
                continue
            if line == '':
                if words:
                    sentences.append(words)
                    labels.append(tags)
                    words = []
                    tags = []
            else:
                parts = line.split()
                if len(parts) == 2:
                    word, tag = parts
                    words.append(word)
                    tags.append(tag)
        if words:
            sentences.append(words)
            labels.append(tags)
    return sentences, labels

sentences, labels = read_conll("ner_dataset.txt")

# Получаем уникальные теги
unique_tags = sorted(set(tag for doc in labels for tag in doc))
tag2id = {tag: i for i, tag in enumerate(unique_tags)}
id2tag = {i: tag for tag, i in tag2id.items()}

# Токенизация и выравнивание меток
def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(
        examples["tokens"],
        truncation=True,
        is_split_into_words=True,
        padding="max_length",
        max_length=128,
    )
    labels = []
    for i, label in enumerate(examples["ner_tags"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)  # Игнорируем специальные токены
            elif word_idx != previous_word_idx:
                # Начало нового слова
                label_ids.append(label[word_idx])
            else:
                # Продолжение слова (подслово) - обычно ставим -100 или I-тег
                # Для простоты ставим -100, так как нам важны только первые токены слов
                label_ids.append(-100)
            previous_word_idx = word_idx
        labels.append(label_ids)
    tokenized_inputs["labels"] = labels
    return tokenized_inputs

# Создаем Dataset в формате HuggingFace
data = {"tokens": sentences, "ner_tags": [[tag2id[t] for t in seq] for seq in labels]}
dataset = Dataset.from_dict(data)
dataset = dataset.map(tokenize_and_align_labels, batched=True)

# Разделение на train/valid
dataset = dataset.train_test_split(test_size=0.2)
train_dataset = dataset["train"]
eval_dataset = dataset["test"]

# Загружаем модель
model = AutoModelForTokenClassification.from_pretrained(model_name, num_labels=len(unique_tags))

# Метрики
from seqeval.metrics import accuracy_score, precision_score, recall_score, f1_score

def compute_metrics(p):
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)

    # Убираем игнорируемые токены (-100)
    true_predictions = [
        [id2tag[p] for (p, l) in zip(pred, lab) if l != -100]
        for pred, lab in zip(predictions, labels)
    ]
    true_labels = [
        [id2tag[l] for (p, l) in zip(pred, lab) if l != -100]
        for pred, lab in zip(predictions, labels)
    ]

    return {
        "precision": precision_score(true_labels, true_predictions),
        "recall": recall_score(true_labels, true_predictions),
        "f1": f1_score(true_labels, true_predictions),
        "accuracy": accuracy_score(true_labels, true_predictions),
    }

# Аргументы обучения
# training_args = TrainingArguments(
#     output_dir="./ner_model",
#     eval_strategy="epoch",
#     save_strategy="epoch",
#     learning_rate=2e-5,
#     per_device_train_batch_size=8,
#     per_device_eval_batch_size=8,
#     num_train_epochs=10,
#     weight_decay=0.01,
#     logging_dir="./logs",
#     load_best_model_at_end=True,
#     metric_for_best_model="f1",
# )
training_args = TrainingArguments(
    output_dir="./ner_model",
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=3e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=20,
    weight_decay=0.01,
    logging_dir="./logs",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,
    save_total_limit=2,
    logging_strategy="epoch",
    report_to="none",
    warmup_ratio=0.1,  # полезно для стабильности
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
    # tokenizer убран — он не нужен, т.к. данные уже предобработаны
)

trainer.train()

model.config.id2label = id2tag
model.config.label2id = tag2id

# Сохраняем модель и токенизатор
model.save_pretrained("./ner_model/final")
tokenizer.save_pretrained("./ner_model/final")