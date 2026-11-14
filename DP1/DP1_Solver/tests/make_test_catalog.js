// TEST ONLY: provisional catalog from the 8 Oct data (layout testing before the 14 Oct sweep lands)
const c = require('./old_catalog_adapter.js'), fs = require('fs');
c.meta = { date: '8 Oct 2026 (provisional test data)' };
for (const b of c.beams) { b.family = b.family || ''; if (b.mat.startsWith('ss')) { b.ro_in = 2 * b.t_in; b.ri_in = b.t_in; } else if (b.mat === 'al6061') { b.ro_in = b.t_in; b.ri_in = b.t_in / 2; } }
for (const p of c.pins) { p.material = p.matKey === 'ss188' ? '18-8 stainless steel' : '316 stainless steel'; p.retention = 'cotter hole; TEST retainer'; }
fs.writeFileSync('dp1-catalog.js', '/* PROVISIONAL TEST CATALOG */\n(function(){var C=' + JSON.stringify(c) + ';if(typeof module!=="undefined"&&module.exports)module.exports=C;else window.DP1_CATALOG=C;})();\n');
