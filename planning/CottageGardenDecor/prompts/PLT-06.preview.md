# PLT-06 Hollyhock — preview prompt (Э5 → Э6)

Catalogue: PLT-06 Мальва `FMS_Garden_Hollyhock` · 1 variant `_White` (colour) · 0.6×0.6×1.8 m · 700 tris · Generator: Sol 6.2

## Prompt

```
Stylized low-poly game asset from a cozy farm and cottage garden series, built from chunky simple shapes with slightly thickened posts, rods and slats and real-world proportions. Faceted flat shading where every face is one solid matte colour; no textures, no gradients, no noise, no outlines, no glossy highlights. Restrained warm palette: light wood #B5835A, dark wood #7A5233, cream #F2E6C9, white-painted wood #EEEDE7, pale limestone #C9C3B6, warm grey stone #A7A39A, dark wrought iron #3A3A3F, brick red #9C3F33, foliage greens #6E9F4A, #4E7A3A and #3F6B3A, rose red #C8473B, rose pink #E58FA0, lilac #A58BC9, opaque water blue #4A78A8. Plants are made of faceted leaf clusters and cup-shaped blooms, never flat leaf cards. Single whole object centred in a three-quarter view from about 25 degrees above, soft warm studio light with soft shadows, plain neutral light-grey background.

A single hollyhock plant, shown whole, three-quarter view from about 25° above, on a plain neutral light-grey background.
A tall cottage-garden hollyhock clump about 1.8 m high and 0.6 m wide, made of exactly three chunky straight stems in foliage green #4E7A3A that grow from one small bunch at the ground, slightly leaning apart: heights 1.8 m, 1.6 m and 1.4 m. Along the upper two thirds of every stem, large open cup-shaped flowers (shallow six-sided faceted cups with a small yellow #E8B83A faceted centre) stand out sideways and upward on very short stalks, spiralling around the stem: five flowers per stem, the largest (about 0.16 m across) low and the smallest (about 0.10 m) near the top, each stem ends in a small pointed green bud cone. Flowers are rose pink #E58FA0 with paler pink #F2B8C2 outer facets. Around the foot of the clump lie six thick flattened faceted leaf plates in foliage green #6E9F4A with lighter #8AB257 upper facets, pointing outward like a rosette, each leaf a chunky low-poly solid, never a flat card. The lower 0.5 m of the stems is bare except for the leaves at the foot. Tall, narrow, upright silhouette, clearly different from a sunflower, a lavender tuft and a round bush.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no photorealism, no noise texture,
not cut off, no flat leaf cards, no alpha cut-out foliage, no realistic petals, no pot, no soil, no round bush, no sunflower head
```

## Exceptions

none. (A small bunch of leaf plates at the foot belongs to the model; no soil disc.)

## Generations (filled by Codex)

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | Matched PLT-01/03 faceting while specifying three green stems, pink shallow cups and a six-leaf rosette. | Sol 6.2 built-in; seed not exposed | Rejected: more than five flowers on each stem. |
| 2 | Made the left, center and right stem counts explicit and kept the lower stems bare. | Sol 6.2 built-in; seed not exposed | Rejected: six cups on the left stem and seven on the center stem. |
| 3 | Edited the second candidate with per-stem flower removal instructions; preserved its framing and shape. | Sol 6.2 built-in; seed not exposed | Rejected: six cups each remained on the left and center stems. |
| 4 | Removed the two extra cups by their exact positions while preserving the five on the right. | Sol 6.2 built-in; seed not exposed | Kept: `references/PLT-06.png`. Verified five cups per stem. |
