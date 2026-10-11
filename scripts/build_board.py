"""Build the board page and the scheduled-task prompts from the templates.

    python3 scripts/build_board.py                      # uses private/family.json
    python3 scripts/build_board.py --config config/family.example.json

Writes
    dist/index.html          the board, one self-contained file (publish this)
    dist/tasks/<name>.txt    the prompt to paste into each scheduled task

Templates use {{path.to.value}} placeholders, filled from the config. Filters:
{{x|js}} escapes for a single-quoted JavaScript string, {{x|curly}} turns ' into ’.
Generated values live under "js." (see js_values below).

The board must stay ONE file: a separate logos.json published next to the page
was refused ("Forbidden") for people the board is shared with. Club logos are
inlined from private/logos.json when that file exists (they are the clubs'
property, so they are not in the repository); without it the board shows
initials instead of logos.
"""
import argparse, copy, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKEN = re.compile(r"\{\{\s*([A-Za-z0-9_.]+)(?:\|([a-z]+))?\s*\}\}")
ID = re.compile(r"^[a-z][a-z0-9_]*$")


def js_values(cfg):
    clubs = cfg["clubs"]
    obj = lambda f: "{" + ",".join(f'{c["id"]}:{json.dumps(f(c), ensure_ascii=False)}' for c in clubs) + "}"
    match = "||".join(f'(e.club==={json.dumps(c["id"])}&&/{c["match"]}/i.test(t))' for c in clubs if c.get("match"))
    return {
        "ownclub": obj(lambda c: c.get("logo_name") or c["id"]),
        "clubsport": obj(lambda c: c["sport"]),
        "own_match": match or "false",
        "fill_club_ids": ",".join(json.dumps(c["id"]) for c in clubs),
    }


def context(cfg):
    for k in ("kids", "adults"):
        if len(cfg.get(k, [])) != 2:
            sys.exit(f"config: '{k}' must list exactly two people (the board has two lanes)")
    for p in cfg["kids"] + cfg["adults"] + cfg["clubs"]:
        if not ID.match(p["id"]):
            sys.exit(f"config: id {p['id']!r} must be lower case letters, digits or _ (it is used as a CSS class)")
    ids = [p["id"] for p in cfg["kids"] + cfg["adults"]] + ["both"]
    if len(set(ids)) != len(ids):
        sys.exit("config: kid and adult ids must be different from each other and from 'both'")
    ctx = copy.deepcopy(cfg)
    ctx["kid1"], ctx["kid2"] = cfg["kids"]
    ctx["adult1"], ctx["adult2"] = cfg["adults"]
    ctx["js"] = js_values(cfg)
    return ctx


def lookup(ctx, path):
    v = ctx
    for part in path.split("."):
        if isinstance(v, dict) and part in v:
            v = v[part]
        elif isinstance(v, list) and part.isdigit() and int(part) < len(v):
            v = v[int(part)]
        else:
            raise KeyError(path)
    if not isinstance(v, str):
        raise KeyError(path + " (not text)")
    return v


FILTERS = {
    None: lambda s: s,
    "js": lambda s: s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n"),
    "curly": lambda s: s.replace("'", "’"),
}


def render(text, ctx, where):
    missing = []

    def sub(m):
        try:
            return FILTERS[m.group(2)](lookup(ctx, m.group(1)))
        except KeyError as e:
            missing.append(str(e).strip("'"))
            return m.group(0)

    out = TOKEN.sub(sub, text)
    if missing:
        sys.exit(f"{where}: missing in config: {', '.join(sorted(set(missing)))}")
    if "{{" in out:
        sys.exit(f"{where}: unfilled placeholder left: {out[out.index('{{'):][:60]!r}")
    return out


def prompt_of(md):
    m = re.search(r"## Prompt\n\n```text\n(.*?)\n```", md, re.S)
    if not m:
        raise ValueError("no ## Prompt block")
    return m.group(1)


def build(cfg_path, out_dir):
    cfg = json.loads(pathlib.Path(cfg_path).read_text())
    ctx = context(cfg)
    out_dir.mkdir(parents=True, exist_ok=True)

    src = (ROOT / "board/index.src.html").read_text()
    page = render(src, ctx, "board/index.src.html")
    logos_file = ROOT / "private/logos.json"
    logos = logos_file.read_text() if logos_file.exists() else '{"v":2,"l":[]}'
    json.loads(logos)  # fail early on a broken file
    tag = "<script>window.__LOGOS=" + logos.replace("</", "<\\/") + ";if(window.__setLogos)window.__setLogos(window.__LOGOS);</script>"
    assert page.count("<!--LOGOS-->") == 1
    page = page.replace("<!--LOGOS-->", tag)
    (out_dir / "index.html").write_text(page)
    print(f"wrote {out_dir / 'index.html'} ({len(page.encode()):,} bytes, logos: {'yes' if logos_file.exists() else 'none'})")

    (out_dir / "tasks").mkdir(exist_ok=True)
    for md in sorted((ROOT / "tasks").glob("*.md")):
        txt = render(prompt_of(md.read_text()), ctx, str(md.relative_to(ROOT)))
        (out_dir / "tasks" / (md.stem + ".txt")).write_text(txt)
        print(f"wrote {out_dir / 'tasks' / (md.stem + '.txt')} ({len(txt):,} chars)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", default=str(ROOT / "private/family.json"))
    ap.add_argument("--out", default=str(ROOT / "dist"))
    a = ap.parse_args()
    if not pathlib.Path(a.config).exists():
        sys.exit(f"{a.config} not found. Copy config/family.example.json to private/family.json and fill it in.")
    build(a.config, pathlib.Path(a.out))
