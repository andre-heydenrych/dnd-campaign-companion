"""Load example data into the database. Safe to run more than once.

Run from api/, after `alembic upgrade head`:

    python seed.py

The data lives in seed_data/*.json, so it can be swapped without touching this
script. Rows are matched by primary key (inventory rows by shop and item) and
updated in place; nothing is deleted.
"""
import json
from pathlib import Path

from sqlalchemy import inspect
from sqlmodel import Session, SQLModel, select

from app.database import engine
from app.models import (
    INVENTORY_ITEM_COLUMNS,
    Account,
    Armor,
    PartyPlayer,
    Shop,
    ShopAccess,
    ShopInventory,
    Weapon,
)

SEED_DIR = Path(__file__).resolve().parent / "seed_data"


def load(filename: str):
    return json.loads((SEED_DIR / filename).read_text(encoding="utf-8"))


def upsert(session: Session, model: type[SQLModel], rows: list[dict]) -> None:
    """Insert each row, or update it if a row with the same primary key exists."""
    for row in rows:
        session.merge(model(**row))


def upsert_inventory(session: Session, rows: list[dict]) -> None:
    """Inventory ids are auto-assigned, so match on (shop, item) instead."""
    for row in rows:
        item_column = next(col for col in INVENTORY_ITEM_COLUMNS if row.get(col))
        existing = session.exec(
            select(ShopInventory).where(
                ShopInventory.shop_id == row["shop_id"],
                getattr(ShopInventory, item_column) == row[item_column],
            )
        ).first()
        if existing is None:
            session.add(ShopInventory(**row))
        else:
            existing.quantity = row.get("quantity", 1)
            existing.cost_modifier = row.get("cost_modifier", 1.0)


def seed(session: Session) -> None:
    upsert(session, Weapon, load("srd_weapons.json"))
    upsert(session, Armor, load("srd_armor.json"))

    campaign = load("example_campaign.json")
    upsert(session, Account, campaign["accounts"])
    upsert(session, Shop, campaign["shops"])
    session.flush()  # parents first, so the foreign keys below have something to point at
    upsert(session, PartyPlayer, campaign["party_players"])
    upsert(session, ShopAccess, campaign["shop_access"])
    upsert_inventory(session, campaign["shop_inventory"])
    session.commit()


def main() -> None:
    if not inspect(engine).has_table("shop_inventory"):
        raise SystemExit("Tables are missing. Run `alembic upgrade head` from api/ first.")
    with Session(engine) as session:
        seed(session)
    print(f"Seeded {engine.url}")


if __name__ == "__main__":
    main()
