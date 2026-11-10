# dnd-campaign-companion

Player-side companion for our D&D 5e campaigns: a shop/item tracker built around our house rules, a shared lore wiki, maps and a house-rule reference — used at (and between) sessions by me and my players across two ongoing campaigns I DM: one online in Foundry VTT and one played in person.

## Why
Over several months I've developed an extensive set of house rules, including more specific rules for items and equipment, alongside a lot of campaign lore. That material currently lives in scattered notes, documents and chat. This app brings it together in one place, so the party can see what they can buy and record what they've learned.

## Planned features

### Shops & items (first milestone)
- [ ] Item catalogue: SRD items plus homebrew, with house-rule properties and pricing
- [ ] Shops per town with shopkeeper (linked NPC), stock and prices
- [ ] Party gold and purchase log

### Lore wiki
- [ ] NPCs, places, factions, deities and history pages with links between them
- [ ] Tags and full-text search
- [ ] "What the party knows" — rumours vs confirmed facts, updated as we learn more
- [ ] Campaign timeline and session notes that feed into lore

### Maps
- [ ] Upload maps and pin locations linked to lore pages

### House rules
- [ ] Searchable house-rule reference per campaign

### Foundry VTT integration
- [ ] Sync shops, items and lore with our Foundry VTT campaign

### Platform
- [ ] Multiple campaigns, player accounts and permissions
- [ ] Mobile-friendly for use at the table
- [ ] Markdown import/export

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
