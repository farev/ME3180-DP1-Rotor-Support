**Review of the 24-page DP2 submission — November 13, 2026**

Reviewed file: DP2_submission.pdf, 1,989,906 bytes, modified November 13 at 20:17:42 according to filesystem metadata. Drawing revision: P4, embedded on page 22. I inspected every rendered page and compared its text with the previous 20-page version. The submission and design files were not edited.

**Verdict:** The added calculations make this version easier to assess. I found no new pass/fail issue in the calculations I reproduced. It remains technically submit-ready under your confirmed course rules, but several minor corrections from the previous review are still outstanding. I would fix the slip-factor rounding and drawing/report consistency before upload, then clean up pagination if time permits.

Your previously confirmed permission to use Kf, approval of all material properties, and full-stock shaft pricing remain accepted. I am not reopening those questions. The $222.07 total is unchanged and correct when calculated from unrounded item costs.

**What improved**

- Pages 13–14 now show the pin-hole shaft net-section coefficients, stresses, and safety-factor substitutions. I reproduced ny = 6.3080 and nf = 2.1259.
- Page 17 now shows the screw thread-root stress components and von Mises combination. The displayed components give approximately 43.22 MPa and n = 4.74.
- Page 14 now works through the plain lower-bearing section and the groove notch-sensitivity limit.
- The bearing resultants on page 6 are separated cleanly.
- The reaction table on page 7 and stress-factor entries on page 10 no longer split numerical values across lines.
- The drawing introduction and embedded drawing both identify Rev P4. The separate drawing PDF is also available.

**Corrections still worth making**

1. **Slip factor: pages 16, 17, and 23.** The PDF still reports 1.22. From the specified 0.24 N m torque, K = 0.2, 6.35 mm screw diameter, and 25% preload reduction, Fmin = 141.7323 N. Thus nslip = 2(0.15)(141.7323)/35 = 1.214848, which rounds to **1.21**. It still passes 1.2. Correct all three occurrences.

2. **Keyseat tolerance model: page 13 versus drawing page 22.** The added calculation assumes the slot remains centered at y = -36 mm while its length grows. The drawing instead locates the first end center at 208.15 mm and measures the second from it. Holding that first location nominal, the maximum upper end is 208.15 + (12.70 + 0.43) + (9.525 + 0.051)/2 - 250.5 = **-24.432 mm**, before applying positional tolerances. The report gives -24.65 mm. Use the drawing's actual dimension chain or change the drawing to specify the center-based scheme. At -24.432 mm, the moment is 266.691 N m and the factors remain approximately ny = 5.611 and nf = 1.886; this correction alone does not change the rounded pass results.

3. **Groove radius: pages 11–12 versus pages 21–22.** Rev P4's R0.225 +/-0.025 still permits **0.200 mm**. Expressing the tolerance symmetrically did not change the lower limit. The report continues to use **0.2032 mm** (0.008 inch) as the minimum. Synchronize the calculation and drawing. Keeping the report's rounded Kt = 3.6, using r = 0.200 mm gives q about 0.6639 and Kf about 2.726; the yield and fatigue factors remain about 3.92 and 1.34. Confirm the chart interpolation using the actual geometric limits when documenting the update.

4. **Upper end margin: pages 2 and 20 versus page 22.** The drawing's nominal margin is **554 - 249.61 - 301.77 = 2.62 mm**, whereas the text says 2.56 mm. State whether the number is nominal or a tolerance-stack minimum and show the relevant stack if claiming a minimum. This discrepancy does not itself show an edge-margin failure.

5. **Load-table wrapping: page 4.** The values -48.62, +161.25, and +13.35 still wrap inside their cells. Widen these numerical columns or reduce cell padding. The word “mid-length” also breaks awkwardly across three lines.

6. **Pagination.** Page 18 contains only the screw-tip bearing equation and cost. Move these onto page 17 or allow the pin section to follow them on page 18. Table 4's final row is alone at the top of page 11; keep the table together or repeat its header. The ring section begins at the very bottom of page 19 and continues on page 20; moving its heading with its equations would improve readability. These are presentation issues, not missing content or violations of the consecutive-section requirement.

**Very small arithmetic/presentation details**

- Page 13 displays (0.168 - 0.15)/(0.175 - 0.15) = 0.714, but those displayed rounded inputs give 0.720. The unrounded hole ratio is 6.378/37.9984 = 0.167849, which gives the intended 0.713967. Display 0.16785 in the interpolation expression. The resulting coefficients and final stresses are already consistent with the unrounded calculation.
- Page 12's q for the stated 0.008-inch radius is approximately **0.6657**, rounding to **0.666**, rather than 0.667. If updating to the drawing's 0.200 mm radius, update q at the same time. Kf still rounds to 2.73 in either case.
- Page 17's hex-socket torsion expression Tr/J remains a simplified treatment of a noncircular section. Calling it an approximation would be more precise; the added algebra does not make it an exact local stress solution.
- The bending figure on page 9 still benefits from explicitly labeling the hub-region curve as a conservative envelope, as explained in the surrounding prose.
- The axial-float assertion on page 21 would be easier to assess with a short stack showing groove spacing, ring thickness limits, and the assumed bearing/support span.
- Rounded BOM rows sum to $222.06, while unrounded costs sum to $222.0697, hence the correct $222.07 total. A note about unrounded totals removes that apparent one-cent discrepancy.

**Current section mapping**

| Section | PDF pages |
| --- | --- |
| Shaft design calculations | 2–15 |
| Connection hardware | 16–20 |
| Drawing and bill of materials | 21–22 |
| Economic assessment | 23 |
| References | 24 |

The sections are consecutive. If the upload rubric separates key/set screw from pin/rings, the current ranges are 16–18 and 19–20 respectively. Reassign pages after any layout changes. The separate Canvas summary quiz remains a separate deliverable; this review does not verify its completion. The nominal grading cost is unavailable, so I cannot predict the economic bonus.

**Recommended final action:** retain the design and the new calculation detail. Correct 1.22 to 1.21, align the drawing-based tolerance statements, and fix page 4's numeric wrapping. Page 18 is the most obvious optional layout cleanup. No further wholesale expansion of the report is needed.
