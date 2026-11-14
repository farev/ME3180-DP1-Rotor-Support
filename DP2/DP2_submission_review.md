**DP2 submission review — November 13, 2026**

**Verdict: technically ready under the course clarifications you confirmed, with several small corrections recommended before submission.** I did not find a demonstrated failure of the required shaft or hardware safety factors under your stated models. I would keep the design, correct the set-screw rounding, make the numerical tables readable, and add working for two abbreviated checks. The submission PDF and design files were not modified.

I reviewed all 20 rendered submission pages against the four-page Rev. 2 assignment, independently recomputed the main numerical results, compared the drawing with the calculations, and checked selected cited references. Existing project scripts and notes helped trace inputs; I did not treat their assertions as independent proof. Older verification notes describe a different revision and do not verify this PDF.

Page numbers below count the cover as page 1.

**1. Course clarifications resolve the original compliance concerns.**

You confirmed that the course permits Kf for the yield calculation, that all material properties are approved, and that the shaft is charged at the full stock price. Those clarifications govern this review. Therefore:

- The Kf-based shaft yield factor of 3.92 is acceptable. I also verified that Shigley's 11th-edition Eq. (7–15) uses Kf and Kfs for this shaft calculation. The supplemental Kt result of 2.97 does not disqualify the design under your confirmed course method.
- The use of Sy = 88 ksi and Sut = 860.2 MPa is accepted based on your confirmation of approval.
- The $112.69 full-stock shaft cost and $222.07 total are accepted. I am withdrawing the proposed prorated-cost correction; it does not apply under your clarification.

For a self-contained report, cite or briefly identify the relevant course clarifications on pages 11–13 and 19. The original Rev. 2 wording alone would otherwise leave the cost interpretation and derived tensile strength ambiguous. There is no need to seek approval again if it has already been given.

The nominal cost used for the economic grading tiers is not in the available brief, so I cannot verify the cost bonus or predict the final grade. I also could not independently refresh McMaster pricing through the available web reader; price arithmetic was checked using your recorded prices.

Source checked: [Shigley's Mechanical Engineering Design, 11th edition, chapter 7](https://studylib.net/doc/26107230/shigley-s-mechanical-engineering-design), equations (7–15) and (7–16). The same source confirms the 11th-edition surface-factor coefficients used in your PDF.

**2. Correct the set-screw slip factor — pages 14–15 and 19.**

With the selected torque and the report's assumptions:

\[
F_{min}=\frac{240}{0.2(6.35)}(0.75)=141.7323\text{ N},\qquad
n_{slip}=\frac{2(0.15)(141.7323)}{35}=1.214848.
\]

This rounds to **1.21**, not 1.22. It still passes the required 1.2. Correct the repeated value in the hardware introduction and compliance table as well as the calculation.

The slip result depends on your stated dry-contact coefficient, two-contact friction model, and preload variation. Keep the assumed contact condition and 0.24 N m installation torque explicit. The margin above 1.2 is small, but that alone is not a violation. For sensitivity only, substituting mu = 0.10 into the same model gives n = 0.810; this is not evidence that the actual joint has that coefficient. A torque increase is an optional design choice, not a required redesign established by this review, and would require updating the other screw checks.

The cited [Unbrako Engineering Guide](https://unbrako.com/docs/engguide.pdf) discusses torque/preload variability. [ATI's 304 data](https://www.atimaterials.com/Products/ati-304) support the quoted 515 MPa tensile and 205 MPa yield baseline for annealed flat products; those published values do not independently certify individual McMaster fasteners.

**3. Show the intermediate calculations for two reported results — pages 13 and 15.**

The assignment asks for calculations necessary to justify results. The pin-hole shaft safety factors and governing screw thread-root stress are mostly stated as final numbers. I reproduced both, but adding a few lines would make them much easier to grade.

For the shaft through the pin hole, show the distinct net-section coefficients Ab = 0.73144 and At = 0.85572, then:

\[
\sigma_b=\frac{32M}{\pi D^3 A_b}=45.227\text{ MPa},\qquad
\tau_t=\frac{16T}{\pi D^3 A_t}=2.1294\text{ MPa}.
\]

With Kt = 2.11430, Kts = 1.60572, and the stated mean axial term, the calculation gives ny = 6.3080 and nf = 2.1259. Label Ab and At separately; the single “A” used for two coefficients is easy to misread.

For the screw thread-root model, your load split and geometry give sigma_x = 28.72 MPa, sigma_y = -13.61 MPa, tau_yz = 11.77 MPa, and tau_zx = 4.14 MPa. Show the equations and von Mises combination leading to 43.22 MPa and n = 4.744, and identify the thread engagement assumption. This is a presentation gap, not an arithmetic failure.

The separate screw socket-section check uses a simplified torsional model for a section with a hexagonal opening. Its use of polar moment and Tr/J should be described as an approximation, rather than an exact local stress solution for that noncircular section.

**4. Reconcile the small drawing/report differences — pages 8, 11–12, and 16–18.**

The A3 drawing is present, is vector content, includes the major shaft features, and also exists as a separate PDF. I found no obviously missing major shaft feature. These details should nevertheless agree:

- **Groove radius:** the drawing allows 0.20–0.25 mm; the calculation calls the minimum 0.008 inch = 0.2032 mm. Use the actual drawing limit when describing the worst-case calculation, or synchronize the callout. The difference is small; this review has not established a pass/fail reversal from it.
- **Keyseat position tolerance:** the drawing fixes the first end center at 208.15 mm from the bottom, then dimensions the center spacing 12.70 +0.43/0. The calculation instead assumes the slot grows symmetrically about a fixed center. With the first center held at nominal, the longest, widest slot reaches y = 208.15 + 13.13 + 9.576/2 - 250.5 = **-24.432 mm**, rather than -24.65 mm, before adding positional tolerances. Use the drawing's dimension chain for a claim about the worst case. This changes the moment only slightly relative to the keyseat's margin.
- **Upper end margin:** the nominal value from the drawing is 554 - 249.61 - 301.77 = **2.62 mm**, not 2.56 mm. A guaranteed minimum should use a tolerance stack. Both quoted nominal values exceed the cited three-depth approximation.
- **Axial float:** add the short stack behind the claim of at least 0.20 mm, including ring thickness limits and the assumed bearing/support span. The brief does not supply the bearing-interface tolerances, so identify them as assumptions.
- **Coating:** a note about protecting precision fits during painting would make the manufacturing intent clearer, although the drawing already assigns painting to others.

The [Smalley ring-design guidance](https://www.smalley.com/engineering-support/ring-design) supports the cited 0.010-inch maximum groove-bottom radius for shafts over one inch and the approximate three-depth edge-margin rule. It also distinguishes ring shear capacity from groove deformation capacity and emphasizes contact geometry. Your large ring margins make this primarily a documentation/interface issue, rather than an identified capacity failure.

**5. Main numerical results verified.**

These results reproduce your stated models. They are not independent certification of the material condition, catalog ratings, or every contact assumption.

| Check | Independently calculated result | Assessment |
| --- | ---: | --- |
| Chain Fx, Fz | 161.2485 N, +13.3477 N | Matches |
| Upper bearing Rx, Rz | +31.6267 N, +989.5863 N | Matches |
| Lower bearing Rx, Rz | -192.8752 N, -1562.9340 N | Matches |
| Shaft weight / total thrust | 48.6228 N / 203.6228 N | Matches |
| Maximum nominal bending moment | 284.4533 N m | Matches |
| Lower groove bending / torque | 280.4979 N m / 0 | Matches |
| Machined endurance limit | 206.3108 MPa | Matches |
| Lower groove ny / nf | 3.9161 / 1.3361 | Passes confirmed course method |
| Keyseat ny / nf | 5.6132 / 1.8866 | Matches reported analytical location |
| Pin-hole shaft ny / nf | 6.3080 / 2.1259 | Matches stated envelope model |
| Key shear / bearing factors | 26.6915 / 15.2395 | Matches |
| Screw thread-root factor | 4.7437 | Matches stated model |
| Pin rated double-shear factor | 30.7910 | Matches stated rating; fracture basis |
| Ring rating / groove-wall factors | 108.1347 / 70.3467 | Matches stated capacities/model |
| Total from unrounded costs | $222.0697 | Rounds to $222.07 |

The bearing-face interpretation is supported by the assignment sketch and explained in the PDF. The signs of the chain-force components and bearing reactions are consistent. The lower groove correctly governs over the plain lower-bearing section despite the latter's slightly larger moment. Fully reversed bending and steady torque are consistent with your load assumptions, and the infinite-life calculation includes the stated surface, size, and reliability reductions.

The pin's 30.8 factor is specifically a rated double-shear fracture check. It should not be presented as proving every possible pin failure mode. The contact calculation is an additional assumed model; it does not by itself establish pin bending strength. I did not identify a demonstrated pin failure and would not label it one without a fuller joint model or a course-specific requirement. The PDF already distinguishes the fracture basis, which is useful.

**6. Fix visible layout issues; keep the successful structure.**

- Tables on pages **4, 7, and 10** wrap numbers within a cell: examples include -48.62, -192.88, 2.114, and 1.606. Widen numeric columns or reduce padding; keep numerical entries unbroken.
- On page **6**, the upper-bearing resultant's answer wraps to a separate centered line. Put the two resultants on separate equations.
- On page **9**, label the bending curve inside the hub as an assumed conservative envelope directly in the figure or its caption. The prose explains this, but the figure otherwise resembles a literal internal-moment diagram despite its nonzero value at the shaft's bottom.
- The rounded BOM line items sum to $222.06, while summing unrounded costs gives $222.07. A note that totals use unrounded values resolves the one-cent discrepancy.
- Reference 11 describes an IT14 table but is also cited for the F7 hole deviations. Identify the relevant fit-table reference too. Direct catalog links and the precise Piazza post reference would improve traceability.
- **Footer correction to my earlier observation:** extracted PDF text contains a stale “3/18” on page 4, but a high-resolution rendering confirms that it is covered. The visible footer correctly reads “4/20”; there is no visible duplicate-footer defect to fix.

The required sections are consecutive:

| Submission section | PDF pages |
| --- | --- |
| Shaft design calculations | 2–13 |
| Connection hardware | 14–16 |
| Drawing and bill of materials | 17–18 |
| Economic assessment | 19 |
| References | 20 |

The separate drawing is solution/cad/DP2-S01_Rotor_Shaft.pdf. Keep the consecutive page organization when revising and update the Gradescope page assignments if pagination changes. The brief separately calls for the Canvas summary quiz; reviewing the PDF does not verify that the quiz has been completed.

**Submission recommendation:** retain the design. Prioritize the 1.21 correction, the wrapped numerical entries, and the two short calculation expansions. Synchronize the small drawing/report differences if time permits. With your course clarifications, I would be comfortable submitting after those cleanup edits; I found no reason to restart the design or change the shaft solely on the basis of this review.
