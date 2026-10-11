# Club logos

The board shows a club's logo next to its events and next to opponents on match days. The logos are the clubs' property, so they are **not** in this repository: the build inlines `private/logos.json` when it exists, and the board falls back to initials when it doesn't.

## Format

`private/logos.json` = `{"v": 2, "l": [[sport, [names…], "data:image/webp;base64,…"], …]}`

- `sport`: `handball`, `basketball`, `volleyball` or `swimming`.
- `names`: every name the club goes by (official name, short name, team names from league tables).
- The image: a small square WebP or PNG (64–72 px keeps the page around 2–3 MB for 600 clubs).

Your own clubs must be findable by their `logo_name` in `private/family.json`.

## Where to get them

Swedish federations publish club lists with logos through the public Handboll Play / Solidsport API:

| Set | Endpoint (`https://solidsport.com/api/play_v1/…`) | Image field |
|---|---|---|
| Handball clubs | `companies/svenskhandboll/channels/association_clubs` | `profile_image_url` |
| Basketball clubs | `companies/sbbf/channels/association_clubs` | `profile_image_url` |
| Volleyball clubs | `companies/svenskvolleyboll/channels/association_clubs` | `profile_image_url` |
| League team badges | `events/event/<league>/games/upcoming` | `home_team` / `away_team` → `badge_image.lg` |

Clubs that aren't there (swimming clubs, small associations) usually have a logo on their own website.

The images were collected in a browser (fetch, draw onto a canvas, export as WebP data URLs), because Claude's cloud workspace can't reach these sites directly.

## How names are matched

The code is in `board/index.src.html` (search for "club logos"):

1. Exact match on any name, after normalising (lower case, accents removed, punctuation dropped).
2. Drop team suffixes from the end (`2`, `Röd`, `Blå`, `U`, `Dam`, `P12`…) and retry.
3. Compare the distinctive part of the name with generic words removed (HK, HF, IF, Handbollsklubb, Basket…), preferring the event's sport.

`node scripts/logos/test_matching.js` prints the logo each name in `logo_tests` (in `private/family.json`) gets. Build first: it reads the engine from `dist/index.html`.
