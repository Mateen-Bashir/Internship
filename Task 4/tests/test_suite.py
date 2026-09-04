"""
Comprehensive Standard Unit Test Suite for AI Interview Question Generator
Using Python's standard unittest module.
"""

import unittest
import os
import json
import tempfile
import shutil

from src.data_loader import DataLoader
from src.gap_analyzer import GapAnalyzer
from src.llm_generator import InterviewQuestionGenerator
from src.rubric_engine import RubricEngine
from src.mock_evaluator import MockResponseEvaluator
from src.export_service import ExportService
from src.evaluator import GenerationEvaluator

class TestInterviewQuestionGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = DataLoader()
        cls.generator = InterviewQuestionGenerator(cls.loader)
        cls.sample_profile = cls.loader.intern_profiles[0]
        cls.sample_job = cls.loader.job_descriptions[0]
        cls.temp_dir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_01_data_loader(self):
        self.assertGreater(len(self.loader.question_bank), 500)
        self.assertGreaterEqual(len(self.loader.intern_profiles), 50)
        self.assertGreaterEqual(len(self.loader.job_descriptions), 8)
        self.assertGreaterEqual(len(self.loader.get_tracks()), 8)
        
        # Test search
        res = self.loader.search_questions(track="AI & Machine Learning", q_type="Technical", limit=10)
        self.assertGreater(len(res), 0)

    def test_02_gap_analyzer(self):
        analysis = GapAnalyzer.analyze(self.sample_profile, self.sample_job)
        self.assertIn("overall_fit_score", analysis)
        self.assertTrue(0.0 <= analysis["overall_fit_score"] <= 100.0)
        self.assertIn("matched_required_skills", analysis)
        self.assertIn("missing_required_skills", analysis)
        self.assertIn("radar_dimensions", analysis)
        self.assertIn("recommendations", analysis)
        self.assertGreaterEqual(len(analysis["radar_dimensions"]), 4)

    def test_03_question_generation_neural(self):
        kit = self.generator.generate(
            profile=self.sample_profile,
            job_desc=self.sample_job,
            backend="rag_neural",
            num_technical=4,
            num_behavioral=2,
            num_project=1
        )
        
        self.assertIn("interview_meta", kit)
        self.assertIn("technical_questions", kit)
        self.assertIn("behavioral_questions", kit)
        self.assertIn("project_deep_dive_questions", kit)
        self.assertIn("coding_scenario", kit)

        self.assertEqual(len(kit["technical_questions"]), 4)
        self.assertEqual(len(kit["behavioral_questions"]), 2)
        self.assertEqual(len(kit["project_deep_dive_questions"]), 1)

        # Validate schema of technical question
        tq = kit["technical_questions"][0]
        self.assertIn("question", tq)
        self.assertIn("expected_answer_points", tq)
        self.assertIn("rubric_5_scale", tq)
        self.assertIn("difficulty", tq)
        self.assertIn(tq["difficulty"], ["Easy", "Medium", "Hard"])

        # Validate schema of behavioral question
        bq = kit["behavioral_questions"][0]
        self.assertIn("star_framework", bq)
        self.assertIn("green_flags", bq)
        self.assertIn("red_flags", bq)

    def test_04_benchmark_evaluator(self):
        kit = self.generator.generate(
            profile=self.sample_profile,
            job_desc=self.sample_job,
            num_technical=5,
            num_behavioral=3
        )
        metrics = GenerationEvaluator.evaluate_kit(kit, self.sample_profile, self.sample_job)
        
        self.assertIn("composite_quality_index", metrics)
        self.assertTrue(0 <= metrics["composite_quality_index"] <= 100)
        self.assertEqual(metrics["star_completeness_pct"], 100.0)
        self.assertGreater(metrics["lexical_distinct_2_ratio"], 0.5)
        self.assertIn(metrics["benchmark_status"], ["GOOD", "EXCELLENT"])

    def test_05_mock_response_evaluator(self):
        question_data = {
            "category": "Technical",
            "question": "Explain how backpropagation and gradient descent work.",
            "expected_answer_points": [
                "Forward pass calculates loss",
                "Chain rule calculates gradients",
                "Gradient descent updates weights"
            ],
            "follow_up_probe": "How do you mitigate vanishing gradients?"
        }

        # Test complete answer
        good_answer = "During the forward pass the model computes predictions and loss. Then the chain rule calculates gradients with respect to weights, and gradient descent updates weights in the opposite direction."
        result_good = MockResponseEvaluator.evaluate_response(question_data, good_answer)
        self.assertGreaterEqual(result_good["score"], 3.0)
        self.assertGreater(len(result_good["matched_criteria"]), 0)

        # Test poor/empty answer
        poor_answer = "I don't know."
        result_poor = MockResponseEvaluator.evaluate_response(question_data, poor_answer)
        self.assertEqual(result_poor["score"], 1.0)

    def test_06_rubric_engine(self):
        kit = self.generator.generate(profile=self.sample_profile, job_desc=self.sample_job)
        scorecard = RubricEngine.generate_scorecard_template(kit)
        self.assertIn("scorecard_entries", scorecard)
        self.assertIn("rubric_scale", scorecard)
        self.assertIn("technical", scorecard["scorecard_entries"])

    def test_07_export_service(self):
        kit = self.generator.generate(profile=self.sample_profile, job_desc=self.sample_job)
        
        md_path = os.path.join(self.temp_dir, "test.md")
        json_path = os.path.join(self.temp_dir, "test.json")
        html_path = os.path.join(self.temp_dir, "test.html")

        ExportService.to_markdown(kit, md_path)
        ExportService.to_json(kit, json_path)
        ExportService.to_html(kit, html_path)

        self.assertTrue(os.path.exists(md_path))
        self.assertTrue(os.path.exists(json_path))
        self.assertTrue(os.path.exists(html_path))

        with open(md_path, "r", encoding="utf-8") as f:
            md_text = f.read()
            self.assertIn(self.sample_profile["name"], md_text)
            self.assertIn("Technical Questions", md_text)

if __name__ == "__main__":
    unittest.main()
