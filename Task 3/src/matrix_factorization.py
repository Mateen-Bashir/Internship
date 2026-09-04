"""
Matrix Factorization Recommendation Engine
Internee.pk - Task 3: Personalized Learning Path Recommendation System

Implements:
1. SVD Matrix Factorization with Baseline Biases (mu + b_u + b_i + P_u @ Q_i^T)
2. NMF (Non-Negative Matrix Factorization) Recommender
3. Train/Test Evaluation Pipeline (RMSE, MAE, Precision@K, Recall@K, NDCG@K)
"""

import numpy as np
import pandas as pd
from scipy.sparse.linalg import svds
from sklearn.decomposition import NMF
from sklearn.model_selection import train_test_split

class SVDMatrixFactorization:
    """
    Singular Value Decomposition (SVD) with User & Item Biases
    for Collaborative Filtering Rating Prediction.
    
    Formula:
        r_hat(u, i) = mu + b_u + b_i + p_u @ q_i^T
    where:
        mu  = global mean rating
        b_u = user bias (mean user rating - mu)
        b_i = item bias (mean item rating - mu)
        p_u = user latent factor vector (1 x k)
        q_i = item latent factor vector (1 x k)
    """
    
    def __init__(self, n_factors=10, reg=0.02, min_rating=1.0, max_rating=5.0):
        self.n_factors = n_factors
        self.reg = reg
        self.min_rating = min_rating
        self.max_rating = max_rating
        
        self.global_mean = 0.0
        self.user_biases = {}
        self.item_biases = {}
        self.user_factors = None
        self.item_factors = None
        
        self.user_to_idx = {}
        self.idx_to_user = {}
        self.item_to_idx = {}
        self.idx_to_item = {}
        
        self.predicted_matrix = None
        self.user_item_matrix = None
        
    def fit(self, interactions_df):
        """
        Fits the SVD Matrix Factorization model on user-item interaction DataFrame.
        Expected columns: ['intern_id', 'module_id', 'rating']
        """
        # Create mapping indexes
        unique_users = interactions_df['intern_id'].unique()
        unique_items = interactions_df['module_id'].unique()
        
        self.user_to_idx = {u: idx for idx, u in enumerate(unique_users)}
        self.idx_to_user = {idx: u for idx, u in enumerate(unique_users)}
        self.item_to_idx = {i: idx for idx, i in enumerate(unique_items)}
        self.idx_to_item = {idx: i for idx, i in enumerate(unique_items)}
        
        num_users = len(unique_users)
        num_items = len(unique_items)
        
        # Build Interaction Matrix (dense for SVD centering)
        self.user_item_matrix = np.full((num_users, num_items), np.nan)
        for _, row in interactions_df.iterrows():
            u_idx = self.user_to_idx[row['intern_id']]
            i_idx = self.item_to_idx[row['module_id']]
            self.user_item_matrix[u_idx, i_idx] = float(row['rating'])
            
        # 1. Global Mean
        self.global_mean = float(np.nanmean(self.user_item_matrix))
        
        # 2. User & Item Biases with Damping Regularization
        self.user_biases = np.zeros(num_users)
        for u_idx in range(num_users):
            user_ratings = self.user_item_matrix[u_idx, ~np.isnan(self.user_item_matrix[u_idx, :])]
            if len(user_ratings) > 0:
                # Regularized user bias
                self.user_biases[u_idx] = (np.sum(user_ratings - self.global_mean)) / (len(user_ratings) + self.reg * 10)
                
        self.item_biases = np.zeros(num_items)
        for i_idx in range(num_items):
            item_ratings = self.user_item_matrix[~np.isnan(self.user_item_matrix[:, i_idx]), i_idx]
            if len(item_ratings) > 0:
                # Regularized item bias
                self.item_biases[i_idx] = (np.sum(item_ratings - self.global_mean)) / (len(item_ratings) + self.reg * 10)
                
        # 3. Compute Residual Matrix (R - mu - b_u - b_i)
        residual_matrix = np.zeros((num_users, num_items))
        for u_idx in range(num_users):
            for i_idx in range(num_items):
                val = self.user_item_matrix[u_idx, i_idx]
                if not np.isnan(val):
                    residual_matrix[u_idx, i_idx] = val - (self.global_mean + self.user_biases[u_idx] + self.item_biases[i_idx])
                else:
                    residual_matrix[u_idx, i_idx] = 0.0  # Zero imputation on centered residuals
                    
        # 4. Truncated SVD on Residuals
        # Effective k cannot exceed min(num_users, num_items) - 1
        k = min(self.n_factors, min(num_users, num_items) - 1)
        U, sigma, Vt = svds(residual_matrix, k=k)
        
        # Sort singular values in descending order
        sort_indices = np.argsort(sigma)[::-1]
        sigma = sigma[sort_indices]
        U = U[:, sort_indices]
        Vt = Vt[sort_indices, :]
        
        # Latent factor embeddings
        sigma_sqrt = np.diag(np.sqrt(sigma))
        self.user_factors = np.dot(U, sigma_sqrt)          # shape: (num_users, k)
        self.item_factors = np.dot(sigma_sqrt, Vt).T        # shape: (num_items, k)
        
        # 5. Full Reconstruction Matrix
        interaction_factors = np.dot(self.user_factors, self.item_factors.T)
        
        # Broadcast biases
        bias_matrix = self.global_mean + self.user_biases[:, np.newaxis] + self.item_biases[np.newaxis, :]
        self.predicted_matrix = bias_matrix + interaction_factors
        
        # Clip to valid rating bounds
        self.predicted_matrix = np.clip(self.predicted_matrix, self.min_rating, self.max_rating)
        return self
        
    def predict_rating(self, intern_id, module_id):
        """Predicts rating score for a specific intern and module."""
        if intern_id in self.user_to_idx and module_id in self.item_to_idx:
            u_idx = self.user_to_idx[intern_id]
            i_idx = self.item_to_idx[module_id]
            return float(self.predicted_matrix[u_idx, i_idx])
        elif module_id in self.item_to_idx:
            # Fallback for new user (Item bias + global mean)
            i_idx = self.item_to_idx[module_id]
            return float(np.clip(self.global_mean + self.item_biases[i_idx], self.min_rating, self.max_rating))
        elif intern_id in self.user_to_idx:
            # Fallback for new item (User bias + global mean)
            u_idx = self.user_to_idx[intern_id]
            return float(np.clip(self.global_mean + self.user_biases[u_idx], self.min_rating, self.max_rating))
        else:
            return float(self.global_mean)
            
    def get_all_predictions_for_user(self, intern_id):
        """Returns a dict of {module_id: predicted_rating} for all catalog modules."""
        if intern_id in self.user_to_idx:
            u_idx = self.user_to_idx[intern_id]
            preds = self.predicted_matrix[u_idx, :]
            return {self.idx_to_item[i]: float(preds[i]) for i in range(len(preds))}
        else:
            # Cold-start fallback
            return {
                m_id: float(np.clip(self.global_mean + self.item_biases[self.item_to_idx[m_id]], self.min_rating, self.max_rating))
                if m_id in self.item_to_idx else self.global_mean
                for m_id in self.item_to_idx.keys()
            }


class NMFRecommender:
    """Non-Negative Matrix Factorization Recommender Baseline."""
    def __init__(self, n_factors=10, min_rating=1.0, max_rating=5.0):
        self.n_factors = n_factors
        self.min_rating = min_rating
        self.max_rating = max_rating
        self.user_to_idx = {}
        self.idx_to_user = {}
        self.item_to_idx = {}
        self.idx_to_item = {}
        self.predicted_matrix = None
        
    def fit(self, interactions_df):
        unique_users = interactions_df['intern_id'].unique()
        unique_items = interactions_df['module_id'].unique()
        self.user_to_idx = {u: idx for idx, u in enumerate(unique_users)}
        self.idx_to_user = {idx: u for idx, u in enumerate(unique_users)}
        self.item_to_idx = {i: idx for idx, i in enumerate(unique_items)}
        self.idx_to_item = {idx: i for idx, i in enumerate(unique_items)}
        
        matrix = np.zeros((len(unique_users), len(unique_items)))
        for _, row in interactions_df.iterrows():
            u = self.user_to_idx[row['intern_id']]
            i = self.item_to_idx[row['module_id']]
            matrix[u, i] = float(row['rating'])
            
        nmf = NMF(n_components=min(self.n_factors, len(unique_items) - 1), init='nndsvda', random_state=42, max_iter=300)
        W = nmf.fit_transform(matrix)
        H = nmf.components_
        self.predicted_matrix = np.clip(np.dot(W, H), self.min_rating, self.max_rating)
        return self

    def predict_rating(self, intern_id, module_id):
        if intern_id in self.user_to_idx and module_id in self.item_to_idx:
            u_idx = self.user_to_idx[intern_id]
            i_idx = self.item_to_idx[module_id]
            return float(self.predicted_matrix[u_idx, i_idx])
        return 3.5


# ----------------------------------------------------------------------
# EVALUATION MODULE
# ----------------------------------------------------------------------
def evaluate_recommender(model, test_df, k=5, threshold=4.0):
    """
    Evaluates Matrix Factorization model on held-out test interactions.
    Computes:
      - RMSE (Root Mean Squared Error)
      - MAE (Mean Absolute Error)
      - Precision@K
      - Recall@K
      - NDCG@K
    """
    y_true = []
    y_pred = []
    
    # Per-user evaluation for ranking metrics
    user_test_groups = test_df.groupby('intern_id')
    precisions = []
    recalls = []
    ndcgs = []
    
    for intern_id, group in user_test_groups:
        actual_ratings = dict(zip(group['module_id'], group['rating']))
        
        # Rating error collection
        for mod_id, actual in actual_ratings.items():
            pred = model.predict_rating(intern_id, mod_id)
            y_true.append(actual)
            y_pred.append(pred)
            
        # Top-K ranking metrics
        # Relevant items: actual rating >= threshold
        relevant_items = {m for m, r in actual_ratings.items() if r >= threshold}
        if not relevant_items:
            continue
            
        # Predict on all items in test set for this user
        ranked_items = sorted(actual_ratings.keys(), key=lambda m: model.predict_rating(intern_id, m), reverse=True)[:k]
        hits = len(set(ranked_items) & relevant_items)
        
        precision_k = hits / k
        recall_k = hits / len(relevant_items)
        
        # DCG & IDCG for NDCG@K
        dcg = sum([1.0 / np.log2(idx + 2) for idx, m in enumerate(ranked_items) if m in relevant_items])
        idcg = sum([1.0 / np.log2(idx + 2) for idx in range(min(k, len(relevant_items)))])
        ndcg_k = dcg / idcg if idcg > 0 else 0.0
        
        precisions.append(precision_k)
        recalls.append(recall_k)
        ndcgs.append(ndcg_k)
        
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    mae = np.mean(np.abs(y_true - y_pred))
    mean_precision = np.mean(precisions) if precisions else 0.0
    mean_recall = np.mean(recalls) if recalls else 0.0
    mean_ndcg = np.mean(ndcgs) if ndcgs else 0.0
    
    return {
        "RMSE": round(float(rmse), 4),
        "MAE": round(float(mae), 4),
        f"Precision@{k}": round(float(mean_precision), 4),
        f"Recall@{k}": round(float(mean_recall), 4),
        f"NDCG@{k}": round(float(mean_ndcg), 4)
    }
