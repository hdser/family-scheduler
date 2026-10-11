# private.example/

This folder shows what your `private/` folder should contain, the way `.env.example` does for a `.env` file. Everything in it is fictional.

```bash
cp -r private.example private      # then edit the files in private/
```

`private/` is in `.gitignore`, so nothing in it is ever committed. Before each commit, `scripts/check_private.py` checks that none of its values leaked into a committed file. Set it up as a git hook and it runs automatically.

| File | Needed? | What it holds |
|---|---|---|
| `family.json` | **yes** | Everything that identifies your family: names, ids, clubs, email, calendar, the board's link, and the paragraphs that brief the Gmail task |
| `logos.json` | no | Club logos, inlined into the board. Without it the board shows initials |
| `league_games.txt` | no | A league schedule, for `scripts/league_fixtures.py` |
| `README.md` | no | This description; you can delete it from `private/` |

---

## family.json

The build (`scripts/build_board.py`) fills every `{{placeholder}}` in `board/index.src.html` and `tasks/*.md` with values from this file. `{{kid1.name}}`, for example, is `kids[0].name`. A missing value stops the build with its name.

### `board`

| Field | Example | Used for |
|---|---|---|
| `title` | `"Lindqvist Team Sheet"` | Browser tab title; how the tasks refer to the board |
| `artifact_url` | `"https://claude.ai/artifact/…"` | The published board. Fill it in after the first publish, then build again |
| `forward_email` | `"you+board@example.com"` | Address you forward invitations to. A `+board` alias of your Gmail address works and needs no setup |
| `home_area` | `"Uppsala, Sweden"` | Context for "Fill in from a message" (resolving places and languages) |
| `timezone` | `"Europe/Stockholm"` | IANA time zone for the tasks and calendar entries |
| `tz_city` | `"Stockholm"` | Same, as words in the prompts ("local Stockholm time") |
| `utc_offsets` | `"+02:00/+01:00"` | Summer/winter offsets the tasks write timestamps with |
| `fill_context` | `"The kids: Alva (handball at …) and Theo (…)."` | One or two sentences telling "Fill in from a message" who the kids are, their clubs and languages |

### `owner`

The parent who owns the board and the scheduled tasks. The prompts say things like "events *he* removed from the board".

| Field | Example |
|---|---|
| `name` | `"Sam"` |
| `he`, `his`, `himself` | `"they"`, `"their"`, `"themselves"` (or `she`/`her`/`herself`, `he`/`his`/`himself`) |

### `kids` (exactly two) and `adults` (exactly two)

The board has two lanes, one per kid. The adults appear on the School & work view.

| Field | Example | Notes |
|---|---|---|
| `id` | `"alva"` | Lower case letters, digits or `_`. Stored in every event and used as a CSS class. **Don't change it once the board has data.** Must not be `both` |
| `name` | `"Alva"` | Shown everywhere |
| `initial` | `"A"` | Kids only: the letter in the coloured circle |
| `calendar_color` | `"11"` | Kids only: Google Calendar colour id (`11` tomato, `10` basil, `9` blueberry, `6` tangerine, `3` grape, `8` graphite…) |

### `clubs`

Sports clubs (the school is always `school` and isn't listed here).

| Field | Example | Notes |
|---|---|---|
| `id` | `"northside"` | Same rules as kid ids; shows up in event and routine ids (`r-northside-tue`) |
| `logo_name` | `"Northside HK"` | The name to look up in `logos.json` |
| `sport` | `"handball"` | `handball`, `basketball`, `volleyball` or `swimming` (picks the right logo when names clash) |
| `match` | `"\\bnorthside\\b"` | Optional regular expression (case-insensitive) that recognises *your* club in game listings, so it isn't shown as an opponent |

### `calendar`

| Field | Example | Notes |
|---|---|---|
| `id` | `"…@group.calendar.google.com"` | Google Calendar → the calendar's settings → "Integrate calendar" → Calendar ID |
| `name` | `"Family"` | The calendar's name as Google shows it |
| `family_label` | `"Family"` | Title prefix for entries for both kids (`Family · Parents' evening`) |
| `family_color` | `"8"` | Colour id for those entries |

### `league` (only if you use the possible-match-day feature)

| Field | Example | Notes |
|---|---|---|
| `team_prefix` | `"Northside "` | Start of your club's team names in the league table (keep the trailing space) |
| `team_match` | `"northside"` | Regular expression that highlights your teams in a game list |
| `kid_name`, `kid_id` | `"Alva"`, `"alva"` | Who plays in the league |
| `club_label`, `club_id` | `"Northside"`, `"northside"` | The club, as words and as its id |
| `page_url` | `"https://handbollplay.se/…"` | Link stored on the tentative events |
| `id_suffix`, `short_label` | `"t"`, `"Team"` | Event ids `ev-YYYYMMDD-<club_id>-<id_suffix><n>` and the short label `Team 2?` |

### `examples`

Small examples that make the prompts concrete. Use ids from your own data so the model sees real patterns.

| Field | Example |
|---|---|
| `party` | `"Maja's birthday party"` (a typical forwarded invitation title) |
| `yield_rule` | `"r-seals-wed yieldsTo r-northside-wed = handball comes first on Wednesdays"` |
| `cancel_routine` | `"r-northside-thu"` |
| `overlap_kid` | `"she"` (the kid with overlapping sessions, as a pronoun) |

### `tasks`

`name` is the scheduled task's name (the audit task looks the other two up by name). `id` is optional, for your own reference.

### `prompt`

Whole paragraphs pasted into the Gmail task (and the audit). Write them like a briefing for a new babysitter: concrete senders, class names, team names, what to ignore. Use `\n` for line breaks inside the JSON string.

| Field | What to write |
|---|---|
| `kids_and_clubs` | `KIDS AND CLUBS` and one line per kid: kid id, clubs with team names and club ids, school and class |
| `club_messages` | `HOW THESE CLUBS COMMUNICATE`: which system each club uses, sender addresses, whether trainings get call-ups, which emails define the weekly schedule |
| `school` | `SCHOOL`: sender, how to tell which kid a message is for, what becomes an event, a break or a to-do, what to skip |
| `league` | The league rules, or `"(no league section)"` |
| `gmail_query` | The Gmail search, in brackets: `(from:club-system.se OR "Club name" OR …)` |
| `mail_details` | How to read each club's call-ups (where time, place, deadline and the reply link are) |
| `audit_kids` | One line the audit uses to check the right kid was picked: `correct kid (Alva = …; Theo = …)` |
| `audit_league` | What the audit checks for league days |

### `private_terms` and `logo_tests`

| Field | Notes |
|---|---|
| `private_terms` | Extra words `check_private.py` looks for, beyond the values above: surname, school, town, club names, friends' names. Words of 4 letters or fewer must match whole; longer ones also match as the start of a word |
| `logo_tests` | Team names `node scripts/logos/test_matching.js` tries to match (`"basketball:Name"` for other sports) |

---

## logos.json

```json
{"v": 2, "l": [
  ["handball",   ["Northside HK", "Northside", "Northside HF"], "data:image/svg+xml;base64,…"],
  ["basketball", ["River Hoops", "River Hoops BK"],             "data:image/webp;base64,…"]
]}
```

Each entry is `[sport, [every name the club goes by], image as a data URL]`. Use small square images (64–72 px WebP keeps 600 clubs around 2.5 MB). `docs/logos.md` says where to get them and how names are matched.

## league_games.txt

```
# date time|home|away|place|series   (time may be TBA)
2026-10-24 10:00|Northside HF 1|Westbay HK|West Hall|Girls U11 South A
```

`python3 scripts/league_fixtures.py private/league_games.txt > writes.json` turns it into "possible match day" events for an ArtifactData batch.
