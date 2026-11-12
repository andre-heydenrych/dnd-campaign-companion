"""Shared test fixtures. Every test gets a fresh in-memory SQLite database, never dnd.db."""
import os

# Belt and braces: point the app's own engine away from dnd.db before it's imported.
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel

from app.database import create_db_engine, get_session
from app.main import app
from app.models import Account, AccountType, PartyPlayer, Shop, ShopAccess


@pytest.fixture
def session():
    # StaticPool keeps one connection, so the in-memory database lives for the whole test.
    engine = create_db_engine("sqlite://", poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture
def client(session):
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def world(session):
    """A party with one player, a loner player, and three shops:

    - party-shop: only the party has access (modifier 1.0)
    - player-shop: only the player has access (modifier 0.8)
    - shared-shop: party at 0.9, player at 0.7 (lowest should win)
    - locked-shop: nobody has access
    """
    session.add_all([
        Account(id="party-a", type=AccountType.party, display_name="Party A"),
        Account(id="player-a", type=AccountType.player, display_name="Player A"),
        Account(id="loner", type=AccountType.player, display_name="Loner"),
        Shop(id="party-shop", name="Party Shop"),
        Shop(id="player-shop", name="Player Shop", description="Secret"),
        Shop(id="shared-shop", name="Shared Shop"),
        Shop(id="locked-shop", name="Locked Shop"),
    ])
    session.flush()
    session.add_all([
        PartyPlayer(party_id="party-a", player_id="player-a"),
        ShopAccess(shop_id="party-shop", account_id="party-a", cost_modifier=1.0),
        ShopAccess(shop_id="player-shop", account_id="player-a", cost_modifier=0.8),
        ShopAccess(shop_id="shared-shop", account_id="party-a", cost_modifier=0.9),
        ShopAccess(shop_id="shared-shop", account_id="player-a", cost_modifier=0.7),
    ])
    session.commit()
