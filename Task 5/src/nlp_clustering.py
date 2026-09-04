"""
NLP Vectorization (TF-IDF) and Clustering (K-Means) Engine.
Clusters industry job descriptions into distinct demand domains and extracts
characteristic skill signatures.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

try:
    from src.preprocessor import clean_text
except ImportError:
    from preprocessor import clean_text

class IndustrySkillClusterModel:
    def __init__(self, n_clusters=6, max_features=600):
        self.n_clusters = n_clusters
        self.max_features = max_features
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            init="k-means++",
            n_init=15,
            max_iter=300,
            random_state=42
        )
        self.pca = PCA(n_components=2, random_state=42)
        self.feature_names = []
        self.cluster_labels_map = {}
        self.cluster_top_terms = {}
        self.is_fitted = False

    def fit(self, jobs_df: pd.DataFrame):
        """Preprocesses job descriptions, fits TF-IDF, and fits K-Means model."""
        # Combine job description and required skills for rich representation
        combined_texts = jobs_df.apply(
            lambda r: f"{r['job_title']} {r['required_skills']} {r['job_description']}", axis=1
        )
        cleaned_corpus = [clean_text(t) for t in combined_texts]
        
        # 1. TF-IDF Vectorization
        self.tfidf_matrix = self.vectorizer.fit_transform(cleaned_corpus)
        self.feature_names = np.array(self.vectorizer.get_feature_names_out())
        
        # 2. K-Means Clustering
        self.cluster_assignments = self.kmeans.fit_predict(self.tfidf_matrix)
        
        # 3. Silhouette Score
        self.silhouette_avg = silhouette_score(self.tfidf_matrix, self.cluster_assignments)
        
        # 4. Extract Top Terms per Cluster & Auto-Label
        self._extract_cluster_profiles(jobs_df)
        
        # 5. Fit PCA for 2D visualization
        self.pca_coords = self.pca.fit_transform(self.tfidf_matrix.toarray())
        
        self.is_fitted = True
        return self

    def _extract_cluster_profiles(self, jobs_df: pd.DataFrame):
        """Extracts top TF-IDF keywords and dominant industry domains per cluster."""
        jobs_df_copy = jobs_df.copy()
        jobs_df_copy["cluster"] = self.cluster_assignments
        
        order_centroids = self.kmeans.cluster_centers_.argsort()[:, ::-1]
        
        for cluster_id in range(self.n_clusters):
            # Top 10 TF-IDF terms
            top_term_indices = order_centroids[cluster_id, :10]
            top_terms = [self.feature_names[ind] for ind in top_term_indices]
            self.cluster_top_terms[cluster_id] = top_terms
            
            # Most frequent domain in this cluster
            cluster_jobs = jobs_df_copy[jobs_df_copy["cluster"] == cluster_id]
            if not cluster_jobs.empty:
                dominant_domain = cluster_jobs["domain"].mode()[0]
                dominant_titles = cluster_jobs["job_title"].value_counts().head(3).index.tolist()
            else:
                dominant_domain = f"Cluster {cluster_id}"
                dominant_titles = []
                
            self.cluster_labels_map[cluster_id] = {
                "name": dominant_domain,
                "common_titles": dominant_titles,
                "top_keywords": top_terms,
                "total_jobs": int(len(cluster_jobs))
            }

    def evaluate_k_range(self, jobs_df: pd.DataFrame, k_range=range(2, 10)):
        """Calculates Inertia and Silhouette scores across different values of k for Elbow Method."""
        combined_texts = jobs_df.apply(
            lambda r: f"{r['job_title']} {r['required_skills']} {r['job_description']}", axis=1
        )
        cleaned_corpus = [clean_text(t) for t in combined_texts]
        tfidf = self.vectorizer.fit_transform(cleaned_corpus)
        
        results = []
        for k in k_range:
            km = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=42)
            labels = km.fit_predict(tfidf)
            score = silhouette_score(tfidf, labels)
            results.append({
                "k": k,
                "inertia": float(km.inertia_),
                "silhouette_score": float(score)
            })
        return results

    def transform_intern(self, intern_skills_text: str):
        """Transforms an intern's skill text into the fitted TF-IDF feature space."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before transforming intern skills.")
        cleaned = clean_text(intern_skills_text)
        intern_vec = self.vectorizer.transform([cleaned])
        return intern_vec

    def predict_intern_cluster(self, intern_vec):
        """Predicts the closest industry cluster for an intern."""
        cluster_id = int(self.kmeans.predict(intern_vec)[0])
        cluster_info = self.cluster_labels_map.get(cluster_id, {})
        return cluster_id, cluster_info

    def get_cluster_centroid(self, cluster_id: int):
        """Returns the centroid vector for a given cluster."""
        return self.kmeans.cluster_centers_[cluster_id]

    def save_model(self, filepath="reports/cluster_model.joblib"):
        """Saves the fitted model pipeline."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self, filepath)
        print(f"Model successfully saved to {filepath}")

    @classmethod
    def load_model(cls, filepath="reports/cluster_model.joblib"):
        """Loads a saved model pipeline."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No saved model found at {filepath}")
        return joblib.load(filepath)

if __name__ == "__main__":
    df_jobs = pd.read_csv("data/job_postings.csv")
    model = IndustrySkillClusterModel(n_clusters=6)
    model.fit(df_jobs)
    print(f"Clustering Complete! Average Silhouette Score: {model.silhouette_avg:.4f}")
    for cid, info in model.cluster_labels_map.items():
        print(f"\nCluster {cid} [{info['name']}]: {info['total_jobs']} jobs")
        print(f"  Top terms: {', '.join(info['top_keywords'][:6])}")
