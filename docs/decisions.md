# Decisions

Newest first. Each entry says what was decided and why.

## 2026-10-11: Public repository, personal data in `private/`
The board page, task prompts and scripts are templates. Names, ids, email addresses, the calendar id, the board's link and the family-specific prompt paragraphs live in `private/family.json`, which git ignores. `scripts/build_board.py` fills the templates in, and `scripts/check_private.py` fails if any of those values shows up in a file git would commit. When the split was made, the rebuilt task prompts were character-for-character identical to the ones running. The rebuilt board only differed in neutral renames (CSS variables `--k1/--k2/--a1/--a2`), and screenshots of every view matched pixel for pixel. Club logos stay private too (they are the clubs' property).

## 2026-10-10: Keep the Claude artifact; no PWA for now
A Claude artifact can't ship a web manifest or service worker, so it can't be installed as an app. A real PWA would need its own hosting plus a database the scheduled tasks can reach. The board stays an artifact; the calendar handles phone reminders.

## 2026-10-10: Reminders through a shared Google calendar
- One previously unused calendar, shared with the family, so both parents get the entries.
- A separate scheduled task (`tasks/calendar-sync.md`), because connectors can't be added to an existing scheduled task.
- Trial window 7 days, rolling. Later: events 3 months ahead, trainings 3 weeks ahead.
- Weekly trainings are single entries, not a repeating series, so a cancelled or skipped session simply disappears.
- Entry title `<Kid|Family> · <title>`, one Google colour per kid, marked free, no guests, no emails.
- Reminders: trainings 60 min before; matches, cups and parties at 19:00 the evening before plus 60 min before; all-day entries at 18:00 the evening before.
- Cancelled and Not going entries are removed. An entry deleted by hand in Google Calendar is never recreated (`meta/gcal.dismissed`).
- Every entry carries `[team-sheet:<key>]`; the sync never touches untagged events.

## 2026-10-10: Daily summary push set aside
Push notifications from scheduled tasks go only to the task's owner, and only when a run is judged noteworthy. The calendar (plus Google's own daily agenda email) covers both parents.

## 2026-10-10: Cheaper model for the syncs, with a temporary audit
Both sync tasks run on Sonnet. A weekly Opus audit (`tasks/team-sheet-audit.md`) checks their work for two weeks and then switches itself off.

## 2026-10-09: The board stays a single file
Publishing the logos as a separate file made the page show "Forbidden" for a parent it was shared with (as Commenter), while it kept working for the owner. Inlining fixed it. Rule: never publish supporting files with the board.

## 2026-10-09: The sync doesn't mark emails as read
Tested: reading a message through the Gmail connector (MINIMAL, PLAIN_TEXT, FULL_CONTENT) leaves it unread.

## 2026-10-09: Club logos
Logos for all Swedish handball and basketball clubs and the volleyball clubs on Handboll Play / Solidsport, plus a few from the clubs' own sites. They are shown **next to** the kid's coloured circle, never instead of it. Opponents come from league games or from "Home – Away" titles; unknown teams show initials.

## 2026-10-09: Colours
One strong colour per kid (used everywhere) and one per adult on the School & work view. The "Going" colour is turquoise so it can't be confused with a kid's colour. The Next up card is solid in the kid's colour. In light mode the kid circles are solid with a white letter.

## 2026-10-09: Answers win over "Possible"
On possible league days a Going / Maybe / Not going answer is shown instead of the "Possible" label; Not going rows are crossed out.

## 2026-10-08: Layout "A + B"
Phone home is the Up next feed. Week view is a two-lane time grid (one lane per kid). On desktop the grid has the to-dos beside it. The look: light grey ground, white panels, solid kid-coloured blocks, blue accent, small radii, no gradients.

## 2026-10-08: League days are tentative
When a club has several teams in one league and the child's team is only known from the call-up, every match day of every team is loaded as "possible". A call-up confirms one day and removes the other teams' entries that day. Possible days never count as clashes.

## 2026-10-08: Coach emails are the source of truth for weekly trainings
Club systems don't send a call-up for every training; season times come in coach emails. The sync reads every page of search results so it doesn't miss them.
