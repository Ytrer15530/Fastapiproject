from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from py_model import UserResponse, UserCreate, ProductCreate, ProductResponse, PostCreate, PostResponse
from alchemy_models import User, Product, get_db, Post
from starlette.responses import JSONResponse
import requests
from typing import List

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
@app.get("/products/{product_id}", response_model=ProductResponse)
def read_products(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/products/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/posts/{post_id}", response_model=PostResponse)
def read_products(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.post("/posts/", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = Post(**post.model_dump())
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


# peredelat'

@app.delete("/delete_user/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    db.delete(user)
    db.commit()
    return JSONResponse('User deleted!')


@app.delete("/delete_product/{product_id}", response_model=ProductResponse)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Product).filter(Product.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail='User not found')
    db.delete(post)
    db.commit()
    return JSONResponse('Product deleted!')


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, update_user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in update_user.model_dump().items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.put("/products/{product_id}", response_model=ProductResponse)
def update_post(post_id: int, update_post: ProductCreate, db: Session = Depends(get_db)):
    db_post = db.query(Product).filter(Product.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in update_post.model_dump().items():
        setattr(db_post, field, value)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.get("/users/", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.get("/products/", response_model=List[ProductResponse])
def list_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = db.query(Product).offset(skip).limit(limit).all()
    return posts


def add_users_from_api_task(db: Session, api_url: str):
    response = requests.get(api_url).json()

    for user_data in response.get('users', []):
        user_create = UserCreate(username=user_data.get('firstName'), password=user_data.get('password'),
                                 email=user_data.get('email'))
        db_user = User(**user_create.model_dump())
        db.add(db_user)
    db.commit()


@app.post('/add_users_from_api/')
def add_users_from_api(bgt: BackgroundTasks, db: Session = Depends(get_db)):
    api_url = 'https://dummyjson.com/users'
    bgt.add_task(add_users_from_api_task, db, api_url)
    return JSONResponse(content={"message": 'Added users from api'})


def add_products_from_api_task(db: Session, api_url: str):
    response = requests.get(api_url).json()

    for product_data in response.get('products', []):
        product_create = ProductCreate(title=product_data.get('title'), price=product_data.get('price'))
        db_product = Product(**product_create.model_dump())
        db.add(db_product)
    db.commit()


@app.post('/add_products_from_api/')
def add_products_from_api(bgt: BackgroundTasks, db: Session = Depends(get_db)):
    api_url = 'https://dummyjson.com/products'
    bgt.add_task(add_products_from_api_task, db, api_url)
    return JSONResponse(content={"message": "Added products from api"})


def add_posts_from_api_task(db: Session, api_url: str):
    response = requests.get(api_url).json()

    for post_data in response.get('posts', []):
        post_create = PostCreate(title=post_data.get('title'), content=post_data.get('body'))
        db_post = Post(**post_create.model_dump())
        db.add(db_post)
    db.commit()


@app.post('/add_posts_from_api/')
def add_posts_from_api(bgt: BackgroundTasks, db: Session = Depends(get_db)):
    api_url = 'https://dummyjson.com/posts'
    bgt.add_task(add_posts_from_api_task, db, api_url)
    return JSONResponse(content={"message": "Added posts from api"})


if __name__ == "__main__":
    import uvicorn
    from alchemy_models import SessionLocal

    uvicorn.run(app, host="127.0.0.1", port=8000)
