import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

##
# class ComplaintClassifier:
#     def __init__(self):
#         local_model_path = "../../models/fine_tuned_complaint_classifier" # Adjust path
#         self.tokenizer = AutoTokenizer.from_pretrained(local_model_path)
#         self.model = AutoModelForSequenceClassification.from_pretrained(local_model_path)

#         self.classifier = pipeline(
#             "text-classification", # Or "zero-shot-classification" 
#             model=self.model,
#             tokenizer=self.tokenizer,
#             return_all_scores=True,
#             device=0 if torch.cuda.is_available() else -1
#         )
#         # Define labels 
#         self.labels = ["Water", "Electricity", "Sanitation", "Roads", "Traffic", "Encroachment", "Animal Control"]
##

nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text) 
    words = text.split()
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return ' '.join(words)

class ComplaintClassifier:
    def __init__(self, model_name="distilbert-base-uncased"):

        self.classifier = pipeline(
            "zero-shot-classification",
            model=model_name, 
            tokenizer=model_name, 
            device=0 if torch.cuda.is_available() else -1 
        )
        self.labels = ["Water", "Electricity", "Sanitation", "Roads", "Traffic", "Encroachment", "Animal Control"]

    def classify_complaint(self, text):
        preprocessed_text = preprocess_text(text)
        # The zero-shot-classification pipeline expects the text and candidate_labels
        results = self.classifier(preprocessed_text, candidate_labels=self.labels, multi_label=False) # multi_label=False for single best category

        if results and results['labels'] and results['scores']:
            # The zero-shot pipeline returns a dictionary with 'labels' and 'scores' lists
            # The first label in 'labels' is the highest scoring one by default
            top_label = results['labels'][0]
            top_score = results['scores'][0]
            return top_label, top_score
        return "Unknown", 0.0

    def extract_location(self, text):
        location_keywords = ["ward", "sector", "road", "park", "area", "complex", "street", "intersection", "neighborhood", "city", "town", "hospital", "school", "market"]
        text_lower = text.lower()
        found_locations = []
        for keyword in location_keywords:
            if keyword in text_lower:
                match = re.search(r'\b(\w+\s+){0,2}' + re.escape(keyword) + r'(\s+\w+){0,2}\b', text_lower)
                if match:
                    found_locations.append(match.group(0).strip())
        if found_locations:
            return ", ".join(list(set(found_locations)))
        return "Unknown Location"

if __name__ == "__main__":
    classifier = ComplaintClassifier()
    sample_complaint = "There is a huge pothole on the main road near the market area, causing severe traffic congestion."
    category, score = classifier.classify_complaint(sample_complaint)
    location = classifier.extract_location(sample_complaint)
    print(f"Complaint: {sample_complaint}")
    print(f"Predicted Category: {category} (Score: {score:.2f})")
    print(f"Extracted Location: {location}")

    sample_complaint_2 = "Power outage in the hospital area since last night. This is critical."
    category_2, score_2 = classifier.classify_complaint(sample_complaint_2)
    location_2 = classifier.extract_location(sample_complaint_2)
    print(f"\nComplaint: {sample_complaint_2}")
    print(f"Predicted Category: {category_2} (Score: {score_2:.2f})")
    print(f"Extracted Location: {location_2}")
