# Demo Fintech - LendFlow

A demo fintech lending app showcasing [Fourbyfour](https://fourbyfour.dev) integration.

## Overview

LendFlow is a simulated lending platform that demonstrates how to integrate Fourbyfour for automated revenue workflows:

- **Payment Reminders** - Trigger `payment.due` when EMI is due/overdue
- **KYC Completion** - Trigger `kyc.incomplete` to nudge users to complete verification
- **Failed Payment Recovery** - Trigger `transaction.failed` to recover failed payments
- **Reactivation** - Trigger `account.dormant` to re-engage inactive users

## Quick Start

### 1. Install dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e .
```

### 2. Configure Fourbyfour

```bash
cp .env.example .env
```

Edit `.env` with your Fourbyfour credentials:

```env
FOURBYFOUR_API_KEY=fbf_live_xxx
FOURBYFOUR_PROJECT_ID=proj_xxx
FOURBYFOUR_BASE_URL=https://api.fourbyfour.dev
```

### 3. Seed demo data

```bash
python scripts/seed.py
```

### 4. Run the app

```bash
uvicorn app.main:app --reload
```

Open http://localhost:8000 to view the dashboard.

## Triggering Events

### Via UI

1. Go to the dashboard at http://localhost:8000
2. Click on a user to view their details
3. Click any of the event trigger buttons:
   - **Payment Due** - Sends `payment.due` event
   - **KYC Incomplete** - Sends `kyc.incomplete` event
   - **Transaction Failed** - Sends `transaction.failed` event
   - **Mark Dormant** - Sends `account.dormant` event

### Via API

```bash
# Payment due
curl -X POST "http://localhost:8000/api/events/payment-due?user_id=u_123&loan_id=loan_456&amount=5000"

# KYC incomplete
curl -X POST "http://localhost:8000/api/events/kyc-incomplete?user_id=u_123"

# Transaction failed
curl -X POST "http://localhost:8000/api/events/transaction-failed?user_id=u_123&transaction_id=txn_789&loan_id=loan_456&amount=5000&failure_reason=insufficient_funds"
```

## Load Testing

Run the load test script to benchmark event throughput:

```bash
# Default: 1000 events, 50 concurrent
python scripts/load_test.py

# Custom configuration
python scripts/load_test.py --events 5000 --concurrency 100

# Different event type
python scripts/load_test.py --event-type transaction.failed
```

### Sample Output

```
============================================================
Benchmark Results
============================================================
Total Events:     1000
Successful:       1000 (100.0%)
Failed:           0 (0.0%)
Duration:         12.34 seconds
============================================================
Throughput:       81.0 events/second
============================================================
Latency (avg):    45.2 ms
Latency (p50):    42.1 ms
Latency (p95):    78.3 ms
Latency (p99):    112.5 ms
============================================================
```

## Project Structure

```
demo-fintech/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app with routes
│   ├── config.py        # Configuration from env
│   ├── models.py        # Data models (User, Loan, Transaction)
│   └── fbf.py           # Fourbyfour SDK wrapper
├── templates/
│   ├── base.html        # Base template
│   ├── dashboard.html   # Main dashboard
│   └── user_detail.html # User detail + event triggers
├── scripts/
│   ├── seed.py          # Seed fake data
│   └── load_test.py     # Load testing script
├── static/              # Static assets
├── .env.example         # Environment template
├── pyproject.toml       # Dependencies
└── README.md
```

## Fourbyfour Integration

This app uses the [Fourbyfour Python SDK](https://pypi.org/project/fourbyfour/):

```python
from fourbyfour import fintech

fbf = fintech(
    api_key=os.environ["FOURBYFOUR_API_KEY"],
    project_id=os.environ["FOURBYFOUR_PROJECT_ID"],
)

# Track events - triggers matching workflows
fbf.track("payment.due", {
    "user_id": "u_123",
    "loan_id": "loan_456",
    "amount": 5000,
    "currency": "INR",
    "due_date": "2025-02-28",
    "days_overdue": 5,
})

# Send user context - helps optimize delivery
fbf.notify({
    "user_id": "u_123",
    "timezone": "Asia/Kolkata",
    "preferred_channel": "sms",
})
```

## Events Reference

| Event | When to Track | Triggers |
|-------|---------------|----------|
| `payment.due` | EMI due date approaching or passed | Payment reminder workflow |
| `kyc.incomplete` | User has incomplete KYC documents | KYC completion workflow |
| `transaction.failed` | Payment attempt failed | Failed payment recovery workflow |
| `account.dormant` | User inactive for 30+ days | Reactivation workflow |

## License

MIT
