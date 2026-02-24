"""Fourbyfour SDK integration for fintech vertical."""

from fourbyfour import fintech
from app.config import config

# Initialize the Fourbyfour client for fintech vertical
fbf = fintech(
    api_key=config.FOURBYFOUR_API_KEY,
    project_id=config.FOURBYFOUR_PROJECT_ID,
    base_url=config.FOURBYFOUR_BASE_URL,
)


async def track_payment_due(
    user_id: str,
    loan_id: str,
    amount: float,
    currency: str,
    due_date: str,
    days_overdue: int = 0,
):
    """Track when a payment is due or overdue."""
    return fbf.track("payment.due", {
        "user_id": user_id,
        "loan_id": loan_id,
        "amount": amount,
        "currency": currency,
        "due_date": due_date,
        "days_overdue": days_overdue,
    })


async def track_kyc_incomplete(
    user_id: str,
    missing_documents: list[str],
    started_at: str,
):
    """Track when KYC is incomplete."""
    return fbf.track("kyc.incomplete", {
        "user_id": user_id,
        "missing_documents": missing_documents,
        "started_at": started_at,
    })


async def track_transaction_failed(
    user_id: str,
    transaction_id: str,
    loan_id: str,
    amount: float,
    currency: str,
    failure_reason: str,
    attempt_number: int = 1,
):
    """Track when a transaction fails."""
    return fbf.track("transaction.failed", {
        "user_id": user_id,
        "transaction_id": transaction_id,
        "loan_id": loan_id,
        "amount": amount,
        "currency": currency,
        "failure_reason": failure_reason,
        "attempt_number": attempt_number,
    })


async def track_account_dormant(
    user_id: str,
    last_active_at: str,
    days_inactive: int,
):
    """Track when an account becomes dormant."""
    return fbf.track("account.dormant", {
        "user_id": user_id,
        "last_active_at": last_active_at,
        "days_inactive": days_inactive,
    })


async def notify_user_context(
    user_id: str,
    timezone: str,
    preferred_channel: str = "sms",
    language: str = "en",
    tier: str = "standard",
):
    """Send user context to help optimize delivery."""
    return fbf.notify({
        "user_id": user_id,
        "timezone": timezone,
        "preferred_channel": preferred_channel,
        "language": language,
        "tier": tier,
    })
