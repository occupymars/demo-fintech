from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import uuid


class LoanStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    OVERDUE = "overdue"
    PAID = "paid"
    DEFAULTED = "defaulted"


class KYCStatus(str, Enum):
    NOT_STARTED = "not_started"
    INCOMPLETE = "incomplete"
    PENDING_REVIEW = "pending_review"
    VERIFIED = "verified"
    REJECTED = "rejected"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class User:
    id: str = field(default_factory=lambda: f"u_{uuid.uuid4().hex[:8]}")
    name: str = ""
    email: str = ""
    phone: str = ""
    timezone: str = "Asia/Kolkata"
    kyc_status: KYCStatus = KYCStatus.NOT_STARTED
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Loan:
    id: str = field(default_factory=lambda: f"loan_{uuid.uuid4().hex[:8]}")
    user_id: str = ""
    amount: float = 0.0
    currency: str = "INR"
    status: LoanStatus = LoanStatus.PENDING
    due_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    emi_amount: float = 0.0
    tenure_months: int = 12
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Transaction:
    id: str = field(default_factory=lambda: f"txn_{uuid.uuid4().hex[:8]}")
    user_id: str = ""
    loan_id: str = ""
    amount: float = 0.0
    currency: str = "INR"
    status: TransactionStatus = TransactionStatus.PENDING
    failure_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


# In-memory storage for demo
class Database:
    def __init__(self):
        self.users: dict[str, User] = {}
        self.loans: dict[str, Loan] = {}
        self.transactions: dict[str, Transaction] = {}

    def clear(self):
        self.users.clear()
        self.loans.clear()
        self.transactions.clear()


db = Database()
