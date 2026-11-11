"""Digitize Shigley 11th ed. Fig. A-15-16 (flat-bottom groove, bending) from the local PDF.

Needs pdftoppm and Pillow. Writes ../data/fig_a15_16.json: {r_over_t: [[a_over_t, Kt], ...]}.
Axis calibration was read from gridlines at 330 dpi (PDF page 1068):
  x: log scale, a/t = 0.5 at px 1009 and 6.0 at px 1977 (the printed '2.0' label is misplaced;
     the r/t=0.40, 0.60, 1.00 curves start at a/t = 0.8, 1.2, 2.0 = 2r/t on this calibration)
  y: Kt = 2 + (1453 - px)/134.7  (gridlines every 0.5)
Usage: python digitize_fig_a15_16.py /path/to/Mechanical_Engineering_Design.pdf
"""
import sys, json, math, subprocess, tempfile
from pathlib import Path
from PIL import Image

pdf = sys.argv[1]
tmp = Path(tempfile.mkdtemp())
subprocess.run(['pdftoppm', '-f', '1068', '-l', '1068', '-r', '330', '-png', pdf, str(tmp/'p')], check=True)
im = Image.open(next(tmp.glob('p*.png'))).convert('L')
X0, X1 = 1009, 1977
xpx = lambda at: X0 + math.log(at/0.5)/math.log(12)*(X1-X0)
kt = lambda y: 2 + (1453 - y)/134.7
CURVES = [0.03, 0.04, 0.05, 0.07, 0.10, 0.15, 0.20, 0.40, 0.60, 1.00]
START = {0.40: 0.8, 0.60: 1.2, 1.00: 2.0}
out = {c: [] for c in CURVES}
for at in [1.0,1.05,1.15,1.25,1.35,1.45,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.4,2.5,2.8,3.0]:
    X = round(xpx(at)); runs = []; inr = False
    for y in range(640, 1450):          # below the inset sketch
        v = im.getpixel((X, y))
        if v < 110 and not inr: s = y; inr = True
        if v >= 110 and inr: runs.append((s+y)/2); inr = False
    present = [c for c in CURVES if at >= START.get(c, 0) + 0.06]
    if len(runs) == len(present):
        top = present
    elif len(runs) == len(present) - 1:
        top = present[1:]          # 0.03 curve hidden under the inset (y < 640)
    else:
        print('ambiguous', at, len(runs), present); continue
    for c, y in zip(top, runs):
        out[c].append([at, round(kt(y), 3)])
json.dump({str(k): sorted(v) for k, v in out.items() if v}, open(Path(__file__).parent.parent/'data'/'fig_a15_16.json', 'w'), indent=1)
print({k: len(v) for k, v in out.items()})
