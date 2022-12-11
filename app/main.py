from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/users")
async def get_users():
    return f"Endpoint for getting all the users."

@app.get("/users/{id}")
async def get_user(id: int):
    return f"This is the id that was sent through {id}."