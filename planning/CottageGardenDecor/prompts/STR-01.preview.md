# STR-01 Arch_Wood — preview prompt (Э5 → Э6)

Catalogue: STR-01 · `FMS_Garden_Arch_Wood` · 1.6×0.7×2.4 m · 1000 tris · atlas A · Generator: Sol 6.2

## Prompt

```
Stylized low-poly game asset from a cozy farm and cottage garden series, built from chunky simple shapes with slightly thickened posts, rods and slats and real-world proportions. Faceted flat shading where every face is one solid matte colour; no textures, no gradients, no noise, no outlines, no glossy highlights. Restrained warm palette: light wood #B5835A, dark wood #7A5233, cream #F2E6C9, white-painted wood #EEEDE7, pale limestone #C9C3B6, warm grey stone #A7A39A, dark wrought iron #3A3A3F, brick red #9C3F33, foliage greens #6E9F4A, #4E7A3A and #3F6B3A, rose red #C8473B, rose pink #E58FA0, lilac #A58BC9, opaque water blue #4A78A8. Plants are made of faceted leaf clusters and cup-shaped blooms, never flat leaf cards. Single whole object centred in a three-quarter view from about 25 degrees above, soft warm studio light with soft shadows, plain neutral light-grey background.

A single wooden garden rose arch with a FLAT top, shown whole, three-quarter view from about 25° above, on a plain neutral light-grey background.
The arch is a tall rectangular portal, 1.6 m wide, 0.7 m deep and 2.4 m high, with an open walk-through opening 1.2 m wide and 2.1 m high; the opening is completely empty (no gate, no door). It stands on four chunky square posts. Wooden posts (shared construction): square section 0.10-0.16 m, flat faceted, only a 0.01 m bevel on the long edges, light wood #B5835A, flat untextured faces. Each side of the arch is a deep side panel 0.6 m deep between the front and rear post, filled with lattice. Lattice (shared construction): diagonal slats crossing at 45°, about 0.03 m square, real open gaps of about 0.10 m between the slats, closed by a flat frame rim about 0.05 m wide so the lattice ends cleanly at the edges; here the lattice is light wood #B5835A and the lattice side panels reach from just above the ground to the lintel at 2.1 m. A thick lintel beam joins the posts at the front and at the rear at a height of 2.1 m. The top is flat and open: two thin purlins run front-to-back on the lintels and five parallel cross-beams lie across them, sticking out about 0.08 m past the posts on both sides, so the roof reads as a flat grid of beams with open sky gaps between them. Cross-beam ends in dark wood #7A5233 (end faces only). Overall silhouette: a rectangular flat-topped portal with deep lattice sides, clearly NOT a curved arch and NOT a fence.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no photorealism, no noise texture,
not cut off, no gate leaf, no door, no plants, no roses, no vines, no curved or rounded top, no fence pickets
```

## Exceptions

none (the arch stands on its four post bases; no ground plane is drawn)

## Generations (filled by Codex)

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | White variant matching STR-06; specified four posts and five upper beams over two purlins | Sol 6.2 built-in, opaque square, auto seed | Rejected: the five top beams run front to back instead of across the opening, and the purlin tier is missing |
| 2 | Rewrote roof as three courses with cross beams parallel to entry lintel | Sol 6.2 built-in, opaque square, auto seed | Rejected: four cross beams instead of five, with slats intersecting the purlins instead of resting on top |
| 3 | Specified five widthwise slats with four visible gaps above two separate supports; raised camera | Sol 6.2 built-in, opaque square, auto seed | Kept: references/STR-01.png; white variant with five top slats and four posts, near-frontal view |
