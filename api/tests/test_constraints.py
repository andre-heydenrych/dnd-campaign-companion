import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models import Armor, ShopInventory, Weapon


@pytest.fixture
def items(session, world):
    session.add_all([
        Weapon(id="dagger", name="Dagger", cost_gp=2),
        Armor(id="shield", name="Shield", cost_gp=10),
    ])
    session.commit()


def test_foreign_keys_pragma_is_on(session):
    assert session.exec(text("PRAGMA foreign_keys")).one()[0] == 1


def test_inventory_row_with_no_item_is_rejected(session, items):
    session.add(ShopInventory(shop_id="party-shop"))
    with pytest.raises(IntegrityError, match="exactly_one_item"):
        session.commit()


def test_inventory_row_with_two_items_is_rejected(session, items):
    session.add(ShopInventory(shop_id="party-shop", weapon_id="dagger", armor_id="shield"))
    with pytest.raises(IntegrityError, match="exactly_one_item"):
        session.commit()


def test_inventory_row_with_one_item_is_accepted(session, items):
    session.add(ShopInventory(shop_id="party-shop", weapon_id="dagger"))
    session.commit()
    row = session.get(ShopInventory, 1)
    assert (row.quantity, row.cost_modifier) == (1, 1.0)


def test_inventory_foreign_key_to_missing_item_is_rejected(session, items):
    session.add(ShopInventory(shop_id="party-shop", weapon_id="no-such-weapon"))
    with pytest.raises(IntegrityError, match="FOREIGN KEY"):
        session.commit()


def test_same_item_twice_in_one_shop_is_rejected(session, items):
    session.add(ShopInventory(shop_id="party-shop", weapon_id="dagger"))
    session.commit()
    session.add(ShopInventory(shop_id="party-shop", weapon_id="dagger"))
    with pytest.raises(IntegrityError, match="UNIQUE"):
        session.commit()
