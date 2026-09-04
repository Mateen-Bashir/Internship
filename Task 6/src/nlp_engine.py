"""
AI Chatbot NLP Engine for Internee.pk Intern Queries
Uses:
1. Hugging Face Transformers (`sentence-transformers/all-MiniLM-L6-v2`) for dense semantic embeddings
2. Intent Classification across internship domains
3. Dynamic confidence scoring and smart fallback support ticket triggers
"""

import os
import json
import re
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

class ChatbotNLPEngine:
    def __init__(self, faq_path: str = "data/faq_data.json", ticket_path: str = "data/historical_tickets.json"):
        self.faq_path = faq_path
        self.ticket_path = ticket_path
        
        self.faq_items: List[Dict[str, Any]] = []
        self.ticket_items: List[Dict[str, Any]] = []
        
        self.documents: List[str] = []
        self.doc_metadata: List[Dict[str, Any]] = []
        
        # Hugging Face Transformers model
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.tokenizer = None
        self.hf_model = None
        self.doc_embeddings: Optional[np.ndarray] = None
        
        self.intent_keywords = {
            "Task Submission": [
                "submit", "task", "assignment", "deadline", "late", "extension", 
                "rubric", "grade", "grading", "marks", "github", "repo", "repository", 
                "commit", "evaluation", "score", "link", "upload"
            ],
            "Certificates & Verification": [
                "certificate", "completion", "verification", "lor", "letter of recommendation", 
                "credential", "verify", "download certificate", "diploma", "name spelling"
            ],
            "Account & Portal": [
                "login", "password", "forgot password", "reset", "portal", "lms", 
                "403", "forbidden", "access", "profile", "phone number", "account", "email"
            ],
            "Mentorship & Community": [
                "mentor", "guidance", "discord", "slack", "office hours", "doubt", 
                "ask mentor", "review", "feedback", "community"
            ],
            "Technical Setup": [
                "error", "modulenotfound", "torch", "transformers", "python", 
                "install", "vscode", "venv", "virtual environment", "git", "setup", "pip"
            ],
            "General Policies": [
                "stipend", "paid", "unpaid", "duration", "how long", "pause", 
                "leave", "exam", "freeze", "benefits", "rules", "perks"
            ]
        }
        
        self.load_data()
        self.init_hf_model()
        self.build_index()

    def load_data(self):
        """Loads FAQ knowledge base and historical support tickets."""
        if os.path.exists(self.faq_path):
            with open(self.faq_path, "r", encoding="utf-8") as f:
                self.faq_items = json.load(f)
        
        if os.path.exists(self.ticket_path):
            with open(self.ticket_path, "r", encoding="utf-8") as f:
                self.ticket_items = json.load(f)

    def init_hf_model(self):
        """Initializes Hugging Face Transformers tokenizer and model."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.hf_model = AutoModel.from_pretrained(self.model_name)
            self.hf_model.eval()
        except Exception as e:
            print(f"Warning: Failed to load HF model {self.model_name}: {e}")

    def _get_hf_embedding(self, texts: List[str]) -> np.ndarray:
        """Generates dense vector embeddings using Hugging Face Transformer with mean pooling."""
        if not self.tokenizer or not self.hf_model:
            return np.zeros((len(texts), 384))
        
        encoded = self.tokenizer(texts, padding=True, truncation=True, max_length=128, return_tensors="pt")
        with torch.no_grad():
            model_output = self.hf_model(**encoded)
            # Mean pooling taking attention mask into account
            token_embeddings = model_output[0]
            input_mask_expanded = encoded["attention_mask"].unsqueeze(-1).expand(token_embeddings.size()).float()
            sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
            sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
            pooled = sum_embeddings / sum_mask
            # Normalize embeddings to unit length for direct dot product cosine similarity
            normalized = torch.nn.functional.normalize(pooled, p=2, dim=1)
            return normalized.cpu().numpy()

    def _preprocess(self, text: str) -> str:
        """Cleans and normalizes query text."""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s\-\#\.]", " ", text)
        return " ".join(text.split())

    def build_index(self):
        """Builds combined corpus index and computes Hugging Face embeddings."""
        self.documents = []
        self.doc_metadata = []

        # Index FAQs
        for item in self.faq_items:
            doc_text = f"{item['question']} {item['category']} {item['answer']}"
            self.documents.append(doc_text)
            self.doc_metadata.append({
                "source": "FAQ",
                "id": item["id"],
                "category": item.get("category", "General Inquiry"),
                "question": item["question"],
                "answer": item["answer"],
                "links": item.get("links", [])
            })

        # Index Historical Support Tickets
        for item in self.ticket_items:
            tags_str = " ".join(item.get("tags", []))
            doc_text = f"{item['user_query']} {tags_str} {item['category']} {item['resolution']}"
            self.documents.append(doc_text)
            self.doc_metadata.append({
                "source": "Historical Ticket",
                "id": item["ticket_id"],
                "category": item.get("category", "Support Ticket"),
                "question": item["user_query"],
                "answer": item["resolution"],
                "links": []
            })

        if self.documents and self.hf_model:
            self.doc_embeddings = self._get_hf_embedding(self.documents)

    def detect_intent(self, query: str) -> Tuple[str, float]:
        """Detects the category/intent from the intern query with confidence."""
        cleaned = self._preprocess(query)
        words = set(cleaned.split())
        
        scores = {}
        for intent, kws in self.intent_keywords.items():
            match_count = 0
            for kw in kws:
                if kw in cleaned:
                    match_count += 2 if kw in words else 1
            scores[intent] = match_count

        best_intent = max(scores, key=scores.get)
        total_matches = sum(scores.values())
        
        if total_matches == 0:
            return "General Inquiry", 0.35
            
        confidence = min(0.99, round(scores[best_intent] / max(1, total_matches) * 0.7 + 0.3, 2))
        return best_intent, confidence

    def predict(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Takes an intern query, encodes it with Hugging Face Transformers,
        computes cosine similarity, and returns best answer, confidence, and escalation tags.
        """
        if not query or not query.strip():
            return {
                "answer": "Please ask a question regarding tasks, deadlines, certificates, or portal access.",
                "confidence": 0.0,
                "category": "General Inquiry",
                "source": "None",
                "needs_ticket": False,
                "suggested_questions": self.get_suggested_questions()
            }

        intent, _ = self.detect_intent(query)
        
        if self.doc_embeddings is None:
            return {
                "answer": "NLP Transformer model is indexing. Please retry in a moment.",
                "confidence": 0.0,
                "category": intent,
                "source": "None",
                "needs_ticket": True,
                "suggested_questions": []
            }

        # Encode query using Hugging Face Transformer
        query_emb = self._get_hf_embedding([query])[0]  # shape: (384,)
        # Cosine similarity since vectors are L2-normalized
        similarities = np.dot(self.doc_embeddings, query_emb)

        top_indices = np.argsort(similarities)[::-1][:top_k]
        best_idx = top_indices[0]
        raw_score = float(similarities[best_idx])
        best_match = self.doc_metadata[best_idx]

        # Hugging Face sentence-transformers cosine thresholding
        # Typical range: 0.50+ is high confidence, 0.35 - 0.50 medium, < 0.35 low
        confidence = round(max(0.0, min(1.0, raw_score)), 3)

        CONFIDENCE_HIGH = 0.52
        CONFIDENCE_MEDIUM = 0.38

        if confidence >= CONFIDENCE_HIGH:
            answer = best_match["answer"]
            needs_ticket = False
        elif confidence >= CONFIDENCE_MEDIUM:
            answer = (
                f"{best_match['answer']}\n\n"
                f"*Note: If this doesn't fully resolve your specific issue regarding '{query}', "
                f"you can escalate this directly to an instructor with 1-click support ticket below.*"
            )
            needs_ticket = False
        else:
            answer = (
                f"I couldn't find an exact automated solution in our knowledge base for your inquiry: "
                f"**\"{query}\"**.\n\n"
                f"Would you like me to instantly log an escalated support ticket with our internship coordinators "
                f"under **{intent}**? Our team typically responds within 24 hours."
            )
            needs_ticket = True

        related = self.get_related_questions(best_match.get("category", intent), exclude_id=best_match.get("id"))

        return {
            "query": query,
            "answer": answer,
            "confidence": confidence,
            "category": best_match.get("category", intent),
            "source": best_match.get("source", "FAQ"),
            "model_used": "Hugging Face (sentence-transformers/all-MiniLM-L6-v2)",
            "matched_question": best_match.get("question", ""),
            "links": best_match.get("links", []),
            "needs_ticket": needs_ticket,
            "suggested_questions": related
        }

    def get_suggested_questions(self) -> List[str]:
        return [
            "How do I submit my weekly internship tasks?",
            "Can I submit tasks after the deadline or request an extension?",
            "When will I receive my internship completion certificate?",
            "I forgot my portal password or cannot log in.",
            "How can I connect with my assigned mentor in Discord?",
            "My file is too large to upload directly on portal"
        ]

    def get_related_questions(self, category: str, exclude_id: Optional[str] = None) -> List[str]:
        related = []
        for faq in self.faq_items:
            if faq["id"] != exclude_id and faq.get("category") == category:
                related.append(faq["question"])
                if len(related) >= 3:
                    break
        if len(related) < 3:
            for q in self.get_suggested_questions():
                if q not in related and len(related) < 3:
                    related.append(q)
        return related
