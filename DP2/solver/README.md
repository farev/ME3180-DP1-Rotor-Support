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
- **Groove root** is the catalog nominal for every ring, the deep end of the Rev P3 callout (1.456–1.460 in for the 1.5 in ring).
- **Groove radius** is 0.008 in, the small end of the R 0.008–0.010 in callout. The groove K_t is the chart value read to one decimal, as in Shigley Example 7-2 (3.58 → 3.6 at the 1.5 in groove). `--check` still reproduces the P2 groove (shallow root, R 0.0098 in).
- **Yield** passes on Shigley Eq. 7-15 (K_f/K_fs). The K_t elastic peak (`nyKt`) is printed for information only.
- **Keyseat** (default model `peterson`): ASME B17.1 Class 1 keyseat with the Table 5 floor fillet (1/32 in for H/2 up to 1/4 in), Peterson's end-milled keyseat K_t/K_ts fits (Pilkey §5.2) with K_f = K_t, no key-pressure term. Key length 1/2 in h14, slot end centres H14 (ISO 286 IT14); key bearing height less the B17.1 key chamfer. `--harsh` keeps the old P2 keyseat model for `--check`.
- **Pin**: 1/4 in 416 dowel (98380A556, or 98380A560 for hubs over 3 in), checked against McMaster's 7200 lbf double-shear breaking strength; shaft hole 6.35 F7, pin at y = −185 mm.
- **Properties.** S_y from the Piazza-approved list; S_ut = 3.4 HB (Eq. 2-36), with HRC converted by ASTM E140.
- **Exclusions.** Keyed, D-profile and nitrided shafts are excluded; the reason is printed for each.
