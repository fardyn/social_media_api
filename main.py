from fastapi import Body, FastAPI
from pydantic import BaseModel


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/posts")
async def posts():
    return {"data": "hello!"}


@app.post("/createpost")
async def create_posts(payload: dict = Body(...)):
    print(payload)
    return {"new_post": f"title: {payload["title"]}, content: {payload["content"]}"}

