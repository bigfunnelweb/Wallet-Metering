
# MeterPay — Wallet Metering Service

A backend service that provides prepaid wallet-based access to a metered API. Customers can create accounts, top up their wallets, consume API calls for a fixed fee, check their balance, and view transaction history.

## Features

- Create accounts with an initial balance of ₹0.
- Top up wallets with a specified amount.
- Consume API calls for a fixed fee of ₹0.10 per call.
- Reject requests when the wallet balance is insufficient.
- Check the current wallet balance.
- View transaction history in chronological order.
- Handle concurrent consume requests without allowing negative balances.
- Store money in integer paise to avoid floating-point errors.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pytest
- HTTPX

## Project Structure

```text
meterpay/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   └── routes.py
├── tests/
│   └── test_concurrency.py
├── requirements.txt
└── README.md
```

## Setup and Installation

### 1. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the server

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

## API Documentation

All monetary amounts in request and response bodies are expressed in paise.

₹1 = 100 paise.

The fixed consume fee is 10 paise (₹0.10).

### 1. Create Account

**POST** `/accounts`

Creates a new account with a zero balance.

Example response (201 Created):

```json
{
  "account_id": 1,
  "balance_paise": 0,
  "balance_rupees": "0.00"
}
```

### 2. Top Up Wallet

**POST** `/accounts/{account_id}/topup`

Adds the specified amount to an account.

Example request:

```json
{
  "amount_paise": 1000
}
```

Example response:

```json
{
  "account_id": 1,
  "credited_paise": 1000,
  "balance_paise": 1000
}
```

Error cases:
- 404 Not Found — account does not exist.
- 422 Unprocessable Entity — amount is missing or not positive.

### 3. Consume API

**POST** `/accounts/{account_id}/consume`

Deducts 10 paise from the account if sufficient balance is available.

Example response:

```json
{
  "account_id": 1,
  "consumed_paise": 10,
  "balance_paise": 990,
  "message": "API call successful"
}
```

Error cases:
- 404 Not Found — account does not exist.
- 409 Conflict — insufficient balance.

A rejected consume request does not change the wallet balance.

### 4. Check Balance

**GET** `/accounts/{account_id}/balance`

Returns the current wallet balance.

Example response:

```json
{
  "account_id": 1,
  "balance_paise": 990
}
```

Error cases:
- 404 Not Found — account does not exist.

### 5. Transaction History

**GET** `/accounts/{account_id}/transactions`

Returns the account's top-up and successful consume transactions in transaction ID order.

Example response:

```json
{
  "account_id": 1,
  "transactions": [
    {
      "transaction_id": 1,
      "type": "topup",
      "amount_paise": 1000,
      "balance_after_paise": 1000,
      "created_at": "2026-09-29T17:46:00"
    },
    {
      "transaction_id": 2,
      "type": "consume",
      "amount_paise": -10,
      "balance_after_paise": 990,
      "created_at": "2026-09-29T17:46:00"
    }
  ]
}
```

Error cases:
- 404 Not Found — account does not exist.

## Concurrency Test

The concurrency test sends 50 simultaneous consume requests against a wallet funded with ₹3.00.

### Run the test

Keep the API server running in one terminal. Open a second terminal and run:

```powershell
python tests/test_concurrency.py
```

### Expected results

| Metric | Expected |
|---|---:|
| Total requests | 50 |
| Successful requests | 30 |
| Rejected requests | 20 |
| Final balance | 0 paise |
| Ledger entries | 31 |

The test verifies that exactly 30 requests succeed, 20 are rejected, and the wallet balance never becomes negative.

## Design Notes

### Data Model

The application uses two tables:

- **Accounts:** Stores each account's current wallet balance in integer paise.
- **Transactions:** Stores each successful top-up or consume, including the transaction type, amount, resulting balance, and timestamp.

The transaction ledger provides a record of how the wallet balance changes over time.

### Concurrency and Atomicity

The consume operation uses a conditional database update that deducts the fee only if the account has sufficient balance.

The balance update and transaction insertion are performed in a database transaction. This prevents a successful deduction from being recorded without its corresponding ledger entry.

SQLite serializes database writes, and the conditional update prevents concurrent requests from overspending the wallet.

### Scaling to Multiple Customers and Instances

For a production deployment with many independent customers and multiple service instances, I would consider PostgreSQL.

Each wallet would be stored as a separate account row, and deductions would use atomic conditional updates or row-level locking inside a database transaction.

A durable transaction ledger, database constraints, appropriate indexes, and idempotency keys for retry-safe operations would help maintain consistency and reliability at scale.

## Scope and Limitations

- No authentication or authorization.
- No external payment gateway.
- No frontend.
- No multi-tenant infrastructure.
- SQLite is used for this assignment; a production deployment with multiple instances would benefit from a server-based database.
