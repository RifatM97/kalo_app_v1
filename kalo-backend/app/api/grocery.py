"""
Grocery API Routes - /api/grocery
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.models.models import GroceryList, GroceryItem, User
from app.api.users import get_current_user

router = APIRouter()

class GroceryItemResponse(BaseModel):
    id: str
    name: str
    quantity: float
    unit: str
    checked: bool

class CreateGroceryItemRequest(BaseModel):
    name: str
    quantity: float
    unit: str

@router.get("/")
async def get_grocery_list(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current grocery list"""
    result = await db.execute(
        select(GroceryList).where(GroceryList.user_id == user.id)
    )
    lists = result.scalars().all()
    if lists:
        return lists[-1]  # Most recent
    return None

@router.post("/")
async def create_grocery_list(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new grocery list"""
    grocery_list = GroceryList(user_id=user.id)
    db.add(grocery_list)
    await db.commit()
    await db.refresh(grocery_list)
    return grocery_list

@router.post("/{list_id}/items")
async def add_item(
    list_id: str,
    req: CreateGroceryItemRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add item to list"""
    item = GroceryItem(
        grocery_list_id=list_id,
        name=req.name,
        quantity=req.quantity,
        unit=req.unit
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.put("/items/{item_id}/check")
async def toggle_item(
    item_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Check off item"""
    result = await db.execute(select(GroceryItem).where(GroceryItem.id == item_id))
    item = result.scalar_one_or_none()
    if item:
        item.checked = not item.checked
        await db.commit()
    return item
