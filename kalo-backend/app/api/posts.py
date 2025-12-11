"""
Posts/Social Feed API Routes - /api/posts
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.models.models import Post, User
from app.api.users import get_current_user

router = APIRouter()

class PostResponse(BaseModel):
    id: str
    content: str
    post_type: str
    media_urls: list
    likes_count: int
    created_at: str

    class Config:
        from_attributes = True

class CreatePostRequest(BaseModel):
    content: str
    post_type: str = "text"
    media_urls: Optional[list[str]] = None

@router.get("/feed")
async def get_feed(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get social feed (simplified - no ranking yet)"""
    result = await db.execute(select(Post).limit(50))
    return result.scalars().all()

@router.post("/", response_model=PostResponse)
async def create_post(
    req: CreatePostRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new post"""
    post = Post(
        user_id=user.id,
        content=req.content,
        post_type=req.post_type,
        media_urls=req.media_urls or []
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post

@router.post("/{post_id}/like")
async def like_post(
    post_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Like a post"""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if post:
        post.likes_count += 1
        await db.commit()
    return post
