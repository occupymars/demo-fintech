#!/usr/bin/env python3
"""Seed script to populate demo data for the fintech app."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from faker import Faker
from app.models import db, User, Loan, LoanStatus, KYCStatus

fake = Faker("en_IN")  # Indian locale for realistic fintech data


def seed_users(count: int = 10) -> list[User]:
    """Create fake users."""
    users = []
    kyc_statuses = [KYCStatus.VERIFIED, KYCStatus.INCOMPLETE, KYCStatus.NOT_STARTED]
    timezones = ["Asia/Kolkata", "Asia/Mumbai", "Asia/Chennai"]

    for i in range(count):
        user = User(
            name=fake.name(),
            email=fake.email(),
            phone=f"+91{fake.msisdn()[3:13]}",
            timezone=timezones[i % len(timezones)],
            kyc_status=kyc_statuses[i % len(kyc_statuses)],
            created_at=fake.date_time_between(start_date="-1y", end_date="now"),
        )
        users.append(user)
        db.users[user.id] = user
        print(f"Created user: {user.name} ({user.id})")

    return users


def seed_loans(users: list[User], loans_per_user: int = 1) -> list[Loan]:
    """Create fake loans for users."""
    loans = []
    loan_amounts = [50000, 100000, 200000, 500000, 1000000]
    tenures = [6, 12, 24, 36]
    statuses = [LoanStatus.ACTIVE, LoanStatus.ACTIVE, LoanStatus.OVERDUE]  # 2/3 active, 1/3 overdue

    for i, user in enumerate(users):
        for j in range(loans_per_user):
            amount = loan_amounts[(i + j) % len(loan_amounts)]
            tenure = tenures[(i + j) % len(tenures)]
            status = statuses[(i + j) % len(statuses)]

            # Calculate EMI (simple calculation)
            interest_rate = 0.12  # 12% annual
            monthly_rate = interest_rate / 12
            emi = amount * monthly_rate * ((1 + monthly_rate) ** tenure) / (((1 + monthly_rate) ** tenure) - 1)

            # Due date: some in the past (overdue), some in future
            if status == LoanStatus.OVERDUE:
                due_date = datetime.now() - timedelta(days=fake.random_int(min=1, max=30))
            else:
                due_date = datetime.now() + timedelta(days=fake.random_int(min=1, max=30))

            loan = Loan(
                user_id=user.id,
                amount=amount,
                currency="INR",
                status=status,
                due_date=due_date,
                emi_amount=round(emi, 2),
                tenure_months=tenure,
                created_at=fake.date_time_between(start_date="-6M", end_date="now"),
            )
            loans.append(loan)
            db.loans[loan.id] = loan
            print(f"Created loan: {loan.id} for {user.name} - INR {amount:,} ({status.value})")

    return loans


def main():
    """Main seed function."""
    print("=" * 50)
    print("Seeding demo-fintech database...")
    print("=" * 50)

    # Clear existing data
    db.clear()

    # Seed data
    users = seed_users(10)
    loans = seed_loans(users, loans_per_user=1)

    print("=" * 50)
    print(f"Seeded {len(users)} users and {len(loans)} loans")
    print("=" * 50)

    # Print summary
    print("\nSample users:")
    for user in users[:3]:
        print(f"  - {user.name} ({user.email})")

    print("\nRun the app with: uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
