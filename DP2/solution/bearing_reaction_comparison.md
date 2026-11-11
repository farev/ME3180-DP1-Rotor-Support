# Bearing-reaction reconciliation - 2026-11-10

Compared the supplied `Rotor_Shaft_Chat_Transcript.pdf` with analysis revision P3 and Figure 2 of the original Rev2 assignment. The two answers use identical loads and signs, but different reaction locations. Both satisfy force and moment equilibrium for their respective geometries.

Coordinates below use the rotor CG as origin, with +y upward. The sprocket force is at y=300 mm, and water drag is at y=-150 mm. Chain components are Fx=161.2484996 N and Fz=13.3477109 N; drag is +560 N in z.

| Model | Lower reaction y (mm) | Upper reaction y (mm) | Reaction span (mm) |
|---|---:|---:|---:|
| Other chat: nominal point supports | 350.00 | 650.00 | 300.00 |
| P3 design: 12.7 mm bearings inside the dimensioned outer faces | 356.35 | 643.65 | 287.30 |

The latter uses half the selected bearing width, 6.35 mm, to move each reaction toward the interior of the support assembly. The chain overhang increases from 50 to 56.35 mm; the water-force lever arm increases from 500 to 506.35 mm.

For arbitrary reaction stations yL and yU, equilibrium gives:

```text
L = yU - yL
RUx = Fx (yL - 300) / L
RUz = [560 (yL + 150) + Fz (yL - 300)] / L
RLx = -Fx - RUx
RLz = -560 - Fz - RUz
Rradial = sqrt(Rx^2 + Rz^2)
```

| Model / bearing | Rx (N) | Rz (N) | Radial magnitude (N) |
|---|---:|---:|---:|
| Other chat / lower | -188.123 | -1508.906 | 1520.588 |
| Other chat / upper | 26.875 | 935.558 | 935.944 |
| P3 design / lower | -192.875 | -1562.934 | 1574.790 |
| P3 design / upper | 31.627 | 989.586 | 990.092 |

The P3 radial magnitudes are 3.565% larger at the lower bearing and 5.785% larger at the upper bearing. Independent checks about the rotor CG give force residuals below 2e-13 N and moment residuals below 2e-11 N mm in both cases. Changing the coordinate origin alone does not change the reactions.

## Which set to use

Figure 2's 300 mm dimension extension lines visually align with the outside support/bearing faces. This supports the finite-width interpretation used in the current shaft design. Requirement 8 only specifies bearing width <=12.7 mm; it does not specify an exact width. Consequently, the P3 results are conditional on choosing the maximum allowed width and representing each radial reaction at the bearing midplane. This gives a conservative reaction case for bearings contained inside those outer faces. Use 1574.79 N lower and 990.09 N upper for the current design model.

The other chat explicitly states that it uses nominal point supports. Its 1520.59 N lower and 935.94 N upper are correct for that idealization, or for a clarified geometry with a true 300 mm center-to-center reaction span. They are not the exact reactions for the P3 finite-width layout. Final selected bearing dimensions or an instructor clarification can fix the remaining geometric assumption.

## Separate axial-load difference

The transcript neglects shaft weight and assigns the upper bearing Ry=120+35=155 N. P3 includes a conservative full-cylinder shaft weight of 48.623 N, giving upper Ry=203.623 N. Both assume the upper retaining-ring/bearing path carries gravity and no axial preload. Centered axial weights do not change Rx, Rz or the radial magnitudes in this comparison.

No shaft geometry or calculation results were changed during this reconciliation.
