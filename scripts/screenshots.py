"""Take README screenshots of the board with personal details blurred.

    pip install playwright pillow          # Chromium: python3 -m playwright install chromium
    python3 scripts/build_board.py
    python3 scripts/screenshots.py --data db --now 2026-10-12T08:00:00+02:00

--data is a dump of your board (ArtifactData "list" with out_dir) or a JSON file.
Writes PNGs to docs/screenshots/.

What gets hidden: every value and private_terms entry from private/family.json
(names, clubs, school…), plus places, team names, opponents and club details found
in the data. Each match is first swapped for random letters of the same length and
then blurred, so the blur has nothing real underneath. Club logos and the kids'
initials are blurred too. Always look at the images before committing them.
"""
import argparse, asyncio, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from preview import load, make_preview  # noqa: E402
import check_private  # noqa: E402

SHOTS = [  # name, view, width, height, scheme
    ("up-next-phone", "overview", 390, 844, "light"),
    ("week-desktop", "week", 1280, 860, "light"),
    ("overview-desktop-dark", "overview", 1280, 860, "dark"),
    ("school-work-phone", "timetable", 390, 844, "light"),
    ("month-phone-dark", "calendar", 390, 844, "dark"),
]

REDACT_JS = r"""(terms) => {
  const res = terms.map(t => new RegExp((/^\w/.test(t) ? '(?<![\\p{L}\\p{N}])' : '') + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + (/\w$/.test(t) && t.length <= 4 ? '(?![\\p{L}\\p{N}])' : ''), 'giu'));
  const scramble = s => s.replace(/\p{Lu}/gu, () => 'ABCDEFGHJKLMNPRSTUVW'[Math.random()*20|0])
                         .replace(/\p{Ll}/gu, () => 'abcdefghijklmnoprstuvw'[Math.random()*22|0])
                         .replace(/\d/g, () => String(Math.random()*10|0));
  const st = document.createElement('style');
  st.textContent = '.rx{filter:blur(4px);display:inline-block} img.crest{filter:blur(3.5px)} .av{filter:blur(2.5px)} .cav{filter:blur(2px)}';
  document.head.appendChild(st);
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {acceptNode: n =>
    n.parentElement && !n.parentElement.closest('script,style,.rx') && n.nodeValue.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT});
  const nodes = []; while (walker.nextNode()) nodes.push(walker.currentNode);
  let hits = 0;
  for (const node of nodes) {
    let text = node.nodeValue, spans = [];
    for (const re of res) { re.lastIndex = 0; let m; while ((m = re.exec(text))) { spans.push([m.index, m.index + m[0].length]); if (!m[0].length) re.lastIndex++; } }
    if (!spans.length) continue;
    spans.sort((a, b) => a[0] - b[0]);
    const merged = []; for (const s of spans) { const l = merged[merged.length - 1]; if (l && s[0] <= l[1]) l[1] = Math.max(l[1], s[1]); else merged.push(s.slice()); }
    const frag = document.createDocumentFragment(); let pos = 0;
    for (const [a, b] of merged) {
      if (a > pos) frag.appendChild(document.createTextNode(text.slice(pos, a)));
      const sp = document.createElement('span'); sp.className = 'rx'; sp.textContent = scramble(text.slice(a, b)); frag.appendChild(sp); pos = b; hits++;
    }
    if (pos < text.length) frag.appendChild(document.createTextNode(text.slice(pos)));
    node.parentNode.replaceChild(frag, node);
  }
  document.querySelectorAll('.av').forEach(a => { if (!a.querySelector('svg')) a.textContent = scramble(a.textContent); });
  return hits;
}"""


def private_terms(cfg_path, data):
    """Words to hide: the leak checker's list plus places, teams and club details from the data."""
    cfg = json.loads(pathlib.Path(cfg_path).read_text())
    terms = set()
    for v in check_private.leaves(cfg):
        v = v.split(":", 1)[1] if v.startswith(("basketball:", "volleyball:", "swimming:", "handball:")) else v
        v = v.strip()
        if 3 <= len(v) <= 60 and not v.replace(":", "").isdigit() and v.lower() not in check_private.GENERIC:
            terms.add(v)
    for p in cfg.get("kids", []) + cfg.get("adults", []):
        terms.add(p["name"])
    def add(v):
        if isinstance(v, str):
            for part in re.split(r"\s*(?:,|\(|\)| / |\||·)\s*", v):
                part = part.strip()
                if len(part) >= 3 and part.lower() not in check_private.GENERIC:
                    terms.add(part)
    for e in data.get("events", {}).values():
        add(e.get("place")); add(e.get("team"))
        for g in e.get("games") or []:
            add(g.get("home")); add(g.get("away")); add(g.get("place"))
    for r in data.get("routine", {}).values():
        add(r.get("place"))
    for t in data.get("timetable", {}).values():
        add(t.get("place"))
    for c in data.get("clubs", {}).values():
        for k in ("name", "short", "team", "contact", "web", "system"):
            add(c.get(k))
    return sorted(terms, key=len, reverse=True)


async def shoot(html, terms, out_dir, scale):
    from playwright.async_api import async_playwright
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = ROOT / "dist" / "_screens.html"
    tmp.write_text(html)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, view, w, h, scheme in SHOTS:
            ctx = await b.new_context(viewport={"width": w, "height": h}, color_scheme=scheme, device_scale_factor=scale)
            pg = await ctx.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            await pg.goto(tmp.as_uri() + "#" + view)
            await pg.wait_for_timeout(800)
            hits = await pg.evaluate(REDACT_JS, terms) if terms else 0
            await pg.wait_for_timeout(100)
            await pg.screenshot(path=str(out_dir / f"{name}.png"))
            print(f"{name}.png  ({hits} redactions{', errors: ' + '; '.join(errors) if errors else ''})")
            await ctx.close()
        await b.close()
    tmp.unlink()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--config", default=str(ROOT / "private/family.json"))
    ap.add_argument("--page", default=str(ROOT / "dist/index.html"))
    ap.add_argument("--out", default=str(ROOT / "docs/screenshots"))
    ap.add_argument("--now")
    ap.add_argument("--scale", type=float, default=2)
    ap.add_argument("--no-redact", action="store_true", help="for fictional data only")
    a = ap.parse_args()
    data = load(a.data)
    terms = [] if a.no_redact else private_terms(a.config, data)
    html = make_preview(pathlib.Path(a.page).read_text(), data, a.now)
    asyncio.run(shoot(html, terms, pathlib.Path(a.out), a.scale))


if __name__ == "__main__":
    main()
