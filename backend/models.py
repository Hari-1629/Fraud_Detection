import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="UPLOADED") # UPLOADED, PROCESSED, ERROR
    text_content = Column(Text, nullable=True)

    extracted_data = relationship("ExtractedData", back_populates="document", uselist=False, cascade="all, delete-orphan")
    clauses = relationship("Clause", back_populates="document", cascade="all, delete-orphan")

class ExtractedData(Base):
    __tablename__ = "extracted_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, ForeignKey("documents.id"), nullable=False, unique=True)
    borrower_name = Column(String, nullable=True)
    loan_amount = Column(Float, nullable=True)
    interest_rate = Column(Float, nullable=True)
    interest_type = Column(String, default="Fixed") # Fixed or Floating
    tenure_months = Column(Integer, nullable=True)
    emi = Column(Float, nullable=True)
    processing_fee = Column(Float, nullable=True)
    processing_fee_pct = Column(Float, nullable=True)
    total_interest = Column(Float, nullable=True)
    total_repayment = Column(Float, nullable=True)
    foreclosure_charges = Column(String, nullable=True)
    late_penalty = Column(String, nullable=True)
    due_dates = Column(String, nullable=True)
    raw_json = Column(JSON, nullable=True)

    document = relationship("Document", back_populates="extracted_data")

class Clause(Base):
    __tablename__ = "clauses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, ForeignKey("documents.id"), nullable=False)
    title = Column(String, nullable=False)
    clause_type = Column(String, nullable=False) # Interest, Penalty, Prepayment, Insurance, Hidden
    text_snippet = Column(Text, nullable=False)
    risk_level = Column(String, nullable=False) # HIGH_RISK, MEDIUM_RISK, LOW_RISK
    simple_explanation = Column(Text, nullable=False)
    impact_score = Column(Float, default=5.0)

    document = relationship("Document", back_populates="clauses")

class ComparisonReport(Base):
    __tablename__ = "comparison_reports"

    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    comparison_json = Column(JSON, nullable=False)
