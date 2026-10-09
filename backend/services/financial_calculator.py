import math
from typing import Dict, Any, List

def calculate_loan_financials(
    loan_amount: float,
    annual_interest_rate: float,
    tenure_months: int,
    processing_fee: float = 0.0,
    emi_override: float = 0.0
) -> Dict[str, Any]:
    """
    Computes standard financial math for loans:
    - EMI (Equated Monthly Installment)
    - Total Interest Payable
    - Total Repayment Amount
    - Effective Annual Percentage Rate (APR)
    - Complete monthly amortization schedule
    """
    if loan_amount <= 0 or tenure_months <= 0:
        return {
            "loan_amount": loan_amount,
            "annual_interest_rate": annual_interest_rate,
            "tenure_months": tenure_months,
            "calculated_emi": 0.0,
            "total_interest_payable": 0.0,
            "total_repayment_amount": 0.0,
            "processing_fee": processing_fee,
            "processing_fee_percentage": 0.0,
            "effective_apr": annual_interest_rate,
            "amortization_schedule": []
        }

    monthly_rate = (annual_interest_rate / 100) / 12

    if emi_override and emi_override > 0:
        emi = emi_override
    else:
        if monthly_rate > 0:
            emi = loan_amount * monthly_rate * math.pow(1 + monthly_rate, tenure_months) / (math.pow(1 + monthly_rate, tenure_months) - 1)
        else:
            emi = loan_amount / tenure_months

    emi = round(emi, 2)
    total_repayment = round(emi * tenure_months, 2)
    total_interest = round(total_repayment - loan_amount, 2)
    
    processing_fee_pct = round((processing_fee / loan_amount) * 100, 2) if loan_amount > 0 else 0.0
    
    # Effective APR estimation = Nominal Rate + (Upfront Fee % / Tenure in years)
    tenure_years = tenure_months / 12.0
    effective_apr = round(annual_interest_rate + (processing_fee_pct / tenure_years if tenure_years > 0 else 0.0), 2)

    schedule = []
    balance = loan_amount
    for month in range(1, tenure_months + 1):
        interest_for_month = round(balance * monthly_rate, 2)
        principal_for_month = round(emi - interest_for_month, 2)
        if month == tenure_months:
            principal_for_month = round(balance, 2)
            emi_actual = round(principal_for_month + interest_for_month, 2)
            balance = 0.0
        else:
            balance = round(balance - principal_for_month, 2)
            emi_actual = emi

        schedule.append({
            "month": month,
            "installment": emi_actual,
            "principal_component": principal_for_month,
            "interest_component": interest_for_month,
            "remaining_balance": max(0.0, balance)
        })

    return {
        "loan_amount": loan_amount,
        "annual_interest_rate": annual_interest_rate,
        "tenure_months": tenure_months,
        "calculated_emi": emi,
        "total_interest_payable": total_interest,
        "total_repayment_amount": total_repayment,
        "processing_fee": processing_fee,
        "processing_fee_percentage": processing_fee_pct,
        "effective_apr": effective_apr,
        "amortization_schedule": schedule
    }
