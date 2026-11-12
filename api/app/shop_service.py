"""Shop access and pricing rules, kept out of the routers so they can be tested on their own.

- An account can see a shop if it has its own shop_access row for it, or
  belongs (via party_players) to a party that has one.
- The access modifier is the lowest shop_access.cost_modifier among the
  account's own row and its parties' rows for that shop.
- Price = item cost_gp x shop cost_modifier x inventory cost_modifier x access modifier,
  rounded once at the end by round_price().
"""
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.models import (
    AdventuringItem,
    Armor,
    MasterworkArmor,
    MasterworkWeapon,
    PartyPlayer,
    Shop,
    ShopAccess,
    ShopInventory,
    Weapon,
)
from app.schemas import InventoryEntry, ItemType

# Which ShopInventory column points at which item table.
ITEM_SOURCES = (
    (ItemType.weapon, "weapon_id", Weapon),
    (ItemType.armor, "armor_id", Armor),
    (ItemType.adventuring_item, "adventuring_item_id", AdventuringItem),
    (ItemType.masterwork_weapon, "masterwork_weapon_id", MasterworkWeapon),
    (ItemType.masterwork_armor, "masterwork_armor_id", MasterworkArmor),
)


# --- Pricing ------------------------------------------------------------------

def round_price(value: float | Decimal) -> Decimal:
    """Round a final price half-up to 2 decimals (2.675 -> 2.68, 0.125 -> 0.13).

    This is the single place prices are rounded. To round to whole gold later,
    change "0.01" to "1" here.
    """
    if not isinstance(value, Decimal):
        # str() first, so 2.675 becomes Decimal("2.675") rather than the
        # binary float's 2.67499999...
        value = Decimal(str(value))
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_price(
    cost_gp: float,
    shop_modifier: float,
    inventory_modifier: float,
    access_modifier: float,
) -> Decimal:
    """Item cost x shop modifier x inventory modifier x access modifier, rounded once."""
    # Multiply as Decimals so the unrounded product is exact (no float drift
    # like 0.30000000000000004 before rounding).
    total = Decimal(1)
    for factor in (cost_gp, shop_modifier, inventory_modifier, access_modifier):
        total *= Decimal(str(factor))
    return round_price(total)


# --- Access -------------------------------------------------------------------

def _access_rows_for(account_id: str):
    """A WHERE clause matching shop_access rows for the account or any of its parties."""
    party_ids = select(PartyPlayer.party_id).where(PartyPlayer.player_id == account_id)
    return or_(ShopAccess.account_id == account_id, ShopAccess.account_id.in_(party_ids))


def visible_shops(session: Session, account_id: str) -> list[Shop]:
    """Shops the account can see, directly or through a party, sorted by name."""
    shop_ids = select(ShopAccess.shop_id).where(_access_rows_for(account_id))
    return list(session.exec(select(Shop).where(Shop.id.in_(shop_ids)).order_by(Shop.name)))


def access_modifier(session: Session, account_id: str, shop_id: str) -> float | None:
    """The lowest applicable shop_access.cost_modifier, or None if the account can't see the shop."""
    statement = select(func.min(ShopAccess.cost_modifier)).where(
        ShopAccess.shop_id == shop_id, _access_rows_for(account_id)
    )
    return session.exec(statement).one()


# --- Inventory ----------------------------------------------------------------

def shop_inventory(session: Session, shop: Shop, access_mod: float) -> list[InventoryEntry]:
    """The shop's inventory with prices for an account whose access modifier is access_mod."""
    rows = list(session.exec(select(ShopInventory).where(ShopInventory.shop_id == shop.id)))

    entries: list[InventoryEntry] = []
    for item_type, column, model in ITEM_SOURCES:
        rows_for_type = [row for row in rows if getattr(row, column) is not None]
        if not rows_for_type:
            continue
        ids = [getattr(row, column) for row in rows_for_type]
        items = {item.id: item for item in session.exec(select(model).where(model.id.in_(ids)))}
        for row in rows_for_type:
            item = items[getattr(row, column)]
            price = calculate_price(item.cost_gp, shop.cost_modifier, row.cost_modifier, access_mod)
            entries.append(
                InventoryEntry(
                    item_type=item_type,
                    item_id=item.id,
                    name=item.name,
                    description=item.description,
                    quantity=row.quantity,
                    in_stock=row.quantity > 0,
                    price_gp=float(price),
                )
            )

    return sorted(entries, key=lambda entry: (entry.name.lower(), entry.item_type.value))
