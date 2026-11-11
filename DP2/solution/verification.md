# Provisional analysis P3 verification record (geometry P2)

Research session: 2026-11-08/09. The original assignment and pre-existing work were not edited.

## Calculation checks

- `calculate.py` uses N, mm and MPa and exposes all inputs and assumed coefficients.
- Transverse force equilibrium and bearing moment equilibrium were checked. The resultant bending above the upper support closes to numerical zero.
- Both yield methods are reported. The lower groove gives 4.1576 with the Shigley Kf/Kfs bending/torsion method, retaining the same small Kt-amplified axial term, and 3.0333 with the supplemental Kt/Kts elastic method.
- The keyseat controls Shigley yielding at 3.5947. At this feature Kf=Kt=3.0 and Kfs=Kts=4.0, so both yield checks agree. For ny=3, required Sy is 499.064 MPa for the whole shaft under Shigley's method versus 591.439 MPa under the added elastic criterion. The groove alone requires 431.503 MPa under the Shigley calculation.
- The P2 keyseat controls shaft fatigue at 1.2404 under the proposed 703 MPa tensile value and stated Marin/contact assumptions. Adding the second yield calculation does not change fatigue.
- The pre-existing P2 revision uses a 1/2-in-long key and 22.45 mm slot; these dimensions were preserved. The key shear and bearing factors are about 27.55 and 23.54, and its worst-case length fits the straight portion of the closed slot.
- Screw installation yield, thread/tip loading and axial slip were checked. Minimum screw factor is 1.275; axial-slip factor is 1.314.
- Pin double shear, bending, bearing and a conservative fit-pressure bound were checked. The smallest pin factor is 1.347.
- Ring allowable thrust, groove-wall bearing and shaft-end margins were checked.
- Python assertions enforce the primary Shigley shaft yield and fatigue criteria, key-slot fit and hardware checks. The elastic check is separately reported, not imposed as an undocumented acceptance rule. Equality of the two methods is checked where Kf=Kt and Kfs=Kts. These verify this model; they do not establish the material condition or replace the cited assumptions.
- Unrounded allocated cost is $165.092358; rounded cost is $165.09. This yield-method revision does not change parts, geometry or cost.

## Artifact checks

- The assembled PDF has 14 pages: shaft calculations 1-7, connection hardware 8-11, drawing/BOM 12-13, sources and approval request 14.
- All report pages were rendered and visually inspected for readable equations, tables, figures, clipping and page order.
- A separate one-page shaft drawing PDF and an editable ASCII DXF are provided. No hardware drawings are included.
- The drawing PDF and DXF are generated from the same vector entities. The DXF record structure and numeric coordinates were checked; it has not been opened in a separate CAD program.
- The catalog observation record contains 48 dated part/price entries. It records the search performed rather than claiming an exhaustive supplier-wide optimization.

## Unresolved approval and interface inputs

The 703/598 MPa shaft property set is a published representative-average proposal, not a supplier-certified minimum. It requires Piazza approval. Holding Sut=703 MPa and the stated geometry/contact assumptions fixed, the Shigley method needs Sy>=499.064 MPa. The earlier unqualified 594 MPa claim was the threshold for an additional Kt elastic criterion, not for Shigley Eq. (7-15). Changing Sut also changes fatigue and notch sensitivity; a different complete approved property set must be recalculated. Smaller-diameter cost screening originally imposed the extra Kt criterion and has not been repeated under a Shigley-only acceptance rule. Bearing face spacing, contact chamfer and axial-stack tolerance require coordination with the bearing design. Other fit, friction and material assumptions remain explicit in the report. No message was posted to Piazza, no order was placed, and no assignment was submitted.
