from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset

# ... (load and preprocess your custom dataset) ...
# df = pd.read_csv("your_complaints_dataset.csv")
# train_texts, val_texts, train_labels, val_labels = train_test_split(...)

# Load base model and tokenizer
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=len(your_categories))

# ... (define your dataset class and collator) ...

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
)

# Create Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=your_train_dataset,
    eval_dataset=your_val_dataset,
    tokenizer=tokenizer,
    # compute_metrics=compute_metrics, # if have a custom metric function
)

# Train the model
trainer.train()

output_model_dir = "./models/fine_tuned_complaint_classifier"
model.save_pretrained(output_model_dir)
tokenizer.save_pretrained(output_model_dir)

print(f"Fine-tuned model saved to {output_model_dir}")
