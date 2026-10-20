# Changelog

## 2026-10-20
- Board can be shared by invitation again: no `data:` URLs left in the page (logos stored as base64 and turned into blob: URLs at runtime; select arrow drawn from script). The build refuses to produce a page with a `data:` URL. No visible change.
- `assets` capability (attaching screenshots to events) turned off.

## 2026-10-19
- Calendar sync also copies one parent's work shifts into a separate shared calendar ("<name> – work") for the next 90 days, one entry per working day and no reminders of their own, so only that parent's notification settings apply.

## 2026-10-13
- Gmail sync now opens club news links (Svenskalag "har publicerat en nyhet" mails only carry a link) and applies corrected times or places to the existing event. Triggered by a coach correcting a tournament's meeting time in a news post the sync had skipped.

## 2026-10-12
- Events without a club (e.g. added by hand) borrow the kid's club for the sport named in the title, so they get the club logo; new events are saved with that club.
- "Fill in from a message" now asks for the kid's club for that sport instead of leaving it empty.

## 2026-10-11
- `private.example/` (like `.env.example`): fictional `family.json`, `logos.json`, `league_games.txt` and a README describing every field. The build now reads `logos.json` from the config's folder.
- README screenshots of the real board with names, places, clubs and logos blurred (`scripts/screenshots.py`).
- Repository made reusable and safe to publish. Personal details moved to `private/family.json` (ignored by git). The board and task prompts are now templates filled in by `scripts/build_board.py`.
- New: `scripts/check_private.py` (leak check), `scripts/preview.py` (open the board locally with an in-memory stand-in for Claude), fictional example data (`config/sample-db.json`).
- Kid and adult colour variables renamed to neutral names (`--k1`, `--k2`, `--a1`, `--a2`); no visible change.
- Club logos moved out of the repository (`private/logos.json`).

## 2026-10-10
- Shared Google calendar: first week added by hand; new scheduled task "calendar sync" (twice a day, rolling 7 days).
- Training reminders set to 1 hour.
- Both sync tasks moved to Sonnet; weekly Opus audit added for two weeks.
- Repository created.

## 2026-10-09
- Logos inlined into the page: a separate `logos.json` made the board "Forbidden" for a parent it was shared with.
- Logos shown next to titles, with the kid's circle kept.
- Club logos for about 600 Swedish handball, basketball and volleyball clubs, with opponents' logos on match days.
- Colours: one strong colour per kid and per adult; darker kid circles in light mode.
- Next up card: solid in the kid's colour.
- Possible league days show the Going / Not going answer instead of "Possible".
- School & work view (timetables, holidays, work shifts), reworked Up next, cancel or remove events, skip or switch weekly sessions.

## 2026-10-08
- Redesign "A + B": Up next feed on phones, two-lane week grid on desktop, light/dark themes.
- Going / Maybe / Not going made visible in Week, Month, Next week and to-dos.
- Add event with "Fill in from a message" (text or screenshot) and attachments; forwarding to a `+board` email alias.
- League match days added as possible match days.
- Missing weekly trainings fixed (coach emails now read in full).
- First board and twice-daily Gmail sync.
