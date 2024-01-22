from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(UserCreate):
    id: int


class PostCreate(BaseModel):
    title: str
    content: str


class PostResponse(PostCreate):
    id: int
