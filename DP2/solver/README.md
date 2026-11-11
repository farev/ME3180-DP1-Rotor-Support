# DP2 shaft solver

Sweeps every McMaster precision rotary shaft that can be cut to the 555 mm shaft, pairs it with every stainless retaining ring sold for that diameter, and runs the same checks as `../solution/calculate.py`: the groove, keyseat, pin hole and plain section at the bearing, plus the pin, key and ring checks.

```bash
python3 solver.py --check     # regression: reproduces calculate.py's 1.500 in numbers exactly
python3 solver.py             # ranked table, design keyseat model (Kt 3.0 / Kts 4.0 + key pressure)
python3 solver.py --table71   # same with Shigley Table 7-1 keyseat (r/d = 0.02, with q)
```

## Files

| File | What it holds |
|---|---|
| `data/shafts.csv` | Shortest stock that is at least 21.8 in long for every plain, keyed, D-profile and nitrided rotary shaft from 1-1/4 in to 2 in and 30–40 mm. Read on McMaster on 10 Nov 2026. |
| `data/rings.csv` | Every 18-8 and 15-7 PH stainless external ring for those diameters (spiral, high-load spiral, ASME B18.27.1, DIN 471), with groove sizes. |
| `data/fig_a15_16.json` | Shigley Fig. A-15-16 digitized from the local PDF by `tools/digitize_fig_a15_16.py`, for a/t from 1 to 3. |
| `data/results_*.csv` | Output tables. |

## Rules applied

- **Cost** = full price of the shortest stock long enough for the shaft, + $100 if the shaft is not stainless, + 2 rings, pin, set screw and key (prorated per item).
- **Groove root** uses the shallow end of the catalog tolerance where the part page gives one, as the P2 drawing does. Otherwise it uses the catalog nominal.
- **Groove radius** is 0.0098 in. The groove K_t is the chart value × 1.06, the same rounding that turns 3.31 into 3.5 at the 1.5 in groove.
- **Properties.** Only 1045 HB 197 has a proposed set (Marks 703/598, valid for 16–50 mm bars). Other steels get S_ut = 3.4 HB (Eq. 2-36), and the solver reports the S_y they would need.
- **Exclusions.** Keyed, D-profile and nitrided shafts are excluded; the reason is printed for each.
