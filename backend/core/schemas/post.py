from pydantic import BaseModel


class PostRead(BaseModel):
    id: int
    title: str
    content: str
    is_published: bool
    author_id: int


class CreatePost(BaseModel):
    title: str
    content: str
    author_id: int
