# Yield-method correction - analysis P3, 2026-11-09

Source: Budynas and Nisbett, *Shigley's Mechanical Engineering Design*, 10th edition, section 3-13, Eq. (3-48), and section 7-4, Eqs. (7-15)-(7-16), printed page 362 (PDF page 385).

Public copy consulted: https://www.mechfamily-ju.com/storage/images/files/file_1731443577xeDvd.pdf#page=385

The text's shaft-specific maximum-equivalent-stress equation uses Kf for bending and Kfs for torsion, then ny=Sy/sigma_max. It does not directly include axial force. Its geometric-factor definition elsewhere uses Kt/Kts to relate nominal and theoretical local elastic stresses.

The earlier report used the latter factors to impose a stricter local elastic stress limit. That is a defensible additional check, but the assignment did not specifically require it and the report should not have described its 594 MPa threshold as the sole requirement. Analysis P3 presents the Shigley method as primary and the elastic check separately.

For a direct comparison, both implemented checks retain the existing 0.660734 MPa axial term at the lower groove. Thus:

- Kf=2.5503507: sigma_max=144.345720 MPa, ny=4.142832, required Sy=433.037161 MPa.
- Kt=3.5: sigma_max=197.848299 MPa, ny=3.022518, required Sy=593.544896 MPa.
- The keyseat, where both factor sets agree, instead governs the Shigley shaft check: sigma_max=166.907655 MPa, ny=3.582819, required Sy=500.722966 MPa.

All results use the preserved P2 geometry, Sut=703 MPa and Sy=598 MPa. The reported yield-strength thresholds vary Sy alone, holding Sut and the other inputs fixed. Fatigue and hardware calculations are unchanged. No claim is made that passing the Kf-based calculation also certifies the stricter Kt-based margin.
