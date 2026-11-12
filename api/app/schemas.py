"""Response models: the shapes the API sends back, separate from the tables."""
from enum import Enum

from sqlmodel import SQLModel


class ShopRead(SQLModel):
    id: str
    name: str
    description: str | None


class ItemType(str, Enum):
    weapon = "weapon"
    armor = "armor"
    adventuring_item = "adventuring_item"
    masterwork_weapon = "masterwork_weapon"
    masterwork_armor = "masterwork_armor"


class InventoryEntry(SQLModel):
    item_type: ItemType
    item_id: str
    name: str
    description: str | None
    quantity: int
    in_stock: bool
    price_gp: float
