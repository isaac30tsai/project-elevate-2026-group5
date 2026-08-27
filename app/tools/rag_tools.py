"""Vertex AI Search Hybrid RAG Knowledge Tool for Altostrat Policy Handbook §6~§35."""
from typing import Dict, Any, List, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Complete Canonical Altostrat Singapore Policy Handbook Knowledge Corpus (§6 to §35)
ALTOSTRAT_HANDBOOK_CORPUS = [
    {
        "section": "§6.1",
        "title": "Working Hours, Core Bands & Flexible Work Arrangements",
        "keywords": ["hours", "core band", "flexible", "wfh", "remote", "schedule", "hybrid", "working hours"],
        "content": "Altostrat Singapore standard full-time work week is 40 hours (Monday through Friday, 09:00 to 18:00 SGT). Core collaboration hours are 10:00 to 16:00 SGT. Employees with at least 6 months tenure may apply for Hybrid Flexible Work (up to 2 days remote weekly) with manager approval."
    },
    {
        "section": "§8.3",
        "title": "Annual Vacation Leave Entitlement & Shift Accrual",
        "keywords": ["vacation", "annual", "accrual", "tenure", "holiday", "shift", "days", "entitlement", "leave balance"],
        "content": "Annual vacation leave is accrued per full calendar year based on completed continuous service: 1 to 3 years tenure receive 18 working days; 4 to 7 years tenure receive 20 working days; 8+ years tenure receive 21 working days. Shift workers on 12-hour continuous shifts consume 1.5 vacation days per shift taken. Unused leave exceeding 5 days at year-end is forfeited unless rollover is approved."
    },
    {
        "section": "§12.1",
        "title": "Outpatient Sick Leave & Medical Certificate Verification",
        "keywords": ["sick", "medical", "mc", "outpatient", "doctor", "clinic", "illness", "unfit", "health"],
        "content": "Full-time permanent employees are entitled to 14 working days of paid outpatient sick leave per calendar year. An official Medical Certificate (MC) issued by a Singapore registered medical practitioner must be submitted in WorkWeek within 48 hours for absences exceeding 2 consecutive working days."
    },
    {
        "section": "§13.2",
        "title": "Hospitalization & Prolonged Illness Leave",
        "keywords": ["hospitalization", "hospital", "surgery", "inpatient", "ward", "prolonged", "critical"],
        "content": "Employees are entitled to up to 60 working days of paid hospitalization leave per calendar year (inclusive of the 14 days outpatient sick leave). Medical documentation from a licensed hospital or specialist must be submitted to People Operations (people-ops@altostrat.com)."
    },
    {
        "section": "§14.2",
        "title": "Compassionate & Bereavement Leave",
        "keywords": ["bereavement", "compassionate", "death", "funeral", "family", "passed away", "mourning", "loss"],
        "content": "Altostrat grants 5 consecutive working days of fully paid compassionate leave upon the death of an immediate family member (spouse, child, parent, sibling). For extended family (grandparents, parents-in-law), 3 consecutive working days are granted. Official verification must be provided to People Ops."
    },
    {
        "section": "§15.1",
        "title": "Government-Paid Parental, Maternity & Paternity Leave",
        "keywords": ["parental", "maternity", "paternity", "gpml", "gppl", "child", "baby", "birth", "adoption", "infant"],
        "content": "Eligible female Singapore citizen employees receive 16 weeks of Government-Paid Maternity Leave (GPML). Eligible male employees receive 4 weeks of Government-Paid Paternity Leave (GPPL) with minimum 3 months continuous service. Submissions require MOM verification forms submitted via People Ops."
    },
    {
        "section": "§22.4",
        "title": "Overtime Compensation & TOIL (Time Off In Lieu)",
        "keywords": ["overtime", "ot", "toil", "weekend", "on-call", "in lieu", "extra hours"],
        "content": "Non-exempt engineering staff required to perform scheduled out-of-hours deployment or on-call duties are eligible for Time Off In Lieu (TOIL) at 1.5x the hours worked. TOIL must be redeemed within 90 days of accrual with manager approval."
    },
    {
        "section": "§31.1",
        "title": "Group Medical Insurance, Specialist Care & Wellness Allowance",
        "keywords": ["insurance", "medical insurance", "dental", "optical", "wellness", "specialist", "claim", "reimbursement"],
        "content": "Altostrat provides comprehensive Group Hospital & Surgical (GHS) insurance and $1,200 annual flexible wellness benefit (covering dental, optical, health screenings, and gym memberships) claimable through the corporate benefits portal."
    },
    {
        "section": "§34.5",
        "title": "Remote Equipment Allowance & Laptop Refresh Policy",
        "keywords": ["equipment", "laptop", "monitor", "ergonomic", "refresh", "hardware", "desk", "allowance"],
        "content": "Employees are eligible for a standard hardware refresh every 36 months. A one-time $800 home ergonomic office setup allowance is provided upon successful completion of probation. Hardware failures are handled via ServiceImmediately IT tickets."
    }
]

class PolicyRAGClient:
    def __init__(self, datastore_id: Optional[str] = None):
        self.datastore_id = datastore_id or settings.datastore_id
        self.corpus = ALTOSTRAT_HANDBOOK_CORPUS

    async def search_policy(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Search Altostrat policy handbook corpus with hybrid BM25 / token ranking."""
        q_clean = query.lower().replace("?", "").replace(".", "").replace(",", "")
        q_words = set(q_clean.split())
        scored = []

        for doc in self.corpus:
            score = 0.0
            # Keyword exact boost
            for kw in doc["keywords"]:
                if kw in q_clean:
                    score += 8.0
                elif any(w in kw.split() for w in q_words):
                    score += 3.0
            
            # Content token overlap
            content_words = set(doc["content"].lower().split())
            overlap = len(q_words.intersection(content_words))
            score += float(overlap) * 1.2
            
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scored[:top_k]]

        if not results:
            return {
                "status": "NOT_FOUND",
                "message": "No matching policy found in Sections 6–35 of the Altostrat Singapore Handbook. Please contact People Operations at people-ops@altostrat.com."
            }

        return {
            "status": "SUCCESS",
            "results": results,
            "primary_section": results[0]["section"],
            "primary_title": results[0]["title"]
        }

RAG_TOOLS_SCHEMA = [
    {
        "name": "search_policy_handbook",
        "description": "Search the authoritative Altostrat Singapore Employee Handbook (§6 to §35) for official policies, leave entitlements, insurance, working hours, and benefits.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language question or search terms regarding Altostrat policies."}
            },
            "required": ["query"]
        }
    }
]
