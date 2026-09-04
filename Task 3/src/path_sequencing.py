"""
Pedagogical Prerequisite Sequencing & Learning Path Engine
Internee.pk - Task 3: Personalized Learning Path Recommendation System

Implements:
1. Directed Acyclic Graph (DAG) of course prerequisites via NetworkX
2. Topological Sort & Dependency Resolution
3. Milestone Staging (Foundations -> Core Competency -> Advanced Mastery)
4. Cold-Start Track Bootstrapping
"""

import networkx as nx
import pandas as pd
import numpy as np

class LearningPathSequencer:
    """
    Transforms raw collaborative filtering recommendation scores into a pedagogically
    valid, prerequisite-respecting, milestone-based sequential learning path.
    """
    
    def __init__(self, courses_df):
        self.courses_df = courses_df.copy()
        self.course_map = {row['module_id']: row.to_dict() for _, row in self.courses_df.iterrows()}
        
        # Parse prerequisites
        for m_id, data in self.course_map.items():
            raw_prereqs = data.get('prerequisites', 'None')
            if isinstance(raw_prereqs, str):
                data['prereq_list'] = [p.strip() for p in raw_prereqs.split(',') if p.strip() and p.strip() != 'None']
            elif isinstance(raw_prereqs, list):
                data['prereq_list'] = raw_prereqs
            else:
                data['prereq_list'] = []
                
        # Build NetworkX Directed Acyclic Graph
        self.graph = nx.DiGraph()
        for m_id, data in self.course_map.items():
            self.graph.add_node(m_id, **data)
            for prereq in data['prereq_list']:
                if prereq in self.course_map:
                    # Edge from Prerequisite -> Dependent Module
                    self.graph.add_edge(prereq, m_id)
                    
        # Check DAG validity
        if not nx.is_directed_acyclic_graph(self.graph):
            cycles = list(nx.simple_cycles(self.graph))
            raise ValueError(f"Prerequisite graph contains cycles: {cycles}")

    def get_all_prerequisites(self, module_id):
        """Recursively retrieves all ancestral prerequisites for a given module."""
        if module_id not in self.graph:
            return set()
        return nx.ancestors(self.graph, module_id)

    def sequence_recommendations(self, predicted_scores, completed_modules=None, target_track=None, top_n=8):
        """
        Sequences recommended modules for an intern.
        
        Parameters:
            predicted_scores (dict): {module_id: score} from Matrix Factorization
            completed_modules (set or list): Already finished module IDs (to exclude)
            target_track (str): Filter/boost target track if desired
            top_n (int): Target number of modules in the learning roadmap
            
        Returns:
            dict: Structured roadmap with milestones, total hours, and prerequisite dependencies.
        """
        completed = set(completed_modules) if completed_modules else set()
        
        # 1. Calculate boosted scores based on track affinity
        candidate_scores = {}
        for m_id, score in predicted_scores.items():
            if m_id in completed:
                continue
            module_info = self.course_map.get(m_id)
            if not module_info:
                continue
                
            boost = 1.0
            if target_track and module_info['domain'] == target_track:
                boost = 1.15  # Domain priority boost
            candidate_scores[m_id] = score * boost

        # 2. Select top candidate modules
        sorted_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        selected_ids = set()
        
        for m_id, _ in sorted_candidates:
            if len(selected_ids) >= top_n:
                break
            selected_ids.add(m_id)
            # Ensure all prerequisite modules are automatically included in the path!
            needed_prereqs = self.get_all_prerequisites(m_id) - completed
            selected_ids.update(needed_prereqs)

        # 3. Create sub-graph of selected modules and perform Topological Sort
        subgraph = self.graph.subgraph(selected_ids)
        
        # Topological sort respects prerequisite order
        ordered_module_ids = list(nx.topological_sort(subgraph))
        
        # Secondary sort key: Group by difficulty level while preserving topological precedence
        difficulty_order = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
        
        # 4. Group into 3 Structured Milestones
        milestones = {
            "Milestone 1: Foundations & Core Concepts": [],
            "Milestone 2: Applied Skills & Core Technologies": [],
            "Milestone 3: Advanced Architectures & Production Mastery": []
        }
        
        total_duration = 0
        all_skills = set()
        
        for step_idx, m_id in enumerate(ordered_module_ids, start=1):
            mod_data = self.course_map[m_id].copy()
            pred_score = predicted_scores.get(m_id, 4.0)
            
            # Prerequisite status check
            prereq_names = [self.course_map[p]['title'] for p in mod_data['prereq_list'] if p in self.course_map]
            
            module_card = {
                "step_order": step_idx,
                "module_id": m_id,
                "title": mod_data['title'],
                "domain": mod_data['domain'],
                "difficulty_level": mod_data['difficulty_level'],
                "duration_hours": mod_data['duration_hours'],
                "skills": [s.strip() for s in str(mod_data['skills']).split(',')],
                "predicted_rating": round(pred_score, 2),
                "rating_avg": mod_data['rating_avg'],
                "prerequisites": mod_data['prereq_list'],
                "prerequisite_titles": prereq_names,
                "description": mod_data['description']
            }
            
            total_duration += mod_data['duration_hours']
            all_skills.update(module_card['skills'])
            
            # Assign to milestone based on difficulty
            if mod_data['difficulty_level'] == "Beginner":
                milestones["Milestone 1: Foundations & Core Concepts"].append(module_card)
            elif mod_data['difficulty_level'] == "Intermediate":
                milestones["Milestone 2: Applied Skills & Core Technologies"].append(module_card)
            else:
                milestones["Milestone 3: Advanced Architectures & Production Mastery"].append(module_card)
                
        # Remove empty milestones
        clean_milestones = {k: v for k, v in milestones.items() if len(v) > 0}
        
        return {
            "total_modules": len(ordered_module_ids),
            "total_duration_hours": total_duration,
            "skills_covered_count": len(all_skills),
            "skills_list": sorted(list(all_skills)),
            "milestones": clean_milestones,
            "sequential_modules": [m for milestone in clean_milestones.values() for m in milestone]
        }

    def generate_cold_start_path(self, target_track, skill_level="Beginner", top_n=6):
        """
        Cold-Start Handler for new interns without prior interaction history.
        Constructs a curated path using track curriculum DAG and domain rating averages.
        """
        track_courses = self.courses_df[self.courses_df['domain'] == target_track]
        if track_courses.empty:
            track_courses = self.courses_df
            
        scores = {}
        for _, row in self.courses_df.iterrows():
            m_id = row['module_id']
            base_score = row['rating_avg']
            
            # Domain match boost
            if row['domain'] == target_track:
                base_score += 0.5
            
            # Skill level alignment
            if skill_level == "Beginner" and row['difficulty_level'] == "Beginner":
                base_score += 0.3
            elif skill_level == "Intermediate" and row['difficulty_level'] == "Intermediate":
                base_score += 0.3
            elif skill_level == "Advanced" and row['difficulty_level'] == "Advanced":
                base_score += 0.3
                
            scores[m_id] = min(5.0, base_score)
            
        return self.sequence_recommendations(scores, completed_modules=[], target_track=target_track, top_n=top_n)
