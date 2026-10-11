# Board data model

The board page and the scheduled tasks share the artifact database. All times are Europe/Stockholm local time.

## events

Doc ids: `ev-YYYYMMDD-<club>-<slug>` (from email), `ev-YYYYMMDD-<club>-<suffix><n>` (possible league days, see `scripts/league_fixtures.py`), `fw-<gmail id>` (forwarded), `m-<base36 time>` (added on the page), `x-<routine id>-YYYYMMDD` (a weekly session skipped on the page), `o-<routine id>-YYYYMMDD` (switched to the other overlapping session that day).

| Field | Meaning |
|---|---|
| title, short | Full title; short label (≤16 chars) |
| kid | a kid id from `private/family.json`, or `both` |
| club | a club id from `private/family.json`, or `school` |
| kind | match, tournament, training, team, meet, camp, fan, social, change, other |
| start, end | `YYYY-MM-DDTHH:MM` or `YYYY-MM-DD` (all-day) |
| meet | Meeting time (samling) `HH:MM` |
| place, notes | Venue; up to three practical lines |
| optional | Fan events, camps, voluntary meets |
| status | confirmed · cancelled · tentative (possible league day) |
| team, series, games | League days: team, series and `[{time, home, away, place}]` |
| rsvpBy, rsvpUrl | Reply deadline and the club's reply link |
| sourceUrl, source | Gmail link; `email` · `league` · `forward` · `manual` |
| cancelsRoutine | Routine id this event cancels on its date |
| overrideRoutine | Routine id chosen instead of its partner on that date |
| attachments | `[{id, name, type, size}]` in the artifact asset store |
| attend, attendAt | **Page only.** Going / Maybe / Not going |
| statusByHand, cancelReason, hidden, hiddenAt | **Page only.** Cancelled or removed on the page |

## routine

One doc per weekly session, id `r-<club>-<mon…sun>`: kid, club, label, day (1–7, Monday = 1), start, end, place, note. `yieldsTo` (**page only**) = the routine that wins when the two overlap (for example `r-swim-wed` yields to `r-handball-wed`).

## todos

Id `t-<club>-<slug>`: title, kid, club, priority (`high` or normal), due, dueLabel, detail, url, linkLabel, email, eventId, source. `done`, `doneAt` are **page only** (except invoice to-dos closed by a payment confirmation).

## clubs

id, name, short, sport, team, kids[], system, contact, web, fees, notes, order.

## timetable (page only)

School and work slots: person (a kid or adult id), kind (`school` · `work` · `other`), label, day or date, start, end, place, note, from/to. The sync never writes here.

## breaks

Days without school: label, from, to, who[], note, source. The sync only adds docs from email.

## meta

- `meta/sync`: lastRun, schedule, log[] (newest first, max 15). Written by the Gmail sync.
- `meta/gcal`: calendarId, map (`key → Google event id`), dismissed[], lastRun, status. Written by the calendar sync. Keys: `ev:<event id>` and `r:<routine id>:<YYYY-MM-DD>`.

## Who writes what

| Writer | May write | Must never write |
|---|---|---|
| Board page (the parents) | attend, done, hidden, cancelReason, statusByHand, yieldsTo, manual events, x-/o- docs, timetable, breaks, attachments | — |
| Gmail sync | events, routine, todos, clubs, breaks (new only), meta/sync | page-only fields, manual docs, timetable |
| Calendar sync | meta/gcal | everything else |
