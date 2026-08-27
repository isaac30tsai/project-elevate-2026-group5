"""Hybrid Knowledge RAG Tool for Altostrat Employee Policy Handbook §6~§35."""
from typing import Dict, Any, List

class PolicyRAGClient:
    def __init__(self):
        self.knowledge_base = {
            "sick_leave": {
                "section": "§12.1",
                "title": "Outpatient Sick Leave & Medical Certificates",
                "keywords": ["sick", "medical", "mc", "outpatient", "doctor", "clinic", "illness"],
                "content": "Full-time employees are entitled to 14 days of paid outpatient sick leave per calendar year. A recognized Medical Certificate (MC) from a registered clinic must be uploaded within 48 hours for absences exceeding 2 consecutive days."
            },
            "vacation_accrual": {
                "section": "§8.3",
                "title": "Annual Vacation Entitlement & Accrual",
                "keywords": ["vacation", "annual", "accrual", "tenure", "holiday", "shift"],
                "content": "Employees with 1-3 years of tenure receive 18 days annual leave. Employees with 4-7 years receive 20 days. Employees with 8+ years receive 21 days annual leave. Shift workers logging 12-hour shifts consume 1.5 vacation days per shift."
            },
            "bereavement_leave": {
                "section": "§14.2",
                "title": "Compassionate & Bereavement Leave",
                "keywords": ["bereavement", "compassionate", "death", "funeral", "family", "passed away"],
                "content": "Altostrat provides 5 consecutive days of paid compassionate leave for immediate family members (spouse, children, parents, siblings). 3 days are provided for grandparents. Proof of relationship/death certificate must be provided to People Operations."
            },
            "parental_leave": {
                "section": "§15.1",
                "title": "Parental & Maternity Leave",
                "keywords": ["parental", "maternity", "paternity", "gpml", "gppl", "child", "baby", "birth"],
                "content": "Eligible female employees receive 16 weeks of Government-Paid Maternity Leave (GPML). Eligible male employees receive 4 weeks of Government-Paid Paternity Leave (GPPL) with minimum 3 months service."
            }
        }

    async def search_policy(self, query: str) -> Dict[str, Any]:
        """Search the Altostrat policy handbook corpus with relevance scoring."""
        q_words = set(query.lower().replace("?", "").replace(".", "").split())
        scored_results = []
        
        for key, doc in self.knowledge_base.items():
            score = 0
            # Match specific keywords
            for kw in doc["keywords"]:
                if kw in q_words or kw in query.lower():
                    score += 5
            # Match content words
            content_words = set(doc["content"].lower().split())
            score += len(q_words.intersection(content_words))
            
            if score > 0:
                scored_results.append((score, doc))
        
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        if not scored_results:
            return {
                "status": "NOT_FOUND",
                "message": "No matching policy found in §6~§35 of the Altostrat Handbook."
            }
        
        return {
            "status": "SUCCESS",
            "results": [item[1] for item in scored_results]
        }
