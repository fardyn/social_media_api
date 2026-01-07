import re
import time
from fastapi import FastAPI, HTTPException, Response, status, Depends
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db
import psycopg2
from typing import List


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/posts", response_model=List[schemas.Post])
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_post(post: schemas.PostBase, db: Session = Depends(get_db)):
    new_post = models.Post(
        title=post.title,
        content=post.content,
        published=post.published,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post
    

@app.get("/posts/{id}", response_model=schemas.Post)
async def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
    return post


@app.delete("/posts/{id}", response_model=schemas.Post)
async def delete_post(id: int, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )
    post_query.delete()
    db.commit()


@app.put("/posts/{id}", response_model=schemas.Post)
async def update_post(id: int, post: schemas.PostBase, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_data = post_query.first()
    if post_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )
    post_query.update({
        models.Post.title: post.title,
        models.Post.content: post.content,
        models.Post.published: post.published,
    })
    db.commit()
    return post_query.first()
