# FinWise AI – Intelligent Financial Decision Support System

🧠 **AI-Powered Full-Stack Financial Document Analysis & Decision Support System**

FinWise AI helps borrowers, loan applicants, and financial analysts understand, analyze, detect contract risks, compare loan offers, and query complex financial contracts (such as loan agreements, sanction letters, and mortgage deeds).

---

## 🎯 Key Features & Modules

1. **Document Management & OCR Processing**:
   - Accept PDF, PNG, JPG, and text files.
   - Batch upload multiple financial contracts simultaneously.
   - Text cleaning, symbol normalization (INR/₹), and secure document ID generation.
   - 3 pre-loaded sample documents (HDFC Personal Loan, SBI Home Loan, Axis Auto Loan) for instant demonstration.

2. **Structured NLP Extraction**:
   - Rule-based + spaCy NLP extraction engine.
   - Returns structured JSON for:
     - `borrower_name`
     - `loan_amount`
     - `interest_rate` & `interest_type` (Fixed vs Floating)
     - `tenure_months`
     - `emi` (Equated Monthly Instalment)
     - `processing_fee` & `processing_fee_pct`
     - `total_interest` & `total_repayment`
     - `foreclosure_charges`
     - `late_payment_penalties`
     - `due_dates`

3. **Financial Calculations Engine**:
   - Computes standard financial formulas:
     $$E = P \cdot r \cdot \frac{(1+r)^n}{(1+r)^n - 1}$$
   - Total Interest Payable & Total Repayment Amount.
   - Effective Annual Percentage Rate (APR) including upfront administrative fees.
   - Complete 12-month to 360-month monthly amortization schedule with Principal/Interest breakdown.

4. **Clause Detection Engine & Risk Analysis**:
   - Scans text to detect and classify critical clauses:
     - Floating vs Fixed Interest Rates
     - Prepayment & Foreclosure Penalties
     - Late Payment & Penal Interest Charges
     - Mandatory Credit Shield / Loan Protection Insurance
     - Hidden Administrative & Ancillary Charges
   - Translates complex legalese into **simple explanations for non-finance users**.
   - Calculates contract risk rating (1.0 to 10.0 scale) and outputs actionable recommendations.

5. **Multi-Loan Side-by-Side Comparison Engine**:
   - Compare multiple loan offers side-by-side.
   - Evaluates total cost, interest exposure, fees, and contract risk.
   - Composite ranking algorithm identifying:
     - **Best Overall Option** (Optimal cost & risk balance)
     - **Lowest Cost Option**
     - **Lowest Risk Option**
   - Renders advantage/disadvantage breakdown for each contract.

6. **RAG-Based AI Q&A Copilot**:
   - Context-grounded retrieval-augmented generation (RAG).
   - Vector chunking & index lookup.
   - Grounded answers strictly based on uploaded contracts with verified text citations.

7. **PDF Report Export**:
   - Generate & download professional PDF decision support reports.

---

## 🏗️ Technical Architecture

```
                               ┌──────────────────────────────────────────────┐
                               │              React Frontend                  │
                               │  - Modern Dark Mode Theme (Vite + React)     │
                               │  - Interactive Calculator & Amortization     │
                               │  - Comparison Matrix & RAG Chat Copilot      │
                               └──────────────────────┬───────────────────────┘
                                                      │ REST API
                                                      ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────┐
 │                                   FastAPI Backend Server                                │
 │  ┌──────────────────┬──────────────────┬──────────────────┬──────────────────────────┐  │
 │  │ File Management  │  OCR & Cleaning  │  NLP Extractor   │  Financial Math Engine   │  │
 │  ├──────────────────┼──────────────────┼──────────────────┼──────────────────────────┤  │
 │  │ Clause Classifier│ Comparison Engine│ RAG Vector Index │ PDF Report Generator     │  │
 │  └──────────────────┴──────────────────┴──────────────────┴──────────────────────────┘  │
 └─────────────────────────┬──────────────────────────┬────────────────────────────────────┘
                           │                          │
                           ▼                          ▼
               ┌───────────────────────┐  ┌───────────────────────┐
               │ SQLite / PostgreSQL   │  │ Document Embeddings   │
               │ (Metadata & Entities) │  │ & RAG Vector Store    │
               └───────────────────────┘  └───────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. Backend Setup (FastAPI)

```bash
cd backend
pip install -r requirements.txt
python create_samples.py
uvicorn main:app --reload --port 8000
```
- API Documentation available at: `http://localhost:8000/docs`

### 2. Frontend Setup (React)

```bash
cd frontend
npm install
npm run dev
```
- Open application at: `http://localhost:3000`

---

## 🐳 Docker Deployment

To build and launch the complete full-stack environment in Docker:

```bash
docker-compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

---

## 🧪 Verification & Testing

Run the automated backend test suite:

```bash
python backend/test_system.py
```

---

## 💡 LLM Prompt Templates Used

```text
You are FinWise AI, an expert financial advisor explaining complex loan agreements to a non-finance user.
Explain the following clause in plain English, highlighting any potential financial risks or unexpected costs:

Clause Snippet: "{clause_text}"

Requirements:
- Keep the language simple and accessible.
- Clearly state if the clause presents HIGH, MEDIUM, or LOW risk.
- Provide a concrete numerical example if applicable.
```
