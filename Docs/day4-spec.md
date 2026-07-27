# Day 4 Technical Specification

## Purpose

This API allows the garden center to store and retrieve product information using a PostgreSQL database. Product data is validated with Pydantic, persisted using SQLAlchemy, and exposed through FastAPI endpoints.

---

# Endpoint: Create Product

**Method:** POST

**Path:** `/products`

## Purpose

Creates a new product and stores it in the PostgreSQL database.

## Request Body

```json
{
  "id": 1,
  "name": "Rose Bush",
  "unit": "each",
  "cost_per_unit": 5.99,
  "price_per_unit": 12.99,
  "quantity_in_stock": 20
}
```

## Successful Response

**Status Code**

```
201 Created
```

**Response Body**

```json
{
  "id": 1,
  "name": "Rose Bush",
  "unit": "each",
  "cost_per_unit": 5.99,
  "price_per_unit": 12.99,
  "quantity_in_stock": 20
}
```

## Validation

Incoming request data is validated using the `ProductSchema` Pydantic model before any database operations occur.

---

# Endpoint: Get All Products

**Method:** GET

**Path:** `/products`

## Purpose

Returns every product currently stored in the database.

## Request Body

None.

## Successful Response

**Status Code**

```
200 OK
```

**Response Body**

```json
[
  {
    "id": 1,
    "name": "Rose Bush",
    "unit": "each",
    "cost_per_unit": 5.99,
    "price_per_unit": 12.99,
    "quantity_in_stock": 20
  }
]
```

---

Endpoint: Search for a Product

Method: GET

Path: /products/search

Purpose

Returns one product matching the provided product ID or product name.

Request Body

None.

Query Parameters

One of the following query parameters must be provided:

id (integer)
name (string)
Example Requests
GET /products/search?id=1
GET /products/search?name=Rose Bush
Successful Response

Status Code

200 OK

Response Body

{
  "id": 1,
  "name": "Rose Bush",
  "unit": "each",
  "cost_per_unit": 5.99,
  "price_per_unit": 12.99,
  "quantity_in_stock": 20
}
Failure Responses

If neither an ID nor a name is provided:

Status Code

400 Bad Request

Response Body

{
  "detail": "Must provide id or name"
}

If the requested product does not exist:

Status Code

404 Not Found

Response Body

{
  "detail": "Product not found"
}
Validation Responsibilities

Validation is performed by Pydantic using ProductSchema.

Pydantic verifies that:

All required fields are provided.
Values match the expected data types.
Numeric values satisfy any validation rules defined in the schema.

If validation fails, FastAPI automatically returns a 422 Unprocessable Entity response.

Database Responsibilities

Database operations are handled by the ProductRepository.

The repository is responsible for:

Creating products.
Retrieving all products.
Retrieving a product by ID.
Retrieving a product by name.
Interacting directly with SQLAlchemy and PostgreSQL.

Database sessions are provided using the get_db() dependency so each request receives its own database session.

SQLAlchemy Responsibilities

The SQLAlchemy Product model defines the structure of the product table in PostgreSQL.

It maps Python objects to database rows and manages persistence.

FastAPI Route Responsibilities

The FastAPI route functions are responsible for:

Receiving HTTP requests.
Calling the appropriate ProductRepository method.
Returning the correct HTTP status code.
Returning API responses using response_model.

Routes do not directly perform SQL queries.

Response Model Decision

All endpoints that return product data use response_model.

Examples include:

response_model=ProductSchema

and

response_model=list[ProductSchema]

This ensures:

Only the intended fields are returned to the client.
Responses follow a consistent API contract.
Internal SQLAlchemy implementation details are hidden.
Responses are validated before being sent to the client.
FastAPI automatically documents the response structure in Swagger UI.

Without response_model, FastAPI would return the SQLAlchemy object directly, making the API dependent on the database model and potentially exposing internal fields that should remain private.