// Shows which logo each team name gets.  node scripts/logos/test_matching.js
// Names come from "logo_tests" in private/family.json ("sport:Name" for non-handball);
// logos from private/logos.json. Both are private, so the output never lands in git.
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..', '..');
const eng = require('./match_engine.js');
const logosFile = path.join(root, 'private', 'logos.json');
if (!fs.existsSync(logosFile)) { console.log('no private/logos.json: nothing to match against'); process.exit(0); }
eng.buildLogoIdx(JSON.parse(fs.readFileSync(logosFile, 'utf8')).l);
const cfgFile = process.env.FAMILY_CONFIG || path.join(root, 'private', 'family.json');
const cfg = JSON.parse(fs.readFileSync(cfgFile, 'utf8'));
const names = (cfg.logo_tests || []).concat(Object.keys(eng.OWNCLUB).map(id => eng.CLUBSPORT[id] + ':' + eng.OWNCLUB[id]));
let hit = 0;
for (const t of names) {
  const m = /^(handball|basketball|volleyball|swimming):(.*)$/.exec(t), sport = m ? m[1] : 'handball', n = m ? m[2] : t;
  const x = eng.logoFor(n, sport); if (x) hit++;
  console.log(n.padEnd(30), '->', x ? x[0] + ': ' + x[1][0] : '—');
}
console.log(`${hit}/${names.length} names matched a logo`);
