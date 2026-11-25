# IMP-05 DiscHarrow — preview prompt (Э5 → Э6)

Catalogue: IMP-05 · Борона дисковая прицепная (`DiscHarrow`) · work pose 4.0×5.0×1.3 m shown (transport pose 2.6×5.0×2.4 derived from hinges) · 4000 tris · Lite · Generator: Sol 6.2

## Prompt

```
Stylized low-poly 3D game asset of modern farm machinery, built from chunky simplified blocks with single chamfered edges and faceted flat shading, matte colours, no textures, no gradients, no text, logos or decals. Small flat palette: signal red body #C8473B with darker red #A8372E, cream wheel rims #F2E6C9, near-black tyres #2B2D31 with large blocky tread lugs, dark grey chassis and seat #474B51, steel grey metal #8E959B, opaque blue-grey cab glass #7FA3B5. Realistic machine proportions simplified for a game, wheels clearly separate and readable, no interior, no hoses, chains, dirt or rust. Single object shown whole, three-quarter front view from about 30 degrees above, soft studio light, plain neutral light-grey background #E9E9EC, no ground, no scene, no other objects.

A single trailed tandem disc harrow in WORK pose, shown whole, three-quarter view from about 30 degrees above, seen from the front-left so the drawbar faces the camera and points toward the viewer. No tractor. Same series look as the earlier machines (plough, trailer): chunky blocks, red and steel grey.
Structure, exactly these simple parts and nothing else:
1. One long steel-grey #8E959B A-shaped drawbar at the front, ending in one chunky ring eye (octagonal ring with a round hole) pointing toward the camera.
2. One central frame in signal red #C8473B with darker red #A8372E sides: a flat rectangular box frame, about 1.6 m wide and 3 m long, lying low and horizontal.
3. Two side frame arms in steel grey, one on each side of the central frame, continuing the frame sideways in a straight line, so the whole frame is one flat horizontal bar about 4 m wide, each arm ending in a small signal-orange #E8913A tip block. The wings are fully unfolded: nothing is tilted, nothing is folded up, no V shape.
4. Exactly TWO rows of discs: a front row and a rear row, parallel to each other, both running straight left to right across the full width of the machine. Each row is ONE straight square steel axle carrying exactly 12 identical discs in an evenly spaced line (12 in the front row, 12 in the rear row, 24 in total). Each disc is a flat, slightly concave round plate of 12 facets, dark grey #474B51 with a lighter steel-grey #8E959B cutting edge, about 0.7 m across, all the same size, all standing upright and parallel to each other. The two axles are level with each other and parallel to the ground; the discs touch the ground line with their lowest edge.
5. Exactly TWO road wheels, one left and one right, on one single transverse axle under the middle of the central frame, set inboard of the frame edges and symmetrical: near-black tyres #2B2D31 with large blocky tread lugs, cream #F2E6C9 rim discs, diameter about 0.9 m. Their lowest point is level with the lowest edge of the discs. There is no third wheel and no other wheel anywhere.
Everything chunky and simple, symmetric left to right, no hoses, no hydraulic cylinders, no chains, no thin rods, no decals.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no tractor, no photorealism, no noise texture,
not cut off, no folded wings, no V shape, no tilted wings, no third wheel, no extra tyres, no more than two wheels, no more or fewer than two disc rows, no mixed disc sizes, no angled disc gangs, no hydraulic cylinders
```

## Exceptions

none (no stand; the harrow is shown floating)

## Generations (filled by Codex)

Prompt v2 (2026-11-24) after 4 rejected generations; attempts 5–6 allowed

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | Used IMP-01 as style reference, specified double gangs and V-folded transport wings | ImageGen, session model gpt-6.2-sol | Rejected: extra third road tyre on front-left frame (1536 x 1024 px) |
| 2 | Edited first draft to remove the extra front-left tyre | ImageGen, session model gpt-6.2-sol | Rejected: remaining road tyres still misaligned with a single transverse axle (1536 x 1024 px) |
| 3 | Regenerated using IMP-03 for single-axle style, tightened hub alignment and chassis constraints | ImageGen, session model gpt-6.2-sol | Rejected: wing disc axles do not follow the wing fold, too many discs in centre (1536 x 1024 px) |
| 4 | Edited third draft to align wing disc axles and balance disc count across segments | ImageGen, session model gpt-6.2-sol | Rejected: wing disc axles still transverse to their inclined supports, disc grouping changed incorrectly, limit reached (1536 x 1024 px) |
| 5 | Used prompt v2 with IMP-01 as style reference, emphasized paired disc stations and one inboard transverse axle | ImageGen, session model gpt-6.2-sol | Rejected: rear row has 11 discs, disc centers lack common gang axles, and the wheel axle is unattached to the frame (1536 x 1024 px) |
| 6 | Used prompt v2 with IMP-03 as style reference, specified through-hub gang axles, groups of four and frame-mounted wheel support | ImageGen, session model gpt-6.2-sol | Rejected: the rear row has only ten discernible discs and an interrupted center pattern, so 12 equally spaced discs cannot be confirmed, limit reached (1774 x 887 px) |
