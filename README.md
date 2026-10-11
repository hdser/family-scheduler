# Family Team Sheet

A shared board for two kids' sports, school and parties. It is kept up to date from Gmail by a scheduled Claude task and mirrored into a shared Google calendar for phone reminders. The board is a single HTML page published as a [Claude artifact](https://claude.ai). It keeps its data in the artifact's own database, so there's no server to run.

Everything personal (names, email addresses, clubs, school, calendar id, the board's link) lives in `private/family.json`, which git ignores. The repository holds templates; a small build script fills them in.

```
Gmail ──(twice a day)──► Gmail → board sync ──► board database ◄──► board page (Claude artifact)
                                                     │                 used by both parents
                                                     ▼
                         Board → calendar sync ──► shared Google calendar ──► phone reminders
```

## What's in here

| Path | What it is |
|---|---|
| `board/index.src.html` | The board page (HTML, CSS and JS in one file) with `{{placeholders}}` |
| `tasks/*.md` | The scheduled tasks: settings plus the prompt template |
| `config/family.example.json` | A fictional family showing every setting |
| `config/sample-db.json` | Fictional board data for trying the page locally |
| `scripts/build_board.py` | Fills the templates → `dist/index.html` and `dist/tasks/*.txt` |
| `scripts/check_private.py` | Fails if a personal value from `private/family.json` is in a file git would commit |
| `scripts/preview.py` | Wraps the built page with an in-memory stand-in for Claude so it opens in any browser |
| `scripts/calendar_plan.py` | Dry run of the calendar rules against a dump of the board's data |
| `scripts/league_fixtures.py` | Turns a league schedule into "possible match day" events |
| `scripts/logos/` | Tests for matching team names to club logos |
| `docs/` | Data model, design decisions, logos |

## Try it

```bash
python3 scripts/build_board.py --config config/family.example.json
python3 scripts/preview.py --now 2026-10-12T08:00:00+02:00
open dist/preview.html
```

## Set it up for your family

You need a Claude plan with artifacts and scheduled tasks, plus the Gmail and Google Calendar connectors.

1. `cp config/family.example.json private/family.json` and fill it in. Kids, adults and clubs need short lower-case ids; they are stored in the data and used as CSS classes, so don't change them later. The `prompt` section holds the paragraphs that describe your clubs and school to the Gmail task. Write them the way you'd brief a new babysitter.
2. `python3 scripts/build_board.py`
3. In Claude, publish `dist/index.html` as an artifact with the capabilities `db`, `user`, `assets`, `downloads` and `sample` (images on). Put its link in `board.artifact_url` and build again.
4. Create a Google calendar for the reminders (or use an empty one) and put its id in `calendar.id`.
5. Create the scheduled tasks from `tasks/*.md`: the settings are in each file's table, and the text to paste is in `dist/tasks/<name>.txt`. Give the Gmail task the Gmail connector and the calendar task the Google Calendar connector.
6. Optional: forward invitations to a `+board` alias of your address (`board.forward_email`); the Gmail task turns every message sent there into an event.

Colours live at the top of `board/index.src.html` (`--k1`, `--k2` for the kids, `--a1`, `--a2` for the adults).

## Changing the board

1. Edit `board/index.src.html` (never `dist/`).
2. `python3 scripts/build_board.py`, then check it with `scripts/preview.py`.
3. Publish `dist/index.html` to the same artifact. It must stay **one file**: supporting files published next to it are refused ("Forbidden") for people the board is shared with.
4. If you changed a task template, paste the new `dist/tasks/<name>.txt` into that scheduled task.
5. Note the change in `CHANGELOG.md`.

Republishing never touches the data: the page reads everything from the artifact database.

## Keeping personal data out of git

- `private/` and `dist/` are in `.gitignore`.
- Run `python3 scripts/check_private.py` before committing, or install it as a hook: `ln -s ../../scripts/check_private.py .git/hooks/pre-commit`.
- Add anything else that identifies you (surname, school, town, club names) to `private_terms` in `private/family.json`, so the check looks for it too.

## Club logos

The board shows club logos next to events and opponents. Logos are the clubs' property, so they aren't in this repository. Put your own collection in `private/logos.json` (format and sources in `docs/logos.md`). Without it the board shows initials instead.

## Licence

MIT, see `LICENSE`.
