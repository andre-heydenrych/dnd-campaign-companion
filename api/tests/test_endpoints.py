import pytest

from app.models import Armor, Shop, ShopInventory, Weapon


@pytest.fixture
def stocked(session, world):
    session.add_all([
        Weapon(id="longsword", name="Longsword", cost_gp=15),
        Weapon(id="dagger", name="Dagger", cost_gp=2, description="Pointy."),
        Armor(id="plate", name="Plate", cost_gp=1500),
    ])
    session.flush()
    session.add_all([
        ShopInventory(shop_id="shared-shop", weapon_id="longsword", quantity=3, cost_modifier=1.1),
        ShopInventory(shop_id="shared-shop", weapon_id="dagger", quantity=10),
        ShopInventory(shop_id="shared-shop", armor_id="plate", quantity=0),
        ShopInventory(shop_id="locked-shop", weapon_id="dagger", quantity=99),
    ])
    session.get(Shop, "shared-shop").cost_modifier = 1.5
    session.commit()


def test_shop_list_for_player(client, world):
    response = client.get("/accounts/player-a/shops")
    assert response.status_code == 200
    # Sorted by name; own access plus the party's.
    assert response.json() == [
        {"id": "party-shop", "name": "Party Shop", "description": None},
        {"id": "player-shop", "name": "Player Shop", "description": "Secret"},
        {"id": "shared-shop", "name": "Shared Shop", "description": None},
    ]


def test_shop_list_for_party(client, world):
    response = client.get("/accounts/party-a/shops")
    assert response.status_code == 200
    assert [shop["id"] for shop in response.json()] == ["party-shop", "shared-shop"]


def test_shop_list_hides_cost_modifier(client, world):
    shop = client.get("/accounts/party-a/shops").json()[0]
    assert set(shop) == {"id", "name", "description"}


def test_inventory_with_computed_prices_and_stock(client, stocked):
    response = client.get("/accounts/player-a/shops/shared-shop/inventory")
    assert response.status_code == 200
    # Shop modifier 1.5; player's access modifier 0.7 (beats the party's 0.9).
    assert response.json() == [
        {
            "item_type": "weapon", "item_id": "dagger", "name": "Dagger",
            "description": "Pointy.", "quantity": 10, "in_stock": True,
            "price_gp": 2.1,  # 2 x 1.5 x 1.0 x 0.7
        },
        {
            "item_type": "weapon", "item_id": "longsword", "name": "Longsword",
            "description": None, "quantity": 3, "in_stock": True,
            "price_gp": 17.33,  # 15 x 1.5 x 1.1 x 0.7 = 17.325, rounded half-up
        },
        {
            "item_type": "armor", "item_id": "plate", "name": "Plate",
            "description": None, "quantity": 0, "in_stock": False,
            "price_gp": 1575.0,  # 1500 x 1.5 x 1.0 x 0.7
        },
    ]


def test_inventory_price_depends_on_who_is_asking(client, stocked):
    prices = {
        entry["item_id"]: entry["price_gp"]
        for entry in client.get("/accounts/party-a/shops/shared-shop/inventory").json()
    }
    assert prices["dagger"] == 2.7  # 2 x 1.5 x 1.0 x 0.9


def test_inventory_403_does_not_leak_stock(client, stocked):
    response = client.get("/accounts/player-a/shops/locked-shop/inventory")
    assert response.status_code == 403
    assert "dagger" not in response.text


@pytest.mark.parametrize("url", [
    "/accounts/nobody/shops",
    "/accounts/nobody/shops/shared-shop/inventory",
])
def test_unknown_account_404(client, world, url):
    response = client.get(url)
    assert response.status_code == 404
    assert response.json() == {"detail": "Account not found"}


def test_unknown_shop_404(client, world):
    response = client.get("/accounts/player-a/shops/nowhere/inventory")
    assert response.status_code == 404
    assert response.json() == {"detail": "Shop not found"}
