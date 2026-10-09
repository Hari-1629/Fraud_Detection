import os
import uuid
import logging
from typing import List, Optional
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, BackgroundTasks
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from fastapi.responses import Response, FileResponse
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from database import engine, get_db, Base
import models
import schemas
from services.ocr_service import extract_text_from_file
from services.nlp_extractor import extract_financial_data
from services.financial_calculator import calculate_loan_financials
from services.clause_detector import analyze_clauses, compute_overall_risk_score
from services.comparison_engine import compare_loans
from services.rag_engine import index_document, query_rag_system
from services.report_generator import generate_pdf_report

# Initialize DB tables
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("finwise-backend")

app = FastAPI(
    title="FinWise AI Backend",
    description="Intelligent Financial Decision Support System API",
    version="1.0.0"
)

# Enable CORS for React frontend and deployed origins (Vercel, localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fine-wise-ai-financial-decision-sup.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "FinWise AI - Intelligent Financial Decision Support System",
        "version": "1.0.0"
    }


@app.post("/api/upload", response_model=List[schemas.DocumentResponse])
async def upload_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Accepts single or multiple PDF/image documents, stores them securely,
    generates unique document IDs, and triggers processing.
    """
    uploaded_docs = []

    for file in files:
        doc_id = f"doc_{uuid.uuid4().hex[:10]}"
        file_ext = os.path.splitext(file.filename)[1].lower()
        if not file_ext:
            file_ext = ".pdf"

        saved_path = os.path.join(UPLOAD_DIR, f"{doc_id}{file_ext}")

        with open(saved_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Process OCR & Text Extraction synchronously for fast feedback
        text_content = extract_text_from_file(saved_path)

        doc_record = models.Document(
            id=doc_id,
            filename=file.filename,
            file_path=saved_path,
            file_type=file_ext.replace(".", "").upper(),
            status="PROCESSED" if text_content else "UPLOADED",
            text_content=text_content
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)

        # Perform NLP Extraction and save to ExtractedData table
        extracted = extract_financial_data(text_content, file.filename)
        ext_record = models.ExtractedData(
            doc_id=doc_id,
            borrower_name=extracted.get("borrower_name"),
            loan_amount=extracted.get("loan_amount"),
            interest_rate=extracted.get("interest_rate"),
            interest_type=extracted.get("interest_type"),
            tenure_months=extracted.get("tenure"),
            emi=extracted.get("emi"),
            processing_fee=extracted.get("processing_fee"),
            processing_fee_pct=extracted.get("processing_fee_pct"),
            total_interest=extracted.get("total_interest"),
            total_repayment=extracted.get("total_repayment"),
            foreclosure_charges=extracted.get("foreclosure_charges"),
            late_penalty=extracted.get("late_payment_penalties"),
            due_dates=extracted.get("due_dates"),
            raw_json=extracted
        )
        db.add(ext_record)

        # Detect Clauses and save
        clauses_list = analyze_clauses(text_content)
        for c in clauses_list:
            clause_record = models.Clause(
                doc_id=doc_id,
                title=c["title"],
                clause_type=c["clause_type"],
                text_snippet=c["text_snippet"],
                risk_level=c["risk_level"],
                simple_explanation=c["simple_explanation"],
                impact_score=c.get("impact_score", 5.0)
            )
            db.add(clause_record)

        db.commit()

        # Index in RAG engine
        index_document(doc_id, file.filename, text_content)

        uploaded_docs.append(doc_record)

    return [
        schemas.DocumentResponse(
            id=d.id,
            filename=d.filename,
            file_type=d.file_type,
            upload_time=d.upload_time,
            status=d.status,
            text_snippet=d.text_content[:200] if d.text_content else ""
        ) for d in uploaded_docs
    ]


@app.get("/api/documents", response_model=List[schemas.DocumentResponse])
def get_all_documents(db: Session = Depends(get_db)):
    docs = db.query(models.Document).order_by(models.Document.upload_time.desc()).all()
    return [
        schemas.DocumentResponse(
            id=d.id,
            filename=d.filename,
            file_type=d.file_type,
            upload_time=d.upload_time,
            status=d.status,
            text_snippet=d.text_content[:200] if d.text_content else ""
        ) for d in docs
    ]


@app.get("/api/documents/{doc_id}")
def get_document_details(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    ext = db.query(models.ExtractedData).filter(models.ExtractedData.doc_id == doc_id).first()
    clauses = db.query(models.Clause).filter(models.Clause.doc_id == doc_id).all()

    clauses_dicts = [{
        "title": c.title,
        "clause_type": c.clause_type,
        "text_snippet": c.text_snippet,
        "risk_level": c.risk_level,
        "simple_explanation": c.simple_explanation,
        "impact_score": c.impact_score
    } for c in clauses]

    risk_info = compute_overall_risk_score(clauses_dicts)

    return {
        "doc_id": doc.id,
        "filename": doc.filename,
        "upload_time": doc.upload_time,
        "status": doc.status,
        "extracted_data": {
            "borrower_name": ext.borrower_name if ext else "N/A",
            "loan_amount": ext.loan_amount if ext else 0.0,
            "interest_rate": ext.interest_rate if ext else 0.0,
            "interest_type": ext.interest_type if ext else "Fixed",
            "tenure": ext.tenure_months if ext else 0,
            "emi": ext.emi if ext else 0.0,
            "processing_fee": ext.processing_fee if ext else 0.0,
            "processing_fee_pct": ext.processing_fee_pct if ext else 0.0,
            "total_interest": ext.total_interest if ext else 0.0,
            "total_repayment": ext.total_repayment if ext else 0.0,
            "foreclosure_charges": ext.foreclosure_charges if ext else "",
            "late_payment_penalties": ext.late_penalty if ext else "",
            "due_dates": ext.due_dates if ext else ""
        },
        "clauses": clauses_dicts,
        "risk_analysis": risk_info,
        "text_content": doc.text_content
    }


@app.get("/api/calculate/{doc_id}", response_model=schemas.FinancialCalculationResponse)
def calculate_doc_financials(doc_id: str, db: Session = Depends(get_db)):
    ext = db.query(models.ExtractedData).filter(models.ExtractedData.doc_id == doc_id).first()
    if not ext:
        raise HTTPException(status_code=404, detail="Extracted data for document not found")

    result = calculate_loan_financials(
        loan_amount=ext.loan_amount or 500000.0,
        annual_interest_rate=ext.interest_rate or 10.5,
        tenure_months=ext.tenure_months or 60,
        processing_fee=ext.processing_fee or 2500.0,
        emi_override=ext.emi or 0.0
    )

    return schemas.FinancialCalculationResponse(
        doc_id=doc_id,
        loan_amount=result["loan_amount"],
        annual_interest_rate=result["annual_interest_rate"],
        tenure_months=result["tenure_months"],
        calculated_emi=result["calculated_emi"],
        total_interest_payable=result["total_interest_payable"],
        total_repayment_amount=result["total_repayment_amount"],
        processing_fee=result["processing_fee"],
        processing_fee_percentage=result["processing_fee_percentage"],
        effective_apr=result["effective_apr"],
        amortization_schedule=result["amortization_schedule"]
    )


@app.get("/api/clauses/{doc_id}")
def get_doc_clauses(doc_id: str, db: Session = Depends(get_db)):
    clauses = db.query(models.Clause).filter(models.Clause.doc_id == doc_id).all()
    clauses_dicts = [{
        "title": c.title,
        "clause_type": c.clause_type,
        "text_snippet": c.text_snippet,
        "risk_level": c.risk_level,
        "simple_explanation": c.simple_explanation,
        "impact_score": c.impact_score
    } for c in clauses]

    risk_info = compute_overall_risk_score(clauses_dicts)

    return {
        "doc_id": doc_id,
        "clauses": clauses_dicts,
        "overall_risk_score": risk_info["risk_score"],
        "risk_category": risk_info["risk_category"],
        "recommendations": risk_info["recommendations"]
    }


@app.post("/api/compare", response_model=schemas.ComparisonResponse)
def compare_loan_documents(req: schemas.ComparisonRequest, db: Session = Depends(get_db)):
    if not req.doc_ids:
        # If no specific doc IDs passed, fetch all processed documents
        docs = db.query(models.Document).all()
        req.doc_ids = [d.id for d in docs]

    if not req.doc_ids:
        raise HTTPException(status_code=400, detail="No documents available to compare.")

    loans_data = []
    for d_id in req.doc_ids:
        doc = db.query(models.Document).filter(models.Document.id == d_id).first()
        ext = db.query(models.ExtractedData).filter(models.ExtractedData.doc_id == d_id).first()
        clauses = db.query(models.Clause).filter(models.Clause.doc_id == d_id).all()
        clauses_dicts = [{"title": c.title, "risk_level": c.risk_level, "impact_score": c.impact_score} for c in clauses]
        risk_info = compute_overall_risk_score(clauses_dicts)

        if doc and ext:
            loans_data.append({
                "doc_id": doc.id,
                "filename": doc.filename,
                "extracted_data": {
                    "borrower_name": ext.borrower_name,
                    "loan_amount": ext.loan_amount,
                    "interest_rate": ext.interest_rate,
                    "interest_type": ext.interest_type,
                    "tenure": ext.tenure_months,
                    "emi": ext.emi,
                    "processing_fee": ext.processing_fee,
                    "total_interest": ext.total_interest,
                    "total_repayment": ext.total_repayment,
                    "foreclosure_charges": ext.foreclosure_charges,
                    "late_payment_penalties": ext.late_penalty
                },
                "risk_analysis": risk_info
            })

    if not loans_data:
        raise HTTPException(status_code=404, detail="No extracted loan data found for comparison.")

    res = compare_loans(loans_data)
    return res


@app.post("/api/chat", response_model=schemas.ChatResponse)
def rag_chat(req: schemas.ChatRequest):
    res = query_rag_system(query=req.query, doc_ids=req.doc_ids)
    return schemas.ChatResponse(
        answer=res["answer"],
        sources=res["sources"],
        confidence_score=res["confidence_score"]
    )


@app.get("/api/report/{doc_id}/pdf")
def export_pdf_report(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    ext = db.query(models.ExtractedData).filter(models.ExtractedData.doc_id == doc_id).first()
    clauses = db.query(models.Clause).filter(models.Clause.doc_id == doc_id).all()

    if not doc or not ext:
        raise HTTPException(status_code=404, detail="Document not found.")

    clauses_dicts = [{
        "title": c.title,
        "clause_type": c.clause_type,
        "text_snippet": c.text_snippet,
        "risk_level": c.risk_level,
        "simple_explanation": c.simple_explanation,
        "impact_score": c.impact_score
    } for c in clauses]

    risk_info = compute_overall_risk_score(clauses_dicts)

    doc_data = {
        "doc_id": doc.id,
        "filename": doc.filename,
        "borrower_name": ext.borrower_name,
        "loan_amount": ext.loan_amount,
        "interest_rate": ext.interest_rate,
        "interest_type": ext.interest_type,
        "tenure": ext.tenure_months,
        "emi": ext.emi,
        "processing_fee": ext.processing_fee,
        "total_interest": ext.total_interest,
        "total_repayment": ext.total_repayment
    }

    pdf_bytes = generate_pdf_report(doc_data, clauses_dicts, risk_info)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=FinWise_Report_{doc_id}.pdf"}
    )


@app.post("/api/load-samples")
def load_sample_documents(db: Session = Depends(get_db)):
    """
    Auto-populates 3 sample loan agreements for instant demo testing.
    """
    sample_dir = os.path.join(os.path.dirname(__file__), "sample_docs")
    sample_files = ["hdfc_personal_loan.pdf", "sbi_home_loan.pdf", "axis_car_loan.pdf"]

    created_docs = []
    for s_file in sample_files:
        s_path = os.path.join(sample_dir, s_file)
        if not os.path.exists(s_path):
            continue

        doc_id = f"sample_{s_file.replace('.pdf', '')}"
        text_content = extract_text_from_file(s_path)

        # Check if already in DB
        existing = db.query(models.Document).filter(models.Document.id == doc_id).first()
        if existing:
            index_document(doc_id, s_file, existing.text_content or text_content)
            created_docs.append(existing.id)
            continue

        doc_record = models.Document(
            id=doc_id,
            filename=s_file,
            file_path=s_path,
            file_type="PDF",
            status="PROCESSED",
            text_content=text_content
        )
        db.add(doc_record)
        db.commit()

        extracted = extract_financial_data(text_content, s_file)
        ext_record = models.ExtractedData(
            doc_id=doc_id,
            borrower_name=extracted.get("borrower_name"),
            loan_amount=extracted.get("loan_amount"),
            interest_rate=extracted.get("interest_rate"),
            interest_type=extracted.get("interest_type"),
            tenure_months=extracted.get("tenure"),
            emi=extracted.get("emi"),
            processing_fee=extracted.get("processing_fee"),
            processing_fee_pct=extracted.get("processing_fee_pct"),
            total_interest=extracted.get("total_interest"),
            total_repayment=extracted.get("total_repayment"),
            foreclosure_charges=extracted.get("foreclosure_charges"),
            late_penalty=extracted.get("late_payment_penalties"),
            due_dates=extracted.get("due_dates"),
            raw_json=extracted
        )
        db.add(ext_record)

        clauses_list = analyze_clauses(text_content)
        for c in clauses_list:
            clause_record = models.Clause(
                doc_id=doc_id,
                title=c["title"],
                clause_type=c["clause_type"],
                text_snippet=c["text_snippet"],
                risk_level=c["risk_level"],
                simple_explanation=c["simple_explanation"],
                impact_score=c.get("impact_score", 5.0)
            )
            db.add(clause_record)

        db.commit()
        index_document(doc_id, s_file, text_content)
        created_docs.append(doc_id)

    return {"message": "Sample documents loaded successfully!", "document_ids": created_docs}


if __name__ == "__main__":
    # pyrefly: ignore [missing-import]
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
