import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import os

print("--- Starting Sentiment Analysis Pipeline ---")

# 1. Load Dataset
data_path = 'dataset 1/glassdoor_reviews.csv'
if not os.path.exists(data_path):
    print(f"Error: {data_path} not found.")
    exit(1)

print("Loading data (reading 50,000 rows for memory efficiency)...")
df = pd.read_csv(data_path, usecols=['overall_rating', 'pros', 'cons'], nrows=50000)
df.dropna(subset=['overall_rating'], inplace=True)

# 2. Data Preprocessing
print("Preprocessing textual data...")
# Combine pros and cons, map ratings >= 4 to Positive (1), else Negative (0)
df['text'] = df['pros'].fillna('') + " " + df['cons'].fillna('')
df['sentiment'] = df['overall_rating'].apply(lambda x: 1 if x >= 4 else 0)
df = df[df['text'].str.strip() != '']

print(f"Total valid records: {len(df)}")
X_train, X_test, y_train, y_test = train_test_split(df['text'], df['sentiment'], test_size=0.2, random_state=42)

# 3. Model Training
print("Training Logistic Regression Model with TF-IDF...")
vectorizer = TfidfVectorizer(stop_words='english', max_features=10000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

model = LogisticRegression(max_iter=1000)
model.fit(X_train_vec, y_train)

print("\nModel Evaluation:")
predictions = model.predict(X_test_vec)
print(classification_report(y_test, predictions, target_names=["Negative", "Positive"]))

# 4. Extracting Areas for Improvement
print("\n--- Identifying Areas for Improvement ---")
feature_names = np.array(vectorizer.get_feature_names_out())
coefs = model.coef_[0]

# Sort to find strongest predictors for class 0 (Negative)
sorted_coef_idx = coefs.argsort()
top_negative_words = feature_names[sorted_coef_idx[:30]]

print(f"Top keywords mentioned in negative feedback (Areas to Improve):")
print(', '.join(top_negative_words))
print("\nThese keywords highlight the primary issues reducing satisfaction.")

print("\n--- Saving Models for API ---")
joblib.dump(model, 'model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')
print("Saved model.pkl and vectorizer.pkl successfully!")
