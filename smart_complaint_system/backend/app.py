from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from datetime import datetime
import os

from nlp_model import ComplaintClassifier
from urgency_scorer import UrgencyScorer

app = Flask(__name__)
CORS(app)

# Initialize models
classifier = ComplaintClassifier()
scorer = UrgencyScorer()

# Database
COMPLAINTS_FILE = 'data/complaints.csv'

def load_complaints():
    if os.path.exists(COMPLAINTS_FILE):
        df = pd.read_csv(COMPLAINTS_FILE)
        # Ensure numerical columns are standard Python types for JSON serialization
        if 'complaint_id' in df.columns:
            df['complaint_id'] = df['complaint_id'].astype(int)
        if 'urgency_score' in df.columns:
            df['urgency_score'] = df['urgency_score'].astype(int)
        return df
    return pd.DataFrame(columns=['complaint_id', 'description', 'category', 'severity', 'location', 'urgency_score', 'date', 'resolution_status'])

def save_complaints(df):
    df.to_csv(COMPLAINTS_FILE, index=False)

@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    data = request.json
    description = data.get('description')
    location_input = data.get('location')

    if not description:
        return jsonify({"error": "Complaint description is required"}), 400

    # 1. Content Analysis with NLP
    predicted_category, _ = classifier.classify_complaint(description)
    extracted_location = classifier.extract_location(description)

    # Use user-provided location if available, otherwise extracted
    final_location = location_input if location_input else extracted_location

    # 2. Urgency Scoring
    urgency_score = scorer.score_complaint(predicted_category, "N/A", final_location, description)

    # Generate unique complaint ID
    complaints_df = load_complaints()
    new_id = complaints_df['complaint_id'].max() + 1 if not complaints_df.empty else 1001

    new_complaint = {
        'complaint_id': int(new_id),
        'description': description,
        'category': predicted_category,
        'severity': scorer.get_severity_level(predicted_category, description),
        'location': final_location,
        'urgency_score': int(urgency_score),
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'resolution_status': 'Pending'
    }

    new_complaints_df = pd.concat([complaints_df, pd.DataFrame([new_complaint])], ignore_index=True)
    save_complaints(new_complaints_df)

    return jsonify({
        "message": "Complaint submitted successfully",
        "complaint_details": new_complaint
    }), 201

@app.route('/get_complaints', methods=['GET'])
def get_complaints():
    complaints_df = load_complaints()
    complaints_df_sorted = complaints_df.sort_values(by='urgency_score', ascending=False)
    return jsonify(complaints_df_sorted.to_dict(orient='records'))

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(COMPLAINTS_FILE):
        save_complaints(pd.DataFrame(columns=['complaint_id', 'description', 'category', 'severity', 'location', 'urgency_score', 'date', 'resolution_status']))

    app.run(debug=True, host='0.0.0.0', port=5000)
