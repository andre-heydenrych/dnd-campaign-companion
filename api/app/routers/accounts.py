from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app import shop_service
from app.database import get_session
from app.models import Account, Shop
from app.schemas import InventoryEntry, ShopRead

router = APIRouter(prefix="/accounts", tags=["shops"])
SessionDep = Annotated[Session, Depends(get_session)]


def get_account_or_404(session: Session, account_id: str) -> Account:
    account = session.get(Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.get("/{account_id}/shops", response_model=list[ShopRead])
def list_shops(account_id: str, session: SessionDep):
    get_account_or_404(session, account_id)
    return shop_service.visible_shops(session, account_id)


@router.get("/{account_id}/shops/{shop_id}/inventory", response_model=list[InventoryEntry])
def get_shop_inventory(account_id: str, shop_id: str, session: SessionDep):
    get_account_or_404(session, account_id)
    shop = session.get(Shop, shop_id)
    if shop is None:
        raise HTTPException(status_code=404, detail="Shop not found")

    access_mod = shop_service.access_modifier(session, account_id, shop_id)
    if access_mod is None:
        # Say only that access is denied; don't reveal anything about the stock.
        raise HTTPException(status_code=403, detail="No access to this shop")

    return shop_service.shop_inventory(session, shop, access_mod)
