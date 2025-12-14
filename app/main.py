import time

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            # password="",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("DATABASE CONNECTION WAS SUCCESSFULLY!")
        break
    except Exception as error:
        print("DATABASE CONNECTIOIN FAILED!!!")
        print("ERROR:", error)
        time.sleep(2)

@app.get("/")
async def root():
    return {"message": "landing page"}


@app.get("/posts")
async def get_posts():
    posts = cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    cursor.execute(
        "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *",
        (post.title, post.content, post.published),
    )
    conn.commit()
    return {"data": cursor.fetchone()}


@app.get("/posts/{id}")
async def get_post(id: int, res: Response):
    cursor.execute("SELECT * FROM posts WHERE id = %s", (str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (str(id), ))
    data= cursor.fetchone()
    conn.commit()
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )


@app.put("/posts/{id}")
async def update_post(id: int, post: Post):
    cursor.execute(
        "UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *",
        (post.title, post.content, post.published, str(id)),
    )
    data = cursor.fetchone()
    conn.commit()
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )
    return {"data": data}
