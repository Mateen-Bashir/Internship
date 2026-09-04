from flask import Flask, request, jsonify, send_from_directory
import joblib
from transformers import pipeline
import os

app = Flask(__name__)

# Load local ML Model globally
print("Loading Logistic Regression Model...")
try:
    log_model = joblib.load('model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
except Exception as e:
    print("Warning: Log model not found. Ensure sentiment_analysis.py ran successfully. Error:", e)

print("Transformer pipeline will be loaded on demand.")
# Prevent transformers warnings
import warnings
warnings.filterwarnings("ignore")
sentiment_analyzer = None

def get_sentiment_analyzer():
    global sentiment_analyzer
    if sentiment_analyzer is None:
        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=-1
        )
    return sentiment_analyzer

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

def extract_dynamic_insights(text, sentiment):
    text = text.lower()
    insight_map = {
        "bullying": ("Workplace Bullying", "Address toxic behavior urgently.", "Negative"),
        "toxic": ("Toxic Culture", "Investigate team dynamics and overall intern culture.", "Negative"),
        "unprofessional": ("Unprofessionalism", "Enforce stricter professional standards among mentors.", "Negative"),
        "underpaid": ("Compensation Constraints", "Review intern stipends and ensure competitive/fair pay.", "Negative"),
        "pay": ("Compensation Constraints", "Review intern stipends and ensure competitive/fair pay.", "Negative"),
        "management": ("Leadership Concerns", "Mentions of management behavior or oversight.", "Both"),
        "manager": ("Leadership Concerns", "Mentions of management behavior or oversight.", "Both"),
        "overworked": ("Work-Life Balance", "Ensure interns have reasonable hours and workloads.", "Negative"),
        "hours": ("Work-Life Balance", "Monitor daily working hours of interns.", "Both"),
        "disorganized": ("Process Structure", "Improve the structure and clarity of onboarding or tasks.", "Negative"),
        "confusing": ("Process Structure", "Tasks or processes lack clear documentation.", "Negative"),
        "turnover": ("Retention Risk", "Address the reasons causing interns to want to leave.", "Negative"),
        "promises": ("Mismatched Expectations", "Ensure internship descriptions match actual duties.", "Negative"),
        "support": ("Strong Support", "Interns feel well-supported by their teams.", "Positive"),
        "learning": ("Valuable Learning", "Internship provides great educational value.", "Positive"),
        "friendly": ("Positive Culture", "The team environment is welcoming and healthy.", "Positive"),
        "culture": ("Culture Mentioned", "Feedback touches heavily on company culture.", "Both"),
        "great": ("Positive Atmosphere", "General high satisfaction with the experience.", "Positive")
    }
    
    found = []
    for word, (title, desc, polarity) in insight_map.items():
        if word in text:
            if polarity in ["Both", sentiment]:
                if not any(r['title'] == title for r in found):
                    found.append({"title": title, "desc": desc, "keyword": word})
                    
    return found

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    text = data.get('text', '')
    model_type = data.get('model', 'logistic') # 'logistic' or 'transformer'
    
    if not text.strip():
        return jsonify({"error": "No text provided"}), 400
        
    if model_type == 'logistic':
        try:
            vec_text = vectorizer.transform([text])
            pred = log_model.predict(vec_text)[0]
            sentiment = "Positive" if pred == 1 else "Negative"
            return jsonify({
                "sentiment": sentiment, 
                "model": "Logistic Regression",
                "insights": extract_dynamic_insights(text, sentiment)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif model_type == 'transformer':
        try:
            sentiment_model = get_sentiment_analyzer()
            # Truncating length to avoid 512 token error
            trunc_text = str(text)[:400]
            result = sentiment_model([trunc_text])[0]
            sentiment = "Positive" if result['label'] == 'POSITIVE' else "Negative"
            score = round(result['score'] * 100, 2)
            return jsonify({
                "sentiment": sentiment, 
                "model": f"DistilBERT ({score}% confidence)",
                "insights": extract_dynamic_insights(text, sentiment)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/insights', methods=['GET'])
def get_insights():
    try:
        import numpy as np
        feature_names = np.array(vectorizer.get_feature_names_out())
        coefs = log_model.coef_[0]
        sorted_coef_idx = coefs.argsort()
        top_words = feature_names[sorted_coef_idx[:20]].tolist()
        
        insight_map = {
            "bullying": ("Workplace Bullying", "Address toxic behavior urgently to ensure a safe environment."),
            "toxic": ("Toxic Culture", "Investigate team dynamics and overall intern culture."),
            "unprofessional": ("Unprofessionalism", "Enforce stricter professional standards among mentors/staff."),
            "underpaid": ("Compensation Constraints", "Review intern stipends and ensure competitive/fair pay."),
            "management": ("Leadership Gaps", "Provide better coaching and oversight training for managers."),
            "overworked": ("Work-Life Balance", "Ensure interns have reasonable hours and manageable workloads."),
            "disorganized": ("Process Structure", "Improve the structure and clarity of onboarding or daily tasks."),
            "turnover": ("Retention Risk", "Address the reasons causing interns or staff to want to leave early."),
            "promises": ("Mismatched Expectations", "Ensure internship descriptions accurately match actual daily duties.")
        }
        
        results = []
        # First pass: known heavy issues
        for word in top_words:
            if word in insight_map:
                title, desc = insight_map[word]
                # Avoid duplicates
                if not any(r['title'] == title for r in results):
                    results.append({"title": title, "desc": desc, "keyword": word})
            
        # Second pass: generic mapping for other top issues
        for word in top_words:
            if len(results) >= 5:
                break
            if word not in insight_map and len(word) > 4:
                # Exclude purely subjective/unhelpful adjectives if possible without NLTK, just simplistic check
                if word not in ['horrible', 'terrible', 'awful', 'worst', 'poor']:
                    results.append({"title": f"Concerns regarding '{word.capitalize()}'", "desc": "Frequent negative feedback involves this topic.", "keyword": word})

        return jsonify({"insights": results[:5]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
            
if __name__ == '__main__':
    print("\nStarting App! Go to http://127.0.0.1:5000 in your browser.")
    # Disabled debug=True to prevent PyTorch and Flask Watchdog from crashing on Windows
    app.run(debug=False, port=5000)
