## Installation

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

In the `main.py` with a FastAPI app instance and at least these two routes:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
def read_hello(name: str):
    return {"message": f"Hello, {name}!"}
```

Start the server with Uvicorn from the src directory:

```bash
uvicorn main:app --reload
```
Or, start the server with Uvicorn from the root directory:

```bash
uvicorn src.main:app --reload
```

Once running, the app should be available at:

```
http://127.0.0.1:8000
```

You should be able to confirm it's working two ways:

- **Browser** — visiting `http://127.0.0.1:8000/` returns a `200` status with the exact body `{"message": "Hello World"}`. Visiting `http://127.0.0.1:8000/hello/Sam` returns a `200` with a body that includes `"Sam"`. Try at least two different names to confirm the path parameter works generally, not just for one value.
- **Postman** — send the same requests from Postman so you can inspect the request, response body, and status code for each. Save both requests into a Postman collection.

## Running Tests

From the gitbash terminal enter:

```bash
pytest
```
Example output of the completed pytest:

```
====================== test session starts ======================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: (File Path)
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.14.2
collected 2 items

tests\test_main.py ..                                                                                                                                                             [100%]

====================== 2 passed in 0.42s ======================
```

## Project Structure

```
project-root/
├── src/
│   ├── __init__.py
│   └── main.py
│   
├── tests/
|   ├── __init__.py
│   └── test_main.py
|
├── requirements.txt
├── .gitignore
├── README.md
└── pyproject.toml
```