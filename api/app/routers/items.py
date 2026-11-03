from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Item, ItemCreate

router = APIRouter(prefix="/items", tags=["items"])
SessionDep = Annotated[Session, Depends(get_session)]

@router.get("")
def list_items(session: SessionDep) -> list[Item]:
    return session.exec(select(Item)).all()

@router.get("/{item_id}")
def get_item(item_id: int, session: SessionDep) -> Item:
    item = session.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("", status_code=201)
def create_item(data: ItemCreate, session: SessionDep) -> Item:
    item = Item.model_validate(data)
    session.add(item)
    session.commit()          # save to the database
    session.refresh(item)     # reload it to get the new id
    return item