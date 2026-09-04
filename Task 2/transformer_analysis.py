import pandas as pd
from sklearn.metrics import classification_report
import os
import sys
import warnings

# Suppress some common HF warnings
warnings.filterwarnings("ignore")

try:
    from transformers import pipeline
except ImportError:
    print("Error: transformers library is not installed. Please try again after installing.")
    sys.exit(1)

print("--- Starting Advanced Sentiment Analysis with DistilBERT ---")

data_path = 'dataset 1/glassdoor_reviews.csv'
if not os.path.exists(data_path):
    print(f"Error: {data_path} not found.")
    sys.exit(1)

# Because Transformers are extremely computationally heavy for a CPU, 
# we sample a much smaller dataset (500-1000 rows) so it doesn't take hours to run locally.
print("Loading data (Sampling 1,000 records for fast CPU inference)...")
df = pd.read_csv(data_path, usecols=['overall_rating', 'pros', 'cons'], nrows=5000)
df.dropna(subset=['overall_rating'], inplace=True)
df['text'] = df['pros'].fillna('') + " " + df['cons'].fillna('')
df['true_sentiment'] = df['overall_rating'].apply(lambda x: 1 if x >= 4 else 0)
df = df[df['text'].str.strip() != '']
df = df.sample(n=1000, random_state=42)

print("\nInitializing DistilBERT pipeline (Downloading weights if first time)...")
# Using device=-1 to guarantee CPU usage
sentiment_analyzer = pipeline(
    "sentiment-analysis", 
    model="distilbert-base-uncased-finetuned-sst-2-english", 
    device=-1
)

texts = df['text'].tolist()
# Truncating length to avoid 512-token max limitations for HF Transformers
truncated_texts = [str(t)[:400] for t in texts]

print("\nRunning inference... (Evaluating each review)")
results = sentiment_analyzer(truncated_texts)

# Map HF positive/negative labels to 1 and 0
predicted = []
for result in results:
    if result['label'] == 'POSITIVE':
        predicted.append(1)
    else:
        predicted.append(0)

print("\n--- DistilBERT Model Evaluation ---")
print(classification_report(df['true_sentiment'], predicted, target_names=["Negative", "Positive"]))
print("Note: The evaluation ran strictly on the laptop's CPU.")
