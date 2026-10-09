import re
from typing import List, Dict, Any

def analyze_clauses(text: str) -> List[Dict[str, Any]]:
    """
    Scans loan contract text to classify financial clauses, flag hidden risks,
    and generate plain-language explanations for non-expert borrowers.
    """
    detected_clauses = []

    # 1. Floating Rate Clause Detection
    if re.search(r'(?i)(?:floating|variable|reset|mclr|repo\s*rate|benchmark\s*rate)', text):
        detected_clauses.append({
            "title": "Floating Interest Rate Clause",
            "clause_type": "Interest Rate Structure",
            "text_snippet": _extract_matching_snippet(text, r'(?i)(?:floating|variable|reset|mclr|repo\s*rate)[^\.\n]+'),
            "risk_level": "MEDIUM_RISK",
            "impact_score": 6.5,
            "simple_explanation": "Your interest rate is NOT fixed. It will fluctuate whenever central bank repo rates or bank benchmark rates change. This means your monthly EMI could increase unexpectedly over time."
        })
    else:
        detected_clauses.append({
            "title": "Fixed Interest Rate Structure",
            "clause_type": "Interest Rate Structure",
            "text_snippet": "Interest rate is fixed for the entire duration of the loan tenure.",
            "risk_level": "LOW_RISK",
            "impact_score": 2.0,
            "simple_explanation": "Your interest rate and monthly EMI will stay 100% constant throughout the entire loan tenure."
        })

    # 2. Foreclosure / Prepayment Penalty
    if re.search(r'(?i)(?:foreclosure|prepayment|early\s*settlement|early\s*closure)\s*(?:charge|penalty|fee)', text):
        snippet = _extract_matching_snippet(text, r'(?i)(?:foreclosure|prepayment|early\s*settlement)[^\.\n]+')
        risk = "HIGH_RISK" if "penalty" in snippet.lower() or "3%" in snippet or "4%" in snippet else "MEDIUM_RISK"
        detected_clauses.append({
            "title": "Prepayment & Foreclosure Penalty",
            "clause_type": "Foreclosure Conditions",
            "text_snippet": snippet or "Borrower will incur a foreclosure fee of 3% on outstanding balance if loan is closed prior to maturity.",
            "risk_level": risk,
            "impact_score": 8.0 if risk == "HIGH_RISK" else 5.5,
            "simple_explanation": "If you win a bonus or get extra cash and want to pay off your loan early, the bank will charge you a penalty fee (usually 2% to 4%) on your remaining principal."
        })

    # 3. Late Payment Penalty & Penal Interest
    if re.search(r'(?i)(?:late\s*payment|overdue|default\s*interest|penal\s*interest)', text):
        snippet = _extract_matching_snippet(text, r'(?i)(?:late\s*payment|overdue|penal\s*interest)[^\.\n]+')
        detected_clauses.append({
            "title": "Overdue & Penal Interest Clause",
            "clause_type": "Late Payment Penalty",
            "text_snippet": snippet or "Penal interest of 2% per month will be levied on overdue instalments.",
            "risk_level": "HIGH_RISK",
            "impact_score": 8.5,
            "simple_explanation": "Missing an EMI due date triggers extra penal interest (typically 24% annual rate) compounded monthly on the unpaid balance, plus bounce fees."
        })

    # 4. Mandatory Insurance Requirement
    if re.search(r'(?i)(?:insurance|credit\s*shield|loan\s*protector|property\s*insurance)', text):
        snippet = _extract_matching_snippet(text, r'(?i)(?:insurance|credit\s*shield|protector)[^\.\n]+')
        detected_clauses.append({
            "title": "Mandatory Insurance Purchase",
            "clause_type": "Insurance Requirement",
            "text_snippet": snippet or "Borrower must purchase loan protection insurance policy mandated by the lender.",
            "risk_level": "MEDIUM_RISK",
            "impact_score": 5.0,
            "simple_explanation": "The lender requires you to buy a credit shield or loan insurance policy. Premium cost is often added directly onto your principal loan amount."
        })

    # 5. Hidden Charges / Administrative Fees
    if re.search(r'(?i)(?:administrative|legal|valuation|documentation|cheque\s*bounce|notice\s*charge)', text):
        snippet = _extract_matching_snippet(text, r'(?i)(?:administrative|legal|valuation|documentation|bounce)[^\.\n]+')
        detected_clauses.append({
            "title": "Administrative & Ancillary Charges",
            "clause_type": "Hidden Charges",
            "text_snippet": snippet or "Documentation, legal verification, and cheque bounce charges applicable as per fee schedule.",
            "risk_level": "MEDIUM_RISK",
            "impact_score": 6.0,
            "simple_explanation": "In addition to processing fees, you may be billed for legal verification, valuation fees, and cheque bounce fees ranging from ₹500 to ₹5,000."
        })

    return detected_clauses

def compute_overall_risk_score(clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes an overall aggregate risk score from 1.0 (Very Low Risk) to 10.0 (High Risk).
    """
    if not clauses:
        return {"risk_score": 3.0, "risk_category": "LOW_RISK", "recommendations": ["Review basic agreement terms."]}

    total_impact = sum(c.get("impact_score", 5.0) for c in clauses)
    avg_impact = round(total_impact / len(clauses), 1)

    if avg_impact >= 7.0:
        category = "HIGH_RISK"
    elif avg_impact >= 4.5:
        category = "MEDIUM_RISK"
    else:
        category = "LOW_RISK"

    recommendations = []
    for c in clauses:
        if c.get("risk_level") == "HIGH_RISK":
            if "Foreclosure" in c["title"]:
                recommendations.append("Negotiate a zero foreclosure penalty clause if you plan to repay early.")
            elif "Penal" in c["title"]:
                recommendations.append("Set up auto-debit (NACH/ECS) 3 days prior to due date to prevent penal interest fees.")
        elif "Floating" in c["title"]:
            recommendations.append("Ensure your household budget can accommodate a 1.5% to 2.0% potential spike in interest rates.")

    if not recommendations:
        recommendations.append("This agreement aligns with standard consumer banking regulations.")

    return {
        "risk_score": avg_impact,
        "risk_category": category,
        "recommendations": recommendations
    }

def _extract_matching_snippet(text: str, pattern: str) -> str:
    match = re.search(pattern, text)
    if match:
        snippet = match.group(0).strip()
        if len(snippet) > 160:
            snippet = snippet[:157] + "..."
        return snippet
    return "Clause identified in document text."
