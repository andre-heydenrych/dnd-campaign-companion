from app.shop_service import access_modifier, visible_shops


def shop_ids(session, account_id):
    return {shop.id for shop in visible_shops(session, account_id)}


def test_own_access_only(session, world):
    # player-shop is granted to the player directly; the party has no row for it.
    assert "player-shop" in shop_ids(session, "player-a")
    assert "player-shop" not in shop_ids(session, "party-a")
    assert access_modifier(session, "player-a", "player-shop") == 0.8


def test_access_through_party_only(session, world):
    # party-shop is granted to the party; the player has no row of their own.
    assert "party-shop" in shop_ids(session, "player-a")
    assert access_modifier(session, "player-a", "party-shop") == 1.0


def test_own_and_party_access_lowest_modifier_wins(session, world):
    # Party row 0.9, player row 0.7.
    assert access_modifier(session, "player-a", "shared-shop") == 0.7
    # The party itself only has its own row.
    assert access_modifier(session, "party-a", "shared-shop") == 0.9


def test_party_row_wins_when_it_is_lower(session, world):
    from app.models import ShopAccess

    row = session.get(ShopAccess, ("shared-shop", "player-a"))
    row.cost_modifier = 1.2
    session.commit()
    assert access_modifier(session, "player-a", "shared-shop") == 0.9


def test_no_access(session, world):
    assert access_modifier(session, "player-a", "locked-shop") is None
    assert shop_ids(session, "loner") == set()


def test_no_access_returns_403(client, world):
    response = client.get("/accounts/player-a/shops/locked-shop/inventory")
    assert response.status_code == 403
    assert response.json() == {"detail": "No access to this shop"}
