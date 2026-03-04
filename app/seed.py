"""Seed database with demo data."""

import random
from datetime import datetime, timedelta
from app.models import db, User, Loan, Transaction, LoanStatus, KYCStatus, TransactionStatus

# Sample users
USERS = [
    {"name": "Rajesh Kumar", "email": "rajesh@example.com", "kyc": KYCStatus.VERIFIED},
    {"name": "Priya Sharma", "email": "priya@example.com", "kyc": KYCStatus.INCOMPLETE},
    {"name": "Amit Patel", "email": "amit@example.com", "kyc": KYCStatus.VERIFIED},
    {"name": "Sneha Gupta", "email": "sneha@example.com", "kyc": KYCStatus.NOT_STARTED},
    {"name": "Vikram Singh", "email": "vikram@example.com", "kyc": KYCStatus.PENDING_REVIEW},
]

# Loan configurations
LOAN_CONFIGS = [
    {"amount": 50000, "tenure": 12, "emi": 4500},
    {"amount": 100000, "tenure": 24, "emi": 4700},
    {"amount": 200000, "tenure": 36, "emi": 6500},
    {"amount": 500000, "tenure": 48, "emi": 12000},
]


def seed_database():
    """Seed the database with demo data."""
    print("Seeding database...")
    db.clear()

    # Create users
    users = []
    for i, user_data in enumerate(USERS):
        user = User(
            name=user_data["name"],
            email=user_data["email"],
            phone=f"+91987654321{i}",
            timezone="Asia/Kolkata",
            kyc_status=user_data["kyc"],
            created_at=datetime.now() - timedelta(days=random.randint(30, 180)),
        )
        users.append(user)
        db.users[user.id] = user

    # Create loans for verified users
    for user in users:
        if user.kyc_status == KYCStatus.VERIFIED:
            num_loans = random.randint(1, 2)
            for _ in range(num_loans):
                config = random.choice(LOAN_CONFIGS)
                status = random.choice([LoanStatus.ACTIVE, LoanStatus.OVERDUE, LoanStatus.ACTIVE])
                due_date = datetime.now() + timedelta(days=random.randint(-10, 30))

                loan = Loan(
                    user_id=user.id,
                    amount=config["amount"],
                    currency="INR",
                    status=status,
                    due_date=due_date,
                    emi_amount=config["emi"],
                    tenure_months=config["tenure"],
                    created_at=datetime.now() - timedelta(days=random.randint(30, 90)),
                )
                db.loans[loan.id] = loan

                # Create some transactions for active loans
                if random.random() > 0.5:
                    tx_status = random.choice([TransactionStatus.SUCCESS, TransactionStatus.FAILED])
                    transaction = Transaction(
                        user_id=user.id,
                        loan_id=loan.id,
                        amount=config["emi"],
                        currency="INR",
                        status=tx_status,
                        failure_reason="insufficient_funds" if tx_status == TransactionStatus.FAILED else None,
                        created_at=datetime.now() - timedelta(days=random.randint(1, 30)),
                    )
                    db.transactions[transaction.id] = transaction

    print(f"Seeded {len(db.users)} users, {len(db.loans)} loans, {len(db.transactions)} transactions")
