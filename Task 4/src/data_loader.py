"""
Data Loader and Repository Accessor for Interview Question Generation System
"""

import json
import os
from typing import List, Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

class DataLoader:
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self._question_bank: List[Dict[str, Any]] = []
        self._intern_profiles: List[Dict[str, Any]] = []
        self._job_descriptions: List[Dict[str, Any]] = []
        self._competency_framework: Dict[str, Any] = {}
        self.load_all()

    def load_all(self):
        self._question_bank = self._load_json("question_banks.json", default=[])
        self._intern_profiles = self._load_json("intern_profiles.json", default=[])
        self._job_descriptions = self._load_json("job_descriptions.json", default=[])
        self._competency_framework = self._load_json("competency_framework.json", default={})

    def _load_json(self, filename: str, default: Any = None) -> Any:
        path = os.path.join(self.data_dir, filename)
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return default

    @property
    def question_bank(self) -> List[Dict[str, Any]]:
        return self._question_bank

    @property
    def intern_profiles(self) -> List[Dict[str, Any]]:
        return self._intern_profiles

    @property
    def job_descriptions(self) -> List[Dict[str, Any]]:
        return self._job_descriptions

    @property
    def competency_framework(self) -> Dict[str, Any]:
        return self._competency_framework

    def get_profile_by_id(self, profile_id: str) -> Optional[Dict[str, Any]]:
        for p in self._intern_profiles:
            if p.get("id") == profile_id:
                return p
        return None

    def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        for j in self._job_descriptions:
            if j.get("id") == job_id:
                return j
        return None

    def search_questions(
        self,
        track: Optional[str] = None,
        difficulty: Optional[str] = None,
        q_type: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        results = []
        for q in self._question_bank:
            if track and track.lower() not in q.get("track", "").lower() and q.get("track", "") != "General Engineering / Cross-Track":
                continue
            if difficulty and difficulty.lower() != q.get("difficulty", "").lower():
                continue
            if q_type and q_type.lower() != q.get("type", "").lower():
                continue
            if keyword:
                kw = keyword.lower()
                text_content = f"{q.get('question', '')} {q.get('topic', '')} {q.get('skill', '')}".lower()
                if kw not in text_content:
                    continue
            results.append(q)
            if len(results) >= limit:
                break
        return results

    def get_tracks(self) -> List[str]:
        tracks = set()
        for j in self._job_descriptions:
            if "track" in j:
                tracks.add(j["track"])
        return sorted(list(tracks))
