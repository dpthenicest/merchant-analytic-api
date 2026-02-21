
# Transactional Analytics API

A high-performance REST API built with **FastAPI** and **PostgreSQL** designed to analyze merchant transaction data and provide actionable business intelligence through real-time analytics endpoints.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Setup and Installation](#setup-and-installation)
5. [Running the Application](#running-the-application)
6. [API Endpoints](#api-endpoints)
7. [Usage Examples](#usage-examples)
8. [Design Decisions](#design-decisions)

## Project Overview

The Transactional Analytics API processes merchant transaction data from CSV files and provides comprehensive analytics on merchant activity, product adoption, KYC conversion funnels, and transaction failure rates. The system automatically seeds data on startup and maintains data consistency through atomic database transactions.

**Technology Stack:**
- **Backend Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy (SQLAlchemy 2.0 with type hints)
- **Data Validation:** Pydantic v2
- **Migration Tool:** Alembic

## Features

- **Real-time Analytics:** Five core analytics endpoints providing merchant performance insights
- **Automated Data Pipeline:** CSV to PostgreSQL ETL with validation and error handling
- **Robust Error Handling:** Graceful handling of malformed data with detailed logging
- **Data Formatting Standards:** Monetary values (2 decimal places), percentages (1 decimal place)
- **Type Safety:** Full type hints with runtime validation
- **Database Migrations:** Version-controlled schema changes with Alembic

## Architecture

### Project Structure

```
merchant-analytic-api/
├── src/
│   ├── main.py                    # FastAPI app initialization
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py            # SQLAlchemy engine & session config
│   ├── models/
│   │   └── merchant_event.py      # SQLAlchemy ORM model
│   ├── schemas/
│   │   └── merchant_event.py      # Pydantic validation schemas
│   ├── routers/
│   │   └── analytic_routes.py     # API route definitions
│   ├── services/
│   │   └── analytics_service.py   # Business logic & queries
│   └── utils/
│       └── csv_to_psql.py         # CSV ingestion utility
├── alembic/                        # Database migrations
├── data/                           # Sample CSV files
├── pyproject.toml                  # Project dependencies
└── README.md
```

## Setup and Installation

### Prerequisites

- **Python 3.14+**
- **PostgreSQL 12+** (with UUID extension)
- **Uv** (Python package manager)
- **Git**

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dpthenicest/merchant-analytic-api.git
   cd merchant-analytic-api
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Activate Virtual Environment:**
  ```bash
    source .venv/bin/activate
  ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<database_name>
   DEBUG=False
   DATA_FOLDER_PATH=./data
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

## Running the Application

1. **Start the server:**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
   ```
   
   The API will be available at `http://localhost:8080`

2. **Interactive API documentation:**
   - Swagger UI: `http://localhost:8080/docs`
   - ReDoc: `http://localhost:8080/redoc`

3. **Data ingestion:**
   Place CSV files in the `./data` folder. On application startup:
   - Database is automatically truncated
   - All CSV files are validated and ingested
   - Server becomes available after seeding completes

## API Endpoints

All endpoints return JSON responses with appropriate HTTP status codes.

### 1. Top Merchant

**Endpoint:** `GET /api/analytics/top-merchant`

Returns the merchant with the highest total transaction volume across all products (successful transactions only).

**Response:**
```json
{
  "merchant_id": "MRC-001234",
  "total_volume": 98765432.10
}
```

### 2. Monthly Active Merchants

**Endpoint:** `GET /api/analytics/monthly-active-merchants`

Returns the count of unique merchants with at least one successful transaction per month.

**Response:**
```json
{
  "2024-01": 8234,
  "2024-02": 8456,
  "2024-12": 9102
}
```

### 3. Product Adoption

**Endpoint:** `GET /api/analytics/product-adoption`

Returns the count of unique merchants per product (sorted by count, highest first).

**Response:**
```json
{
  "POS": 15234,
  "AIRTIME": 12456,
  "BILLS": 10234
}
```

### 4. KYC Conversion Funnel

**Endpoint:** `GET /api/analytics/kyc-funnel`

Returns the KYC conversion funnel showing unique merchants at each tier (successful transactions only).

**Response:**
```json
{
  "tier_starter": 5432,
  "tier_verified": 4521,
  "tier_premium": 3890
}
```

### 5. Failure Rates

**Endpoint:** `GET /api/analytics/failure-rates`

Returns failure rate per product: `(FAILED / (SUCCESS + FAILED)) × 100`. Percentages are sorted descending.

**Response:**
```json
[
  {
    "product": "BILLS",
    "failure_rate": 5.2
  },
  {
    "product": "AIRTIME",
    "failure_rate": 4.1
  }
]
```


## Usage Examples

### Using cURL

1. **Top Merchant:**
   ```bash
   curl -X GET "http://localhost:8080/api/analytics/top-merchant" \
     -H "accept: application/json"
   ```

2. **Monthly Active Merchants:**
   ```bash
   curl -X GET "http://localhost:8080/api/analytics/monthly-active-merchants" \
     -H "accept: application/json"
   ```

3. **Product Adoption:**
   ```bash
   curl -X GET "http://localhost:8080/api/analytics/product-adoption" \
     -H "accept: application/json"
   ```

4. **KYC Conversion Funnel:**
   ```bash
   curl -X GET "http://localhost:8080/api/analytics/kyc-funnel" \
     -H "accept: application/json"
   ```

5. **Failure Rates:**
   ```bash
   curl -X GET "http://localhost:8080/api/analytics/failure-rates" \
     -H "accept: application/json"
   ```

### Using Postman

Import the endpoints into Postman and use the interactive UI for testing with automatic response formatting and syntax highlighting.

## Design Decisions

### 1. Data Validation and Null Handling

**Decision:** Most fields are optional (nullable) except `event_id` and `merchant_id`.

**Rationale:** Source CSV data contains incomplete records. Rather than discarding valid transactions with missing optional fields, we preserve the data and set missing values to `None`. This approach:
- Maximizes data retention for analytics
- Maintains data integrity for aggregations
- Follows real-world transaction processing practices

### 2. Amount Field Defaults

**Decision:** The `amount` field defaults to `0.00` (Decimal, non-nullable) instead of NULL.

**Rationale:** As per specification, non-monetary transactions default to zero rather than null. This ensures:
- Consistent numeric calculations in aggregations
- No unexpected NULL propagation in SUM() operations
- Clear distinction between "zero amount" and "missing data"

### 3. Enum Validation with Fallback

**Decision:** Fields like `status`, `channel`, `product`, and `merchant_tier` use Pydantic Literals with null fallback.

**Rationale:** Invalid or unexpected enum values are set to `None` rather than rejecting the record. This:
- Prevents data loss from schema mismatches
- Allows flexible data ingestion
- Enables future specification updates

### 4. Server Startup Blocking

**Decision:** FastAPI lifespan context manager blocks server startup until CSV seeding completes.

**Rationale:**
- Ensures database consistency: all data is loaded before serving requests
- Prevents partial analytics results during data loading
- Makes analytics state predictable and reproducible
- Simplifies deployment and monitoring (server ready = data ready)

### 5. Error Handling and Logging

**Decision:** All analytics service methods include try/catch blocks with logging.

**Rationale:** Graceful degradation of malformed data:
- Service remains available even with data quality issues
- Detailed logs enable root cause analysis
- Sensible default values prevent cascading failures

### 6. Number Formatting Standards

**Decision:** Monetary values use 2 decimal places, percentages use 1 decimal place.

**Rationale:**
- NGN (Nigerian Naira) currency standard (ISO 4217)
- Percentage precision balances readability with statistical significance
- Consistent formatting across all API responses




