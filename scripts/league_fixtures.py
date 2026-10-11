"""Turn a league schedule into "possible match day" events for the board.

Some clubs enter several teams in the same league and a child's team for the day is
only known from the call-up. This script makes one tentative event per team per match
day; the Gmail sync later confirms the right one when the call-up arrives.

    python3 scripts/league_fixtures.py private/league_games.txt > league_writes.json
    python3 scripts/league_fixtures.py games.txt --confirmed 2026-11-08:"Northside HF 2"

Input: one game per line, "YYYY-MM-DD HH:MM|home|away|place|series" (time may be TBA),
lines starting with # are ignored. Output: a JSON list of ArtifactData batch writes
({"op":"set","collection":"events","doc_id":…,"data":…}). Days given with --confirmed
are skipped (they already exist as confirmed events).

Uses "league" from private/family.json (or FAMILY_CONFIG): team_prefix (e.g. "Northside "),
kid_id, kid_name, club_id, page_url, and optionally id_suffix (event ids
ev-YYYYMMDD-<club_id>-<id_suffix><n>, default "t") and short_label (default "Team").
"""
import argparse, collections, datetime as dt, json, os, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("games")
    ap.add_argument("--confirmed", action="append", default=[], help='DATE:TEAM, e.g. 2026-11-08:"Northside HF 2"')
    ap.add_argument("--now", default=dt.datetime.now().astimezone().isoformat(timespec="seconds"))
    a = ap.parse_args()
    lg = json.load(open(os.environ.get("FAMILY_CONFIG", ROOT / "private/family.json")))["league"]
    prefix = lg["team_prefix"].strip()
    confirmed = {tuple(c.split(":", 1)) for c in a.confirmed}

    days = collections.OrderedDict()
    for line in pathlib.Path(a.games).read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        when, home, away, place, series = [x.strip() for x in line.split("|")]
        date, time = when.split(" ")
        team = home if home.startswith(prefix) else away if away.startswith(prefix) else None
        if not team:
            continue
        days.setdefault((date, team), []).append(
            {"time": None if time == "TBA" else time, "home": home, "away": away, "place": place, "series": series})

    writes, games_total = [], 0
    for (date, team), games in days.items():
        games_total += len(games)
        if (date, team) in confirmed:
            continue
        timed = [g["time"] for g in games if g["time"]]
        num = team.split()[-1]
        doc = {
            "team": team, "series": games[0]["series"], "kid": lg["kid_id"], "club": lg["club_id"], "kind": "match",
            "games": [{"time": g["time"] or "TBA", "home": g["home"], "away": g["away"], "place": g["place"]} for g in games],
            "place": " / ".join(sorted({g["place"] for g in games})), "sourceUrl": lg.get("page_url", ""),
            "source": "league", "updatedAt": a.now,
            "title": f"Possible match day · {team}", "short": f"{lg.get('short_label', 'Team')} {num}?"[:16], "status": "tentative",
        }
        if timed:
            first, last = min(timed), max(timed)
            h, m = map(int, last.split(":"))
            doc["start"] = f"{date}T{first}"
            doc["end"] = f"{date}T{dt.datetime(2000, 1, 1, h, m) + dt.timedelta(minutes=40):%H:%M}"
            doc["notes"] = (f"{len(games)} game{'s' if len(games) > 1 else ''} for {team}. "
                            f"{lg['kid_name']}'s team for the day comes with the call-up.")
        else:
            doc["start"] = date
            doc["notes"] = "Game times not set yet in the league schedule."
        writes.append({"op": "set", "collection": "events",
                       "doc_id": f"ev-{date.replace('-', '')}-{lg['club_id']}-{lg.get('id_suffix', 't')}{num}".lower(), "data": doc})

    json.dump(writes, sys.stdout, ensure_ascii=False, indent=1)
    print(f"\n{len(days)} match days, {games_total} games, {len(writes)} tentative events", file=sys.stderr)


if __name__ == "__main__":
    main()
