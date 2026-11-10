from enum import Enum
from sqlmodel import SQLModel, Field

class Rarity(str, Enum):
    common = "common"
    uncommon = "uncommon"
    rare = "rare"
    very_rare = "very rare"
    legendary = "legendary"
    artifact = "artifact"

class ItemBase(SQLModel):               # fields shared by everything
    name: str = Field(index=True)
    price_gp: int = Field(ge=0)
    rarity: Rarity = Rarity.common
    description: str | None = None

class Item(ItemBase, table=True):       # table=True makes it a database table
    id: int | None = Field(default=None, primary_key=True)  # the DB assigns it

class ItemCreate(ItemBase):             # what the client sends (no id)
    pass