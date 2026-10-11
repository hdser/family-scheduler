// Loads the logo-matching code straight out of the built board (dist/index.html),
// so the tests always exercise exactly what the page runs. No copy to keep in sync.
//   const eng = require('./match_engine.js'); eng.logoFor("IK Sävehof 2", "handball")
const fs = require('fs'), path = require('path'), vm = require('vm');
const root = path.join(__dirname, '..', '..');
const page = fs.readFileSync(path.join(root, 'dist', 'index.html'), 'utf8');
const a = page.indexOf('/* ---------- club logos'), b = page.indexOf('function logoUrl(', a);
if (a < 0 || b < 0) throw new Error('logo engine not found in dist/index.html; run scripts/build_board.py first');
const ctx = { console };
vm.createContext(ctx);
vm.runInContext(page.slice(a, b) + '\nthis.api={nrm,coreName,buildLogoIdx,logoFor,OWNCLUB,CLUBSPORT};', ctx);
module.exports = ctx.api;
