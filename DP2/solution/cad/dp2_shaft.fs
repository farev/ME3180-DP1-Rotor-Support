// DP2 rotor shaft, Rev P4. Paste below the "FeatureScript ####; import(path : "onshape/std/geometry.fs", ...)"
// header that Onshape puts at the top of a new Feature Studio, then add the "DP2 rotor shaft" feature to a Part Studio.
// Axis along +X, bottom (rotor-hub) end at X = 0. Station X = y + 250.5 mm, where y is the report coordinate.
// Keyseat opens toward +Z; the pin hole is drilled along Z (same set-up as the keyseat).
// Model values are the drawing nominals (mm):
//   stock McMaster 1346K534, OD 38.100 (1.500 in, -0.004/0), cut 554 long
//   pin hole 6.35 F7 at X = 65.50 (y = -185)
//   keyseat ASME B17.1 Class 1: W 9.525 +0.051/0, end-centre 12.70 H14, S 32.733 +0/-0.381, floor R 0.79, centre X = 214.50 (y = -36)
//   ring grooves for 93576A210: root 37.033 +/-0.051 (36.982-37.084), width 0.787 +0.051/0, root R 0.225 +/-0.025 (0.20-0.25)
//     lower groove: outer (hub-side) wall at X = 249.61;  upper groove: outer (top-side) wall at X = 551.38 (301.77 apart)

annotation { "Feature Type Name" : "DP2 rotor shaft" }
export const dp2RotorShaft = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
    }
    {
        const mm = millimeter;
        const R = 19.05;          // OD / 2
        const L = 554.0;
        const rRoot = 37.033 / 2; // groove root radius
        const gw = 0.787;         // groove width
        const gr = 0.225;         // groove root corner radius, 0.225 +/- 0.025
        const xGL = 249.613;      // lower groove, outer wall (groove runs toward +X)
        const xGU = 551.387;      // upper groove, outer wall (groove runs toward -X)
        const xKey = 214.5;       // keyseat centre
        const kw = 9.525;         // keyseat width
        const kcc = 12.70;        // keyseat end-centre distance
        const zFloor = 32.733 - R; // keyseat floor above the axis (S - D/2)
        const kr = 0.794;         // keyseat floor fillet, 1/32 in
        const xPin = 65.5;
        const dPin = 6.35;

        // 1. stock
        fCylinder(context, id + "stock", {
                    "bottomCenter" : vector(0, 0, 0) * mm,
                    "topCenter" : vector(L, 0, 0) * mm,
                    "radius" : R * mm });
        const shaft = qCreatedBy(id + "stock", EntityType.BODY);

        // 2. ring grooves: subtract a tube (outer cylinder minus root cylinder), then round the two root corners
        const grooves = [["gl", xGL, xGL + gw], ["gu", xGU - gw, xGU]];
        for (var g in grooves)
        {
            const gid = id + g[0];
            fCylinder(context, gid + "outer", {
                        "bottomCenter" : vector(g[1], 0, 0) * mm,
                        "topCenter" : vector(g[2], 0, 0) * mm,
                        "radius" : (R + 1) * mm });
            fCylinder(context, gid + "core", {
                        "bottomCenter" : vector(g[1] - 1, 0, 0) * mm,
                        "topCenter" : vector(g[2] + 1, 0, 0) * mm,
                        "radius" : rRoot * mm });
            opBoolean(context, gid + "tube", {
                        "tools" : qCreatedBy(gid + "core", EntityType.BODY),
                        "targets" : qCreatedBy(gid + "outer", EntityType.BODY),
                        "operationType" : BooleanOperationType.SUBTRACTION });
            opBoolean(context, gid + "cut", {
                        "tools" : qCreatedBy(gid + "outer", EntityType.BODY),
                        "targets" : shaft,
                        "operationType" : BooleanOperationType.SUBTRACTION });
            const corners = qUnion([
                        qContainsPoint(qOwnedByBody(shaft, EntityType.EDGE), vector(g[1], 0, rRoot) * mm),
                        qContainsPoint(qOwnedByBody(shaft, EntityType.EDGE), vector(g[2], 0, rRoot) * mm)]);
            opFillet(context, gid + "rootRadius", {
                        "entities" : corners,
                        "radius" : gr * mm });
        }

        // 3. keyseat: closed end-milled slot (two cutter positions joined by straight walls), floor fillet R 1/32 in
        const x0 = xKey - kcc / 2;
        const x1 = xKey + kcc / 2;
        fCylinder(context, id + "ks0", {
                    "bottomCenter" : vector(x0, 0, zFloor) * mm,
                    "topCenter" : vector(x0, 0, R + 5) * mm,
                    "radius" : (kw / 2) * mm });
        fCylinder(context, id + "ks1", {
                    "bottomCenter" : vector(x1, 0, zFloor) * mm,
                    "topCenter" : vector(x1, 0, R + 5) * mm,
                    "radius" : (kw / 2) * mm });
        fCuboid(context, id + "ks2", {
                    "corner1" : vector(x0, -kw / 2, zFloor) * mm,
                    "corner2" : vector(x1, kw / 2, R + 5) * mm });
        const ksTools = qUnion([qCreatedBy(id + "ks0", EntityType.BODY), qCreatedBy(id + "ks1", EntityType.BODY), qCreatedBy(id + "ks2", EntityType.BODY)]);
        opBoolean(context, id + "ksUnion", {
                    "tools" : ksTools,
                    "operationType" : BooleanOperationType.UNION });
        opBoolean(context, id + "ksCut", {
                    "tools" : qCreatedBy(id + "ks0", EntityType.BODY),
                    "targets" : shaft,
                    "operationType" : BooleanOperationType.SUBTRACTION });
        const floorEdges = qUnion([
                    qContainsPoint(qOwnedByBody(shaft, EntityType.EDGE), vector(xKey, kw / 2, zFloor) * mm),
                    qContainsPoint(qOwnedByBody(shaft, EntityType.EDGE), vector(xKey, -kw / 2, zFloor) * mm),
                    qContainsPoint(qOwnedByBody(shaft, EntityType.EDGE), vector(x0 - kw / 2, 0, zFloor) * mm),
                    qContainsPoint(qOwnedByBody(shaft, EntityType.EDGE), vector(x1 + kw / 2, 0, zFloor) * mm)]);
        opFillet(context, id + "ksFillet", {
                    "entities" : floorEdges,
                    "radius" : kr * mm });

        // 4. pin hole, through, along Z
        fCylinder(context, id + "pin", {
                    "bottomCenter" : vector(xPin, 0, -R - 5) * mm,
                    "topCenter" : vector(xPin, 0, R + 5) * mm,
                    "radius" : (dPin / 2) * mm });
        opBoolean(context, id + "pinCut", {
                    "tools" : qCreatedBy(id + "pin", EntityType.BODY),
                    "targets" : shaft,
                    "operationType" : BooleanOperationType.SUBTRACTION });
    });
