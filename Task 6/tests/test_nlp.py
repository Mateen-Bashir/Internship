import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.nlp_engine import ChatbotNLPEngine
from src.ticket_manager import TicketManager

class TestChatbot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = ChatbotNLPEngine(faq_path="data/faq_data.json", ticket_path="data/historical_tickets.json")
        cls.ticket_mgr = TicketManager(data_file="data/test_tickets.json", historical_file="data/historical_tickets.json")

    def test_faq_submission_query(self):
        res = self.engine.predict("how to submit weekly task 6 on portal")
        self.assertIn("GitHub", res["answer"])
        self.assertGreaterEqual(res["confidence"], 0.3)
        self.assertEqual(res["needs_ticket"], False)

    def test_certificate_query(self):
        res = self.engine.predict("when can I download my completion certificate?")
        self.assertIn("certificate", res["answer"].lower())
        self.assertGreaterEqual(res["confidence"], 0.3)

    def test_historical_ticket_match(self):
        res = self.engine.predict("error 403 forbidden on assignment portal")
        self.assertIn("cookies", res["answer"].lower())
        self.assertEqual(res["source"], "Historical Ticket")

    def test_low_confidence_fallback(self):
        res = self.engine.predict("what is the weather on mars today?")
        self.assertTrue(res["needs_ticket"])
        self.assertLess(res["confidence"], 0.22)

    def test_ticket_creation(self):
        ticket = self.ticket_mgr.create_ticket(
            query="Cannot submit task",
            category="Task Submission",
            intern_name="Test User",
            intern_email="test@user.com",
            priority="High",
            confidence=0.1
        )
        self.assertIn("TCK-", ticket["ticket_id"])
        self.assertEqual(ticket["status"], "Open")

if __name__ == "__main__":
    unittest.main()
