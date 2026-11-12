# dnd-campaign-companion

Player-side companion for our D&D 5e campaigns: a shop/item tracker built around our house rules, a shared lore wiki, maps and a house-rule reference — used at (and between) sessions by me and my players across two ongoing campaigns I DM: one online in Foundry VTT and one played in person.

## Why
Over several months I've developed an extensive set of house rules, including more specific rules for items and equipment, alongside a lot of campaign lore. That material currently lives in scattered notes, documents and chat. This app brings it together in one place, so the party can see what they can buy and record what they've learned.

## Roadmap

### 1. House-rule items, shops and basic login (in progress)
- [x] Data model: accounts (admin, party, player), parties, shops, shop access, and item tables for weapons, armor, adventuring items and masterwork weapons and armor
- [x] Pricing: item cost × shop modifier × inventory modifier × the account's access modifier, with per-player rates within a party
- [x] API: the shops an account can see, and each shop's stock with computed prices
- [x] Example data: SRD 5.1 weapons and armor, plus example shops
- [x] Web: username login that remembers accounts on the device
- [ ] Web: browse the shops your account can access, and their stock and prices
- [ ] House-rule item properties beyond name, description and cost
- [ ] Mobile-friendly layout for use at the table

### 2. Masterwork items
- [ ] Modifications that turn a base weapon or armor into a masterwork item
- [ ] Create masterwork items in the app
- [ ] Import items in bulk

### 3. Lore wiki and handouts
- [ ] Present handouts and lore to the party
- [ ] NPCs, places, factions and history pages with links between them
- [ ] Control what the party has discovered, and when

### Later
- [ ] Foundry VTT integration: sync shops, items and lore with the online campaign
- [ ] Discord integration (to be decided)
- [ ] Maps with pinned locations linked to lore
- [ ] Searchable house-rule reference
- [ ] Campaigns and settings, with real player accounts and permissions

## Tech stack
- **Backend:** FastAPI (Python)
- **Frontend:** Angular (TypeScript)
- Built iteratively with Claude Code

## Structure
- `api/` — backend (FastAPI)
- `web/` — frontend (Angular)

## How to run the API
You need Python 3.13+. From `api/`:

```bash
python -m venv .venv
.venv\Scripts\activate         # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head           # create or update the database tables
fastapi dev app/main.py        # API on http://localhost:8000, docs at /docs
```

Run `alembic upgrade head` again after pulling changes that add migrations; the API doesn't create tables on startup. The database is `api/dnd.db` by default. Set the `DATABASE_URL` environment variable to use a different one.

### Example data
To load the SRD 5.1 weapons and armor (name and cost), a party account (`party-foundry`), a player in that party (`player-demo`) and two shops with some stock, run from `api/` after `alembic upgrade head`:

```bash
python seed.py
```

It's safe to run more than once: existing rows are updated, not duplicated. The data lives in `api/seed_data/*.json`, so you can replace it without touching the script.

### Tests
From `api/`, with the venv active:

```bash
pytest
```

The tests use a fresh in-memory SQLite database each time, so they never touch `dnd.db`.

### Endpoints
Interactive docs are at http://localhost:8000/docs while the API runs.

- `GET /health`: returns `{"status": "ok"}`.
- `GET /accounts/{account_id}/shops`: the shops an account can see, either through its own access or through a party it belongs to. 404 if the account doesn't exist.
- `GET /accounts/{account_id}/shops/{shop_id}/inventory`: the shop's stock as that account sees it, with each item's type, id, name, description, quantity, `in_stock` and `price_gp`. 404 if the account or shop doesn't exist, 403 if the account can't see the shop.

Prices are item cost × shop modifier × inventory modifier × the account's access modifier (the lowest of its own and its parties' modifiers for that shop), rounded half-up to 2 decimals at the end. The rules live in `api/app/shop_service.py`.

With the example data, try `/accounts/player-demo/shops` (both shops) and `/accounts/party-foundry/shops/back-room-armory/inventory` (403).

## How to run the web app
You need Node.js 22.22+ or 24.15+ (check with `node -v`).

```bash
cd web
npm install      # first time, and after package.json changes
npm start        # dev server on http://localhost:4200
```

The dev server forwards any request to `/api/...` to the FastAPI backend at `http://localhost:8000` (the `/api` prefix is stripped, so `/api/health` hits `/health`). Start the API first if you need it; see `web/proxy.conf.json`.

Other commands, from `web/`:
- `npm test` runs the unit tests (Vitest)
- `npm run build` makes a production build in `web/dist/`
- `npm run ng -- <args>` runs any other Angular CLI command, e.g. `npm run ng -- generate component foo`

The scripts call `node node_modules/@angular/cli/bin/ng.js` directly instead of `ng`, because the Windows `ng.cmd` shim breaks on the `&` in this repo's folder path.

For now the app only has a username-only login page and an empty home page. The username is kept in the browser (localStorage) and isn't sent to the API yet.

## Content
Uses only SRD 5.1/5.2 rules content (Creative Commons) plus our own homebrew and campaign material. Campaign data is stored in the app's database, not in this repository.

## License
Code is licensed under the [MIT License](LICENSE).
