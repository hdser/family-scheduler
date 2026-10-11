# Changelog

## 2026-10-11
- Repository made reusable and safe to publish. Personal details moved to `private/family.json` (ignored by git). The board and task prompts are now templates filled in by `scripts/build_board.py`.
- New: `scripts/check_private.py` (leak check), `scripts/preview.py` (open the board locally with an in-memory stand-in for Claude), a fictional `config/family.example.json` and `config/sample-db.json`.
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
