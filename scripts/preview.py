"""Open the board locally, without Claude, using sample or dumped data.

    python3 scripts/build_board.py --config private.example/family.json
    python3 scripts/preview.py --data config/sample-db.json      # writes dist/preview.html
    open dist/preview.html                                        # or any browser

--data is either one JSON file {"events": {"<id>": {...}}, "routine": {...}, ...}
or a folder with <collection>/<id>.json files (ArtifactData "list" with out_dir).
--now freezes the clock (e.g. 2026-10-09T09:30:00+02:00) so screenshots are stable.

The preview replaces the Claude runtime (window.claude) with an in-memory stand-in:
answers, ticks and new events work until you reload, nothing is saved, and
"Fill in from a message" returns nothing.
"""
import argparse, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

MOCK = r"""<script>
(function(){var D=%DATA%;
%CLOCK%
function snap(col){var docs=Object.keys(D[col]||{}).map(function(k){return {id:k,exists:true,data:function(){return D[col][k]}}});return {docs:docs,size:docs.length,empty:!docs.length,docChanges:function(){return[]},metadata:{}}}
var subs={};function emit(c){(subs[c]||[]).forEach(function(n){n(snap(c))})}
function ref(c,id){return {update:function(x){D[c]=D[c]||{};D[c][id]=Object.assign({},D[c][id]||{},x);setTimeout(function(){emit(c)},0);return Promise.resolve()},set:function(x){D[c]=D[c]||{};D[c][id]=x;setTimeout(function(){emit(c)},0);return Promise.resolve()},delete:function(){if(D[c])delete D[c][id];setTimeout(function(){emit(c)},0);return Promise.resolve()}}}
var db={collection:function(c){return {onSnapshot:function(n){(subs[c]=subs[c]||[]).push(n);setTimeout(function(){n(snap(c))},10);return function(){}},doc:function(id){return ref(c,id)}}},doc:function(c,id){if(id===undefined){var p=String(c).split("/");id=p.pop();c=p.join("/")}return ref(c,id)}};
window.claude={use:function(n){return Promise.resolve(n==="db"?db:n==="user"?{can:function(){return Promise.resolve(true)}}:n==="downloads"?{save:function(){}}:n==="assets"?{upload:function(){return Promise.resolve({id:"x",contentType:"image/png",sizeBytes:1})}}:n==="sample"?Object.assign(function(){},{json:function(){return Promise.resolve({})},limits:function(){return Promise.resolve({images:{maxCount:4,mediaTypes:["image/png","image/jpeg"]}})}}):null)}};
})();
</script>"""

CLOCK = """(function(){var off=new Date(%NOW%).getTime()-Date.now();var _D=Date;
window.Date=class extends _D{constructor(...a){if(!a.length)super(_D.now()+off);else super(...a)}static now(){return _D.now()+off}};})();"""


def load(path):
    p = pathlib.Path(path)
    if p.is_dir():
        return {c.name: {f.stem: json.loads(f.read_text()) for f in sorted(c.glob("*.json"))}
                for c in sorted(p.iterdir()) if c.is_dir()}
    return json.loads(p.read_text())


def make_preview(page_html, data, now=None):
    """The board page wrapped with the in-memory runtime and the given data."""
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    clock = CLOCK.replace("%NOW%", json.dumps(now)) if now else ""
    head = ('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" '
            'content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light}'
            'body{margin:0}[hidden]{display:none!important}</style></head><body>')
    return head + MOCK.replace("%DATA%", blob).replace("%CLOCK%", clock) + page_html + "\n</body></html>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "config/sample-db.json"))
    ap.add_argument("--page", default=str(ROOT / "dist/index.html"))
    ap.add_argument("--out", default=str(ROOT / "dist/preview.html"))
    ap.add_argument("--now", help="freeze the clock, ISO time with offset")
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.write_text(make_preview(pathlib.Path(a.page).read_text(), load(a.data), a.now))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
