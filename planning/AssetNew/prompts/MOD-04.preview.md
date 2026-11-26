# MOD-04 Wall Pillar — preview prompt (Э5 → Э6)

Catalogue: MOD-04 · `FMS_Garden_Wall_Pillar` · 0.50×0.50×1.05 m · ≤ 300 tris · atlas A · Generator: Sol 6.2

## Prompt

```
Stylized low-poly game asset from a cozy farm and cottage garden series, built from chunky simple shapes with slightly thickened posts, rods and slats and real-world proportions. Faceted flat shading where every face is one solid matte colour; no textures, no gradients, no noise, no outlines, no glossy highlights. Restrained warm palette: light wood #B5835A, dark wood #7A5233, cream #F2E6C9, white-painted wood #EEEDE7, pale limestone #C9C3B6, warm grey stone #A7A39A, dark wrought iron #3A3A3F, brick red #9C3F33, foliage greens #6E9F4A, #4E7A3A and #3F6B3A, rose red #C8473B, rose pink #E58FA0, lilac #A58BC9, opaque water blue #4A78A8. Plants are made of faceted leaf clusters and cup-shaped blooms, never flat leaf cards. Single whole object centred in a three-quarter view from about 25 degrees above, soft warm studio light with soft shadows, plain neutral light-grey background.

A single square stone wall pillar with a ball finial, shown whole, three-quarter view from about 25° above, on a plain neutral light-grey background.
A short, sturdy square pillar 0.5 m wide and about 0.8 m tall, built of stone blocks of different lengths in warm grey stone #A7A39A, with some blocks in the second tone, pale limestone #C9C3B6, three courses on each face with staggered joints. It carries a flat square pale limestone #C9C3B6 coping slab with slightly rounded long top edges 0.06 m thick, exactly as wide as the shaft, and, on top of that, a faceted pale limestone #C9C3B6 ball finial about 0.25 m across (low-subdivision icosphere, visible flat facets) resting on the cap, so the whole piece is about 1.05 m high. Silhouette difference from the earlier packs: a squat stone pillar with a ball, only about half as tall as a person, not a wooden fence post and not a tall wall section.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no photorealism, no noise texture,
not cut off,
no wall attached, no iron lantern, no plants, no moss, no text
```

## Exceptions

none. The wall is not shown; the pillar stands alone.

## Generations (filled by Codex)

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | Matched MOD-03 masonry; specified same-width cap and half-width faceted ball | Sol 6.2 built-in, opaque square, auto seed | Rejected: finial reads oversized and has broad pentagonal faces instead of triangular icosphere facets |
| 2 | Used STR-06 finial as geometry anchor and reduced the ball proportions | Sol 6.2 built-in, opaque square, auto seed | Kept: references/MOD-04.png; single straight shaft, three masonry courses and small triangulated finial |
