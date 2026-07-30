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

---

Day 5 completes the CRUD set for Product by adding update and delete endpoints, and replaces silent failures or unhandled crashes with intentional error handling. Every endpoint now returns a predictable status code and body shape for both success and failure, backed by `HTTPException` and Pydantic-level validation.

---

## Goals

The API now supports:

- Updating an existing product's details (name, unit, cost, price, stock).
- Permanently removing a discontinued product from the catalog.
- Returning a clear `404` when a target product doesn't exist for update or delete.
- Rejecting invalid input (e.g. a negative price) before it ever reaches the database.
- A documented, predictable contract for every success and failure outcome.

---

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| PUT | `/products/{identifier}` | Update an existing product by ID or name |
| DELETE | `/products/{identifier}` | Remove a product by ID or name |

`identifier` accepts either a numeric product ID or a product name, consistent with the lookup pattern already used by `GET /products/search/{identifier}`.

---

## Endpoint Specifications

### Update Product

**Endpoint**

```
PUT /products/{identifier}
```

**Purpose**

Updates an existing product's details in PostgreSQL.

**Request Body**

This is a **full update**, not a partial one — the client must send every field defined on `ProductSchema`. There is no support yet for updating a single field in isolation (e.g. price only); the entire product record is replaced with the submitted values.

```json
{
  "name": "Basil Plant - 4in Pot",
  "unit": "each",
  "cost_per_unit": 1.75,
  "price_per_unit": 4.99,
  "quantity_in_stock": 35
}
```

**Success Response**

- Status Code: `200 OK`
- Returns the updated product using `ProductSchema` as the response model.

**Failure — Target Not Found**

- Status Code: `404 Not Found`
- Body:
  ```json
  { "detail": "Product not found" }
  ```
- Raised via `HTTPException` in the route once the repository lookup returns `None`.

**Failure — Invalid Identifier Format**

- Status Code: `400 Bad Request`
- Returned when a numeric identifier is `<= 0`, or a name identifier is blank after stripping whitespace.
- Body:
  ```json
  { "detail": "Product ID must be greater than 0." }
  ```
  or
  ```json
  { "detail": "Product name cannot be empty." }
  ```

---

### Delete Product

**Endpoint**

```
DELETE /products/{identifier}
```

**Purpose**

Permanently removes a product from PostgreSQL so it no longer appears in the catalog for staff or customers.

**Success Response**

- Status Code: `204 No Content`
- No response body — a `204` signals the delete succeeded and there's nothing further to return.

**Failure — Target Not Found**

- Status Code: `404 Not Found`
- Body:
  ```json
  { "detail": "Product not found" }
  ```
- Raised via `HTTPException` once the repository confirms no matching row exists to delete.

---

## Validation Rules

`ProductSchema` enforces the following at the Pydantic layer, using `Field` constraints:

- `cost_per_unit` must be greater than `0` (`Field(gt=0)`)
- `price_per_unit` must be greater than `0` (`Field(gt=0)`)
- `quantity_in_stock` must be greater than or equal to `0` (`Field(ge=0)`)

These rules apply to **every** endpoint that accepts a `ProductSchema` body — not just update. Since `POST /products` and `PUT /products/{identifier}` both take the same schema, a negative `cost_per_unit` or `price_per_unit` is rejected identically on create and update.

**Failure — Validation Rejected**

- Status Code: `422 Unprocessable Entity`
- Body (FastAPI's default Pydantic error shape):
  ```json
  {
    "detail": [
      {
        "type": "greater_than",
        "loc": ["body", "price_per_unit"],
        "msg": "Input should be greater than 0",
        "input": -6.0
      }
    ]
  }
  ```
- This response is generated by FastAPI/Pydantic automatically — the request never reaches the route function or the database.

**Additional constraint — Unique Product Name**

The `Product` model enforces `name` uniqueness at the database level (`unique=True`). A duplicate name on create raises a Postgres `IntegrityError`, which the route catches and converts into a readable error rather than a raw `500`:

- Status Code: `409 Conflict`
- Body:
  ```json
  { "detail": "Product 'Basil Plant' already exists" }
  ```

---

## Where Each Failure Is Caught

| Failure | Layer | Mechanism |
|---|---|---|
| Missing/invalid required field, wrong type, negative price, negative cost | Pydantic schema | Automatic `422`, request never reaches the route |
| Non-positive numeric identifier, blank name identifier | FastAPI route | Manual `if` checks, raises `HTTPException(400, ...)` |
| Product ID or name not found for update/delete | FastAPI route | Manual `if product is None:` check after the repository call returns, raises `HTTPException(404, ...)` |
| Duplicate product name on create | Database (Postgres) | `IntegrityError` raised by the `unique=True` constraint, caught in the route and converted to `HTTPException(409, ...)` |

No case is allowed to fall through to an unhandled exception — every failure path listed above is either intercepted by Pydantic before the route runs, or explicitly caught and re-raised as an `HTTPException` with a clear status code and message.

---

## Testing

Update and delete are covered by automated tests using `pytest` and FastAPI's `TestClient`, run against the real PostgreSQL database (no mocking):

- **Happy path** — create a product, then update it, and confirm the response reflects the changed fields with a `200`.
- **Not found** — update or delete a nonexistent identifier and confirm a `404` with a clear `detail` message.
- **Validation failure** — submit a negative price on update and confirm a `422`, proving the same schema-level rule applies across create and update.

Because these tests hit real Postgres rather than a mock, they also catch database-level behavior a mock wouldn't — for example, the `unique=True` constraint on `name` is enforced by Postgres itself, so a test can confirm the app correctly translates a real `IntegrityError` into a `409` rather than crashing.

---

## Key Engineering Lessons

Day 5 focused on turning "the API works" into "the API fails predictably." The main skills practiced were:

- Distinguishing which layer owns which kind of failure — schema, route, or database.
- Using `HTTPException` deliberately instead of letting errors surface as raw `500`s.
- Extending validation rules to every endpoint they logically apply to, not just the one being actively worked on.
- Writing tests against a real database to catch failures a mock would hide.

---

---

# Day 6: Testing & Config Cleanup

## Overview

Day 6 replaces manual Postman verification with an automated test suite, and moves the database connection string out of source code and into environment-based configuration. Both changes work together: once the connection string lives in a `.env` file instead of hardcoded in `database.py`, the test suite and every developer's machine need a reliable way to find it.

---

## Goals

- Verify create, validation, and not-found behavior automatically instead of by hand in Postman.
- Remove the hardcoded database connection string from source code entirely.
- Confirm the app still runs correctly for every developer after the config change, not just the one who made it.
- Re-run the full Postman collection from Days 4 and 5 as a final regression check.

---

## Automated Tests

**Where they live**

Tests are located in the `tests/` directory (e.g. `tests/test_main_create.py`), separate from application code in `src/`.

**How to run them**

From the project root, with the virtual environment activated:

```bash
pytest
```

Or target a specific file:

```bash
pytest tests/test_main_create.py -v
```

**Dependencies**

```bash
pip install pytest httpx
```

`httpx` is required because FastAPI's `TestClient` uses it internally to send simulated requests.

**What each required test asserts, and why**

| Test | What it does | What it proves |
|---|---|---|
| Happy-path create | Sends a valid `ProductSchema` body to `POST /products` | The full round trip works — the route accepts the request, the repository inserts into real Postgres, the database auto-assigns an `id`, and the response matches the expected shape with a `201` |
| Validation failure | Sends a body with a negative `price_per_unit` to `POST /products` | Pydantic's `Field(gt=0)` constraint rejects invalid input with a `422` before the request ever reaches the route function or the database |
| Not found | Sends a lookup or update/delete request for an identifier that doesn't exist | The route's `if product is None: raise HTTPException(404, ...)` branch returns a clear, readable error rather than a crash or a false success |

These tests run against the real PostgreSQL database rather than a mock, which matters: a mock only enforces behavior it's told to have, so it can't catch database-level rules like the `unique=True` constraint on `name` actually rejecting a duplicate insert.

---

## Configuration & Secrets

**Where the connection string used to live**

Previously, the database connection string was constructed directly inside `database.py` using a hardcoded value.

**Where it lives now**

`database.py` loads the connection string from an environment variable at runtime:

```python
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")
```

The actual value lives in a `.env` file in the project root, which is **not committed to version control**.

**`.gitignore`**

`.env` is listed in `.gitignore` so it can never be accidentally committed:

```
.env
```

**`.env.example`**

A `.env.example` file is committed instead, showing which variables are required without exposing real credentials:

```
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

**Setup for a new developer**

Anyone cloning the repo should:

1. Copy `.env.example` to a new file named `.env`.
2. Fill in their own local Postgres username, password, host, port, and database name.
3. Confirm the app starts cleanly with `uvicorn src.main:app --reload` and that `GET /db-check` returns a `200` with a product count.

Because `database.py` reads `DATABASE_URL` from the environment rather than a hardcoded string, each developer's `.env` can point at their own local database without touching shared source code.

---

## Regression Verification

Before considering Day 6 complete, the team re-ran the full Postman collection covering every endpoint from Days 4 and 5 (`POST /products`, `GET /products`, `GET /products/search/{identifier}`, `PUT /products/{identifier}`, `DELETE /products/{identifier}`, `GET /db-check`) to confirm the config change didn't silently break anything that previously worked. At least one teammate other than the person who made the `.env` change verified the app runs successfully after pulling it, since a config change working on one machine doesn't guarantee it works everywhere.

---

## Key Engineering Lessons

Day 6 focused on making correctness verifiable and configuration portable, rather than relying on one person's manual checks and one person's local setup:

- Automated tests turn "I checked it and it looked right" into a repeatable, objective check.
- Secrets and environment-specific values don't belong in source code — they belong in an untracked `.env` file, with a checked-in example showing the shape without the values.
- A change isn't verified until someone other than its author has run it successfully.