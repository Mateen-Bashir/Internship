"""
High-Level Recommender Pipeline & Coordinator
Internee.pk - Task 3: Personalized Learning Path Recommendation System

Integrates:
- Data Ingestion & Indexing
- Matrix Factorization Collaborative Filtering Engine
- Prerequisite DAG Sequencer
- Profile & Analytics Query Methods
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from src.matrix_factorization import SVDMatrixFactorization, NMFRecommender, evaluate_recommender
from src.path_sequencing import LearningPathSequencer

class PersonalizedLearningRecommenderPipeline:
    """
    Main entry point for learning path recommendation workflows.
    """
    
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.data_dir = data_dir
        
        # Data containers
        self.courses_df = None
        self.profiles_df = None
        self.interactions_df = None
        
        # Models & Components
        self.svd_model = None
        self.nmf_model = None
        self.sequencer = None
        self.metrics = {}
        
        self._load_and_train()
        
    def _load_and_train(self):
        """Loads data, trains models, evaluates metrics, and initializes sequencer."""
        courses_path = os.path.join(self.data_dir, "courses_metadata.csv")
        profiles_path = os.path.join(self.data_dir, "intern_profiles.csv")
        interactions_path = os.path.join(self.data_dir, "intern_interactions.csv")
        
        if not (os.path.exists(courses_path) and os.path.exists(profiles_path) and os.path.exists(interactions_path)):
            raise FileNotFoundError("Dataset CSVs not found in data/. Run data_generator.py first.")
            
        self.courses_df = pd.read_csv(courses_path).fillna("None")
        self.profiles_df = pd.read_csv(profiles_path).fillna("None")
        self.interactions_df = pd.read_csv(interactions_path).fillna(0)
        
        # 1. Initialize Sequencer
        self.sequencer = LearningPathSequencer(self.courses_df)
        
        # 2. Train/Test Split (80/20) for rigorous evaluation
        train_df, test_df = train_test_split(self.interactions_df, test_size=0.20, random_state=42)
        
        # 3. Train SVD Matrix Factorization
        self.svd_model = SVDMatrixFactorization(n_factors=12, reg=0.02)
        self.svd_model.fit(train_df)
        
        # 4. Train NMF baseline
        self.nmf_model = NMFRecommender(n_factors=12)
        self.nmf_model.fit(train_df)
        
        # 5. Evaluate Performance
        svd_eval = evaluate_recommender(self.svd_model, test_df, k=5)
        nmf_eval = evaluate_recommender(self.nmf_model, test_df, k=5)
        
        self.metrics = {
            "SVD (Proposed)": svd_eval,
            "NMF (Baseline)": nmf_eval,
            "Total_Users": len(self.profiles_df),
            "Total_Courses": len(self.courses_df),
            "Total_Interactions": len(self.interactions_df)
        }
        
        # Fit on full dataset for final deployment
        self.svd_model.fit(self.interactions_df)
        self.nmf_model.fit(self.interactions_df)

    def get_intern_profile(self, intern_id):
        """Fetches profile for a specific intern."""
        match = self.profiles_df[self.profiles_df['intern_id'] == intern_id]
        if not match.empty:
            return match.iloc[0].to_dict()
        return None

    def get_intern_history(self, intern_id):
        """Fetches completed & ongoing modules for an intern."""
        history = self.interactions_df[self.interactions_df['intern_id'] == intern_id]
        if history.empty:
            return []
        
        merged = history.merge(self.courses_df, on='module_id', how='left')
        return merged.to_dict(orient='records')

    def recommend_for_intern(self, intern_id, top_n=8):
        """
        Generates personalized sequential learning path for an existing intern.
        """
        profile = self.get_intern_profile(intern_id)
        if not profile:
            # Fallback to cold-start
            return self.recommend_cold_start(target_track="Data Science & Analytics", skill_level="Beginner", top_n=top_n)
            
        history = self.get_intern_history(intern_id)
        completed_modules = [h['module_id'] for h in history if h.get('status') == 'Completed' or h.get('completion_percentage', 0) >= 80]
        
        # Get SVD predicted ratings for all modules
        predicted_scores = self.svd_model.get_all_predictions_for_user(intern_id)
        
        # Sequence through DAG
        roadmap = self.sequencer.sequence_recommendations(
            predicted_scores=predicted_scores,
            completed_modules=completed_modules,
            target_track=profile['primary_track'],
            top_n=top_n
        )
        
        roadmap['intern_profile'] = profile
        roadmap['completed_modules_count'] = len(completed_modules)
        roadmap['history'] = history
        return roadmap

    def recommend_cold_start(self, target_track, skill_level="Beginner", top_n=8):
        """
        Generates customized learning path for a brand new intern.
        """
        roadmap = self.sequencer.generate_cold_start_path(
            target_track=target_track,
            skill_level=skill_level,
            top_n=top_n
        )
        roadmap['intern_profile'] = {
            "intern_id": "NEW_INTERN",
            "name": "Guest / New Intern",
            "primary_track": target_track,
            "secondary_track": "None",
            "experience_level": skill_level,
            "learning_pace": "Standard (10 hrs/wk)"
        }
        roadmap['completed_modules_count'] = 0
        roadmap['history'] = []
        return roadmap
