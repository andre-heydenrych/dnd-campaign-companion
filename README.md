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

## Content
Uses only SRD 5.1/5.2 rules content (Creative Commons) plus our own homebrew and campaign material. Campaign data is stored in the app's database, not in this repository.

## License
Code is licensed under the [MIT License](LICENSE).
