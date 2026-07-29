# Project Description
This project is a FastAPI web service built with Python to practice creating and testing API endpoints. It provides HTTP endpoints that return responses based on user requests. The project helps developers learn the basics of API development, virtual environments, dependency management, and testing with Postman.

# Prererequisites
Python 3.x: Required because the FastAPI application is written in Python and needs the Python interpreter to run.
Git: Required to clone the repository, pull updates, and push code changes to GitHub.
Code Editor (Cursor, VS Code, etc.): Required to view, edit, and manage the project files.
Postman: Required to send requests to the API and verify that the endpoints return the expected responses.

# Virtual Environment Setup

Create a virtual environment:

```bash
python -m venv venv
```

Activate virtual environment: 

```bash
venv/Scripts/activate
```

# Installation

### If you're cloning an existing project (has a `requirements.txt`)

With your venv activated, install the exact dependencies the project already uses:

```bash
pip install -r requirements.txt
```

### If you're setting up the project for the very first time (no `requirements.txt` yet)

1. With an activated, empty venv, install FastAPI and Uvicorn:

   ```bash
   pip install fastapi uvicorn
   ```

2. Confirm the app runs (see [Running the App](#running-the-app) below) with no exceptions.

3. Once you've confirmed everything works, generate `requirements.txt` so your exact dependencies are captured:

   ```bash
   pip freeze > requirements.txt
   ```

4. Commit and push `requirements.txt` to the repo:

   ```bash
   git add requirements.txt
   git commit -m "Add requirements.txt"
   git push (Your branch)
   ```

## Running the App

The FastAPI application is located in `src/main.py` and can be started with Uvicorn from the root directory:

```bash
uvicorn src.main:app --reload
```

Once running, the app should be available at:

```
http://127.0.0.1:8000
```

## Day 1: Basic FastAPI Endpoints

Day 1 introduced the first FastAPI routes and established the project structure.

Endpoints added on Day 1:

- `GET /` — returns a simple hello message
- `GET /hello/{name}` — returns a personalized greeting

This day was about learning how FastAPI routes work and how to run the app locally.

## Day 2: Request/Response Basics & Pydantic

Day 2 added the first product domain concept using Pydantic and in-memory state.

Endpoints added on Day 2:

- `POST /products` — accepts a `Product` request body and stores it in memory
- `GET /products` — returns every product submitted so far
- `GET /products/search` — searches products by required `name` query and optional `unit` query parameter

Example `Product` request body:

```json
{
  "name": "Basil Plant - 4in Pot",
  "unit": "each",
  "cost_per_unit": 1.75,
  "price_per_unit": 4.99,
  "quantity_in_stock": 40
}
```

Day 2 also introduced validation rules for the `Product` model using Pydantic.

Validation rules:

- `cost_per_unit` must be greater than or equal to 0
- `price_per_unit` must be greater than or equal to 0
- `quantity_in_stock` must be greater than or equal to 0

The original Day 2 design stored products in a Python list inside the running process, so data would disappear when the server restarted.

## Day 3: Postgres & SQLAlchemy Connection

Day 3 replaces in-memory storage with a PostgreSQL database and SQLAlchemy model mapping.

Endpoints supported now:

- `POST /products` — accepts a `Product` payload and stores it in Postgres
- `GET /products` — returns every product stored in Postgres
- `GET /products/search` — searches products by required `name` query and optional `unit` query parameter
- `GET /db-check` — verifies the PostgreSQL connection and returns a product count

Database dependencies:

```bash
pip install sqlalchemy psycopg2-binary
```

The app is now configured to connect to PostgreSQL through a shared database module. The same engine and SQLAlchemy `Base` class are used across the application.

### Schema strategy

During development, the app rebuilds its schema on startup by dropping and recreating tables from the SQLAlchemy models.

### Database check endpoint

Use `GET /db-check` to confirm the app can talk to Postgres and return the current number of products.

### Validation

The `Product` model continues to enforce business rules via Pydantic:

- `cost_per_unit` must be greater than or equal to 0
- `price_per_unit` must be greater than or equal to 0
- `quantity_in_stock` must be greater than or equal to 0

Invalid requests return a `422` response with details about the failing field.

## Confirming the app

You should be able to confirm the app works by:

- **Browser** — visiting `http://127.0.0.1:8000/` returns a `200` body `{"message": "Hello World"}`
- **Postman** — sending requests to `/hello/{name}`, `/products`, `/products/search`, and `/db-check`



# Day 4: Product CRUD — Create & Read

## Overview

Day 4 introduces database persistence for the Garden Center product catalog.

Products are now stored in PostgreSQL using SQLAlchemy instead of an in-memory list. The API supports creating products, retrieving all products, and retrieving individual products by ID.

The implementation was based on a technical specification created from business requirements before development began.

---

# Goals

The API supports:

- Persisting new products in PostgreSQL.
- Retrieving the full product catalog.
- Retrieving a single product by identifier.
- Returning a clear response when a product does not exist.
- Providing controlled API responses through Pydantic schemas.

---

# Technology Stack

| Technology | Purpose |
|---|---|
| FastAPI | API routing and HTTP responses |
| Pydantic | Request validation and response schemas |
| SQLAlchemy | Database models and persistence |
| PostgreSQL | Product data storage |

---

# API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/products` | Create a new product |
| GET | `/products` | Retrieve all products |
| GET | `/products/{product_id}` | Retrieve a single product |

---

# Endpoint Specifications

## Create Product

**Endpoint**

```
POST /products
```

**Purpose**

Creates and stores a new product in PostgreSQL.

**Success Response**

- Status Code: `201 Created`
- Returns the created product using the product response schema.

---

## Retrieve All Products

**Endpoint**

```
GET /products
```

**Purpose**

Returns all products currently stored in the database.

**Success Response**

- Status Code: `200 OK`
- Returns a list of products.

---

## Retrieve Single Product

**Endpoint**

```
GET /products/{product_id}
```

**Purpose**

Retrieves one product using its unique identifier.

**Success Response**

- Status Code: `200 OK`
- Returns the requested product.

---

## Product Not Found

When a product identifier does not exist:

**Response**

- Status Code: `404 Not Found`
- Returns a clear error message indicating the product was not found.

A missing product is treated as a client resource lookup issue, not a server failure.

---

# Application Architecture

## Pydantic Schemas

Responsible for:

- Validating incoming request data.
- Defining API request and response formats.
- Controlling which fields are returned to clients.

---

## SQLAlchemy Models

Responsible for:

- Representing database tables.
- Mapping application objects to PostgreSQL records.
- Handling persistence operations.

---

## FastAPI Routes

Responsible for:

- Handling HTTP requests.
- Coordinating validation and database operations.
- Returning appropriate status codes and responses.

---

# Database Session Management

The application uses a FastAPI database dependency (`get_db`) to provide a database session per request.

This prevents routes from manually creating connections and keeps database access consistent across the application.

---

# Response Models

All endpoints returning product data use FastAPI `response_model`.

Response models ensure:

- API responses remain predictable.
- Internal database fields are not exposed accidentally.
- Database structure changes do not automatically change the API contract.

---

# Persistence Verification

The application should demonstrate that:

1. A product can be created.
2. The application can be restarted.
3. The same product can still be retrieved.

This confirms that product data is stored in PostgreSQL rather than memory.

---

# Testing Checklist

## Product Creation

- Product creation works.
- Correct status code is returned.
- Created product data is returned.

## Product Retrieval

- Full catalog retrieval works.
- Single product lookup works.
- Correct status codes are returned.

## Not Found Handling

- Missing products return `404 Not Found`.
- Error responses are clear and consistent.

---

# Day 4 Definition of Done

Completed:

- [x] Technical specification created before implementation.
- [x] Products persisted in PostgreSQL.
- [x] Create product endpoint implemented.
- [x] Product catalog endpoint implemented.
- [x] Single product lookup implemented.
- [x] Not-found handling implemented.
- [x] Response models added.
- [x] Database sessions managed through dependencies.
- [x] Postman collection updated.
- [x] README updated.

---

# Key Engineering Lessons

Day 4 focused on translating business requirements into a technical specification.

The main skills practiced were:

- Designing API contracts.
- Choosing meaningful HTTP behavior.
- Separating validation, database, and routing responsibilities.
- Writing clear specifications before implementation.

A clear specification creates predictable software and reduces ambiguity during development.