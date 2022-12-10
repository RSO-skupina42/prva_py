from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/users/{name}")
async def say_hello(name: str):
    return f"Endpoint for user {name}"
