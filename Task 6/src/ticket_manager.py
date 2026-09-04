"""
Ticket Manager for Internee.pk Intern AI Chatbot
Handles ticket persistence, escalation logging, analytics, and status updates.
"""
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

class TicketManager:
    def __init__(self, data_file: str = "data/active_tickets.json", historical_file: str = "data/historical_tickets.json"):
        self.data_file = data_file
        self.historical_file = historical_file
        self.tickets: List[Dict] = []
        self._load_tickets()

    def _load_tickets(self):
        """Loads tickets from disk, initializing if not present."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.tickets = json.load(f)
                return
            except Exception as e:
                print(f"Error reading {self.data_file}: {e}")

        # Seed initial tickets from historical dataset or sensible defaults
        if os.path.exists(self.historical_file):
            try:
                with open(self.historical_file, "r", encoding="utf-8") as f:
                    historical = json.load(f)
                    # convert some to active/recent
                    for item in historical:
                        self.tickets.append({
                            "ticket_id": item["ticket_id"],
                            "intern_name": "Sample Intern",
                            "intern_email": "intern@internee.pk",
                            "category": item["category"],
                            "query": item["user_query"],
                            "status": item.get("status", "Resolved"),
                            "priority": item.get("priority", "Medium"),
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "notes": item.get("resolution", ""),
                            "confidence": 0.95
                        })
            except Exception as e:
                print(f"Error reading {self.historical_file}: {e}")
        self._save_tickets()

    def _save_tickets(self):
        """Persists tickets to disk."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.tickets, f, indent=2)

    def create_ticket(self, query: str, category: str, intern_name: str = "Guest Intern", 
                      intern_email: str = "intern@internee.pk", priority: str = "Medium", 
                      confidence: float = 0.0) -> Dict:
        """Creates a new escalated support ticket."""
        ticket_id = f"TCK-{len(self.tickets) + 1001}"
        new_ticket = {
            "ticket_id": ticket_id,
            "intern_name": intern_name,
            "intern_email": intern_email,
            "category": category or "General Inquiry",
            "query": query,
            "status": "Open",
            "priority": priority,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "notes": "Escalated from AI Chatbot for mentor review.",
            "confidence": round(confidence, 3)
        }
        self.tickets.insert(0, new_ticket)
        self._save_tickets()
        return new_ticket

    def get_tickets(self, limit: int = 50, status: Optional[str] = None) -> List[Dict]:
        """Returns list of tickets with optional status filter."""
        filtered = self.tickets
        if status:
            filtered = [t for t in self.tickets if t.get("status", "").lower() == status.lower()]
        return filtered[:limit]

    def update_status(self, ticket_id: str, new_status: str, notes: Optional[str] = None) -> Optional[Dict]:
        """Updates ticket status (e.g. Open, In Progress, Resolved)."""
        for t in self.tickets:
            if t["ticket_id"] == ticket_id:
                t["status"] = new_status
                if notes:
                    t["notes"] = notes
                self._save_tickets()
                return t
        return None

    def get_stats(self) -> Dict:
        """Returns support analytics and status distributions."""
        total = len(self.tickets)
        open_count = sum(1 for t in self.tickets if t.get("status") == "Open")
        in_progress = sum(1 for t in self.tickets if t.get("status") == "In Progress")
        resolved = sum(1 for t in self.tickets if t.get("status") == "Resolved")
        
        category_counts = {}
        for t in self.tickets:
            cat = t.get("category", "General Inquiry")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "total_tickets": total,
            "open": open_count,
            "in_progress": in_progress,
            "resolved": resolved,
            "resolution_rate": f"{round((resolved / total * 100) if total else 0, 1)}%",
            "by_category": category_counts
        }
