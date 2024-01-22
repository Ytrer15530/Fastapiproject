from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from py_model import UserResponse, UserCreate, PostResponse, PostCreate
from alchemy_models import User, Post, get_db
from starlette.responses import JSONResponse


# init fast api app
app = FastAPI()

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],
                   )


# crud operation for User model
@app.get("/users/{user_id}", response_model=UserResponse)
def read_users(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# crud operation for Post model
@app.get("/posts/{post_id}", response_model=PostResponse)
def read_posts(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.post("/posts/", response_model=PostResponse)
def create_post(post: PostCreate, user_id: int, db: Session = Depends(get_db)):
    db_post = Post(**post.model_dump(), user_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.get("/")
def test_json():
    data = {
        "user_id": 1,
        "user": "ilya",
        "email": "ilya15530@gmail.com"
    }
    return JSONResponse(data)


def task():
    for i in range(100):
        print(i)


@app.get("/task/")
def back_task(bgt: BackgroundTasks):
    bgt.add_task(task)
    return JSONResponse({"task": "Start"})


if __name__ == "__main__":
    import uvicorn
    from alchemy_models import SessionLocal

    uvicorn.run(app, host="127.0.0.1", port=8000)
