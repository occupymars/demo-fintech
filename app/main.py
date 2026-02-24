"""Demo Fintech App - Showcasing Fourbyfour Integration."""

from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import config
from app.models import db, User, Loan, Transaction, LoanStatus, KYCStatus, TransactionStatus
from app import fbf

app = FastAPI(
    title="LendFlow Demo",
    description="A demo fintech lending app showcasing Fourbyfour integration",
    version="0.1.0",
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ============================================================================
# Pages
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Dashboard showing all users and loans."""
    users = list(db.users.values())
    loans = list(db.loans.values())
    transactions = list(db.transactions.values())

    # Stats
    total_users = len(users)
    active_loans = len([l for l in loans if l.status == LoanStatus.ACTIVE])
    overdue_loans = len([l for l in loans if l.status == LoanStatus.OVERDUE])
    pending_kyc = len([u for u in users if u.kyc_status == KYCStatus.INCOMPLETE])

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "users": users,
        "loans": loans,
        "transactions": transactions[-10:],  # Last 10 transactions
        "stats": {
            "total_users": total_users,
            "active_loans": active_loans,
            "overdue_loans": overdue_loans,
            "pending_kyc": pending_kyc,
        },
    })


@app.get("/users/{user_id}", response_class=HTMLResponse)
async def user_detail(request: Request, user_id: str):
    """User detail page."""
    user = db.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_loans = [l for l in db.loans.values() if l.user_id == user_id]
    user_transactions = [t for t in db.transactions.values() if t.user_id == user_id]

    return templates.TemplateResponse("user_detail.html", {
        "request": request,
        "user": user,
        "loans": user_loans,
        "transactions": user_transactions,
    })


# ============================================================================
# Actions - Trigger Fourbyfour Events
# ============================================================================

@app.post("/actions/payment-due")
async def trigger_payment_due(
    user_id: str = Form(...),
    loan_id: str = Form(...),
):
    """Trigger payment.due event for a loan."""
    user = db.users.get(user_id)
    loan = db.loans.get(loan_id)

    if not user or not loan:
        raise HTTPException(status_code=404, detail="User or loan not found")

    # Calculate days overdue
    days_overdue = max(0, (datetime.now() - loan.due_date).days)

    # Update loan status if overdue
    if days_overdue > 0:
        loan.status = LoanStatus.OVERDUE

    # Track event with Fourbyfour
    await fbf.track_payment_due(
        user_id=user_id,
        loan_id=loan_id,
        amount=loan.emi_amount,
        currency=loan.currency,
        due_date=loan.due_date.isoformat(),
        days_overdue=days_overdue,
    )

    # Send user context
    await fbf.notify_user_context(
        user_id=user_id,
        timezone=user.timezone,
        preferred_channel="sms",
    )

    return RedirectResponse(url=f"/users/{user_id}", status_code=303)


@app.post("/actions/kyc-incomplete")
async def trigger_kyc_incomplete(
    user_id: str = Form(...),
):
    """Trigger kyc.incomplete event for a user."""
    user = db.users.get(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update KYC status
    user.kyc_status = KYCStatus.INCOMPLETE

    # Track event with Fourbyfour
    await fbf.track_kyc_incomplete(
        user_id=user_id,
        missing_documents=["pan_card", "address_proof"],
        started_at=user.created_at.isoformat(),
    )

    # Send user context
    await fbf.notify_user_context(
        user_id=user_id,
        timezone=user.timezone,
        preferred_channel="email",
    )

    return RedirectResponse(url=f"/users/{user_id}", status_code=303)


@app.post("/actions/transaction-failed")
async def trigger_transaction_failed(
    user_id: str = Form(...),
    loan_id: str = Form(...),
):
    """Trigger transaction.failed event."""
    user = db.users.get(user_id)
    loan = db.loans.get(loan_id)

    if not user or not loan:
        raise HTTPException(status_code=404, detail="User or loan not found")

    # Create failed transaction
    transaction = Transaction(
        user_id=user_id,
        loan_id=loan_id,
        amount=loan.emi_amount,
        currency=loan.currency,
        status=TransactionStatus.FAILED,
        failure_reason="insufficient_funds",
    )
    db.transactions[transaction.id] = transaction

    # Track event with Fourbyfour
    await fbf.track_transaction_failed(
        user_id=user_id,
        transaction_id=transaction.id,
        loan_id=loan_id,
        amount=loan.emi_amount,
        currency=loan.currency,
        failure_reason="insufficient_funds",
        attempt_number=1,
    )

    # Send user context
    await fbf.notify_user_context(
        user_id=user_id,
        timezone=user.timezone,
        preferred_channel="sms",
    )

    return RedirectResponse(url=f"/users/{user_id}", status_code=303)


@app.post("/actions/mark-dormant")
async def trigger_account_dormant(
    user_id: str = Form(...),
):
    """Trigger account.dormant event."""
    user = db.users.get(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Calculate days inactive (simulate)
    days_inactive = 30
    last_active = datetime.now() - timedelta(days=days_inactive)

    # Track event with Fourbyfour
    await fbf.track_account_dormant(
        user_id=user_id,
        last_active_at=last_active.isoformat(),
        days_inactive=days_inactive,
    )

    # Send user context
    await fbf.notify_user_context(
        user_id=user_id,
        timezone=user.timezone,
        preferred_channel="email",
    )

    return RedirectResponse(url=f"/users/{user_id}", status_code=303)


# ============================================================================
# API Endpoints (for load testing)
# ============================================================================

@app.post("/api/events/payment-due")
async def api_payment_due(
    user_id: str,
    loan_id: str,
    amount: float,
    currency: str = "INR",
    due_date: str = None,
    days_overdue: int = 0,
):
    """API endpoint for triggering payment.due event."""
    if not due_date:
        due_date = datetime.now().isoformat()

    result = await fbf.track_payment_due(
        user_id=user_id,
        loan_id=loan_id,
        amount=amount,
        currency=currency,
        due_date=due_date,
        days_overdue=days_overdue,
    )

    return {"status": "tracked", "event": "payment.due", "result": result}


@app.post("/api/events/kyc-incomplete")
async def api_kyc_incomplete(
    user_id: str,
    missing_documents: list[str] = ["pan_card"],
    started_at: str = None,
):
    """API endpoint for triggering kyc.incomplete event."""
    if not started_at:
        started_at = datetime.now().isoformat()

    result = await fbf.track_kyc_incomplete(
        user_id=user_id,
        missing_documents=missing_documents,
        started_at=started_at,
    )

    return {"status": "tracked", "event": "kyc.incomplete", "result": result}


@app.post("/api/events/transaction-failed")
async def api_transaction_failed(
    user_id: str,
    transaction_id: str,
    loan_id: str,
    amount: float,
    currency: str = "INR",
    failure_reason: str = "insufficient_funds",
    attempt_number: int = 1,
):
    """API endpoint for triggering transaction.failed event."""
    result = await fbf.track_transaction_failed(
        user_id=user_id,
        transaction_id=transaction_id,
        loan_id=loan_id,
        amount=amount,
        currency=currency,
        failure_reason=failure_reason,
        attempt_number=attempt_number,
    )

    return {"status": "tracked", "event": "transaction.failed", "result": result}


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": "demo-fintech",
        "fourbyfour_configured": bool(config.FOURBYFOUR_API_KEY),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.APP_PORT)
