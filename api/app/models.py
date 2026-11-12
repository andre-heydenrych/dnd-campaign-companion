"""Database tables.

Every primary key is a human-readable slug (e.g. "shortsword",
"party-foundry"), except ShopInventory.id, which is an autoincrement int.
Response shapes for the API live in app/schemas.py, not here.
"""
from enum import Enum

from sqlalchemy import CheckConstraint, Numeric, UniqueConstraint
from sqlmodel import Field, SQLModel

# Name constraints and indexes predictably. Alembic's batch mode (needed for
# SQLite) can only drop or change a constraint later if it has a name.
SQLModel.metadata.naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Gold costs are floats stored with 2-decimal precision.
GOLD = Numeric(10, 2, asdecimal=False)


def modifier_field():
    """A price multiplier, 1.0 (no change) by default."""
    return Field(default=1.0, sa_column_kwargs={"server_default": "1.0"})


# --- Accounts -----------------------------------------------------------------

class AccountType(str, Enum):
    admin = "admin"
    player = "player"
    party = "party"


class Account(SQLModel, table=True):
    __tablename__ = "accounts"

    id: str = Field(primary_key=True)
    type: AccountType
    display_name: str


class PartyPlayer(SQLModel, table=True):
    """A player belonging to a party (both are accounts)."""
    __tablename__ = "party_players"

    party_id: str = Field(foreign_key="accounts.id", primary_key=True)
    player_id: str = Field(foreign_key="accounts.id", primary_key=True)


# --- Shops --------------------------------------------------------------------

class Shop(SQLModel, table=True):
    __tablename__ = "shops"

    id: str = Field(primary_key=True)
    name: str
    description: str | None = None
    cost_modifier: float = modifier_field()


class ShopAccess(SQLModel, table=True):
    """Which accounts (players or parties) can see a shop, and at what modifier."""
    __tablename__ = "shop_access"

    shop_id: str = Field(foreign_key="shops.id", primary_key=True)
    account_id: str = Field(foreign_key="accounts.id", primary_key=True)
    cost_modifier: float = modifier_field()


# --- Items --------------------------------------------------------------------

class ItemBase(SQLModel):
    """Columns every item table has."""
    id: str = Field(primary_key=True)
    name: str
    description: str | None = None
    cost_gp: float = Field(sa_type=GOLD)


class Weapon(ItemBase, table=True):
    __tablename__ = "weapons"


class Armor(ItemBase, table=True):
    __tablename__ = "armor"


class AdventuringItem(ItemBase, table=True):
    __tablename__ = "adventuring_items"


class MasterworkWeapon(ItemBase, table=True):
    __tablename__ = "masterwork_weapons"

    base_weapon_id: str = Field(foreign_key="weapons.id")


class MasterworkArmor(ItemBase, table=True):
    __tablename__ = "masterwork_armor"

    base_armor_id: str = Field(foreign_key="armor.id")


# --- Shop inventory -----------------------------------------------------------

# Each inventory row points at exactly one of these item columns.
INVENTORY_ITEM_COLUMNS = (
    "weapon_id",
    "armor_id",
    "adventuring_item_id",
    "masterwork_weapon_id",
    "masterwork_armor_id",
)


class ShopInventory(SQLModel, table=True):
    __tablename__ = "shop_inventory"
    __table_args__ = (
        CheckConstraint(
            " + ".join(f"({col} IS NOT NULL)" for col in INVENTORY_ITEM_COLUMNS) + " = 1",
            name="exactly_one_item",
        ),
        *(UniqueConstraint("shop_id", col) for col in INVENTORY_ITEM_COLUMNS),
    )

    id: int | None = Field(default=None, primary_key=True)  # the DB assigns it
    shop_id: str = Field(foreign_key="shops.id")
    weapon_id: str | None = Field(default=None, foreign_key="weapons.id")
    armor_id: str | None = Field(default=None, foreign_key="armor.id")
    adventuring_item_id: str | None = Field(default=None, foreign_key="adventuring_items.id")
    masterwork_weapon_id: str | None = Field(default=None, foreign_key="masterwork_weapons.id")
    masterwork_armor_id: str | None = Field(default=None, foreign_key="masterwork_armor.id")
    quantity: int = Field(default=1, sa_column_kwargs={"server_default": "1"})  # 0 = out of stock
    cost_modifier: float = modifier_field()
