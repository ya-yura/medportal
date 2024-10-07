from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.models import User, db_helper, Post
from core.schemas.post import PostRead, CreatePost


router = APIRouter(
    tags=["Posts"]
)


@router.get("/", response_model=list[PostRead])
async def get_posts(session: AsyncSession = Depends(db_helper.session_getter)):
    stmt = select(Post)
    result = await session.scalars(stmt)
    return result.all()


@router.post("/create", response_model=CreatePost)
async def create_post(post: CreatePost, session: AsyncSession = Depends(db_helper.session_getter)):
    post = Post(**post.dict())
    session.add(post)
    await session.commit()
    return post

