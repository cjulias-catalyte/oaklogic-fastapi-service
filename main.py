from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello Worldd"}

@app.get("/hello/{name}")
async def root(name: str):
    return {"message": f"Hello {name}"}
