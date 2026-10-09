from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    upload_time: datetime
    status: str
    text_snippet: Optional[str] = None

    class Config:
        from_attributes = True

class ExtractedDataSchema(BaseModel):
    borrower_name: Optional[str] = "N/A"
    loan_amount: Optional[float] = 0.0
    interest_rate: Optional[float] = 0.0
    interest_type: Optional[str] = "Fixed"
    tenure: Optional[int] = 0
    emi: Optional[float] = 0.0
    processing_fee: Optional[float] = 0.0
    processing_fee_pct: Optional[float] = 0.0
    total_interest: Optional[float] = 0.0
    total_repayment: Optional[float] = 0.0
    foreclosure_charges: Optional[str] = "Not Specified"
    late_payment_penalties: Optional[str] = "Not Specified"
    due_dates: Optional[str] = "5th of every month"

class ClauseSchema(BaseModel):
    id: Optional[int] = None
    title: str
    clause_type: str
    text_snippet: str
    risk_level: str  # HIGH_RISK, MEDIUM_RISK, LOW_RISK
    simple_explanation: str
    impact_score: float = 5.0

class FinancialCalculationResponse(BaseModel):
    doc_id: str
    loan_amount: float
    annual_interest_rate: float
    tenure_months: int
    calculated_emi: float
    total_interest_payable: float
    total_repayment_amount: float
    processing_fee: float
    processing_fee_percentage: float
    effective_apr: float
    amortization_schedule: List[Dict[str, Any]]

class AnalysisReportResponse(BaseModel):
    doc_id: str
    filename: str
    extracted_data: ExtractedDataSchema
    financial_summary: Dict[str, Any]
    detected_clauses: List[ClauseSchema]
    overall_risk_score: float
    risk_category: str
    recommendations: List[str]

class ComparisonRequest(BaseModel):
    doc_ids: List[str]

class LoanComparisonItem(BaseModel):
    doc_id: str
    filename: str
    borrower_name: str
    loan_amount: float
    interest_rate: float
    interest_type: str
    tenure_months: int
    emi: float
    processing_fee: float
    total_interest: float
    total_repayment: float
    foreclosure_charges: str
    late_penalty: str
    risk_score: float
    overall_rank: int
    pros: List[str]
    cons: List[str]

class ComparisonResponse(BaseModel):
    comparison_id: str
    timestamp: datetime
    compared_loans: List[LoanComparisonItem]
    best_option_doc_id: str
    best_option_name: str
    recommendation_reasoning: str
    lowest_cost_doc_id: str
    lowest_risk_doc_id: str

class ChatRequest(BaseModel):
    doc_ids: Optional[List[str]] = None
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence_score: float = 0.95
