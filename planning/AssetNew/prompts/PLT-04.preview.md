# PLT-04 Ivy Patch — preview prompt (Э5 → Э6)

Catalogue: PLT-04 Плющ на стену `FMS_Garden_Ivy_Patch` · no variants · 1.0×0.15×1.0 m · 500 tris · Generator: Sol 6.2

## Prompt

```
Stylized low-poly game asset from a cozy farm and cottage garden series, built from chunky simple shapes with slightly thickened posts, rods and slats and real-world proportions. Faceted flat shading where every face is one solid matte colour; no textures, no gradients, no noise, no outlines, no glossy highlights. Restrained warm palette: light wood #B5835A, dark wood #7A5233, cream #F2E6C9, white-painted wood #EEEDE7, pale limestone #C9C3B6, warm grey stone #A7A39A, dark wrought iron #3A3A3F, brick red #9C3F33, foliage greens #6E9F4A, #4E7A3A and #3F6B3A, rose red #C8473B, rose pink #E58FA0, lilac #A58BC9, opaque water blue #4A78A8. Plants are made of faceted leaf clusters and cup-shaped blooms, never flat leaf cards. Single whole object centred in a three-quarter view from about 25 degrees above, soft warm studio light with soft shadows, plain neutral light-grey background.

A single patch of ivy, shown whole, three-quarter view from about 25° above, on a plain neutral light-grey background.
A square carpet of ivy standing upright by itself, about 1.0 m wide, 1.0 m tall and only 0.15 m deep, like a green blanket meant to cover a wall. Its back is one perfectly flat vertical plane; the front is covered with many overlapping chunky diamond-shaped (rhombus) leaves, each leaf a small faceted solid with a raised centre ridge, not a flat card. The leaves lie in three shallow overlapping layers: a dense back layer in deep green #3F6B3A, a middle layer in dark foliage green #4E7A3A, and a front layer in foliage green #6E9F4A, so the patch reads as three tones with a slightly bumpy surface. Leaves point mostly downward and sideways, in loose rows. Three short chunky dark wood brown #7A5233 vine stems run up through the patch and are visible in a few gaps. The outline of the patch is irregular and leafy (not a clean square): leaf tips stick out of the edge, but overall it stays within the 1 m square. No flowers, no berries.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no photorealism, no noise texture,
not cut off, no flat leaf cards, no alpha cut-out foliage, no wall, no fence, no lattice, no pot, no soil, no flowers
```

## Exceptions

The ivy is shown alone, without a wall. Its back is a deliberately flat vertical plane (the side that touches the wall) and is part of the model; all leaves lie in front of it, so the left or right silhouette edge reads as a thin straight line. Mounting dimensions: 1.0 m wide × 1.0 m tall × 0.15 m deep; it is placed on the face of the stone wall MOD-03 (2.0 m long, 0.60 m high, 0.40 m thick), the lattice screen MOD-01 (1.88 m wide, 1.80 m high, 0.06 m thick) or a similar flat vertical surface.

## Generations (filled by Codex)

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | Used PLT-02's flush attachment edge and PLT-01's foliage shading; described three layers of raised rhombus leaves. | Sol 6.2 built-in; seed not exposed | Rejected: deeply lobed ivy leaves in place of the specified four-corner rhombi. |
| 2 | Specified four straight sides per leaf and an oblique view of the shallow flush back edge. | Sol 6.2 built-in; seed not exposed | Kept: `references/PLT-04.png`. |
