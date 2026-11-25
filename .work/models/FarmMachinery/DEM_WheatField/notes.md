# DEM-07 Demo WheatField (`FMS_Mach_Demo_WheatField`) — builder notes

Demo environment piece (owner approved 2026-11-24; demo only, not a catalogue product). Built and checked HEADLESS only — **no live MCP pass** (live Blender MCP still unreachable). Uses the NEW second demo atlas `art/FarmMachinery/Demo/Textures/T_FarmMachinery_Demo2_BaseColor.png` (256 px 4×4, md5 f825e637…) + material `M_FarmMachinery_Demo2` (the first demo atlas has no free cell). Cells: 0 straw light #CDB27E, 1 ochre #B8955A, 2 shadow straw #8E7046, 3 stalk dark #6E5634, 4 bale light #C9AE78, 5 bale shade #A88A56, 6 bale end #9C7E4C, 7 bale ring/twine #7A6038, 8 seedling light #8DB55A, 9 seedling dark #5E8A3A, 10 soil #7D6662 (= demo soil), 11 soil light #9E8274, 12 soil dark #54403C, 13 stubble ground #967E54 (= soft), 14 seedling stem #6E8E44, 15 straw #B29660 (= soft) — muted warm straw in the soft / LOOK v2 range. Existing atlases unchanged (Demo 8b41ff7e, Red eb6768e2). Root on the ground, no LOD. Checks: non-manifold / loose / degenerate 0, coplanar 0, gaps 0; FBX re-import verified (texture found). Max 3 rounds.

- Module 16 × 12 m (snaps on the 16 × 12 grid with DEM-02 / DEM-03 / itself): one faceted canopy block — heightfield on a 0.5 m grid (33 × 25), irregular ear points 0.56–0.86 m with interior plan jitter, ~12 % sparse 3-sided ear spikes to ~1.08 m, two/three straw tones by facet orientation to the key; side walls with a wavy ear band (ochre / light) over shadow stalks in alternating vertical stripes; closed bottom on −0.05. Periodic heights → opposite edges identical.
- Size 16.00 × 1.13 × 12.00 m (top ~1.08). Tris 2494 / 2500.
- Deviation: budget does not allow individual stalks over 192 m², so the wheat is a faceted canopy mass (reads as standing wheat at the demo camera distance, see assembled_789.png); Synty-like single stalks would need ~10× the tris.
- Rounds 3: (1) regular checker pyramids read as an egg crate; (2) irregular heights + plan jitter, spikes; (3) lower canopy (top ~1.0), wavy ear band, larger spikes.
- SNAP: WheatField | WheatField along X 75/75 and along Z 99/99 edge vertices OK; WheatField +Z edge | WheatEdge 99/99 OK; | DEM-03 along X: same footprint and slab bottom (profiles differ by design).

## REDO v2 (2026-11-24, coordinator: v1 read as faceted rocks / crumpled paper) — stalks with ears
- v1 canopy mass replaced (v1 text above is superseded). Structure now: stubble-ground slab (top Y 0, bottom −0.05, Demo2 cell 13)
  + clumps of separate stalks on a jittered cell grid, one clump per cell, bases kept inside their cell (modules tile / snap,
  slab edges identical; SNAP field|field X and Z, field|edge strip, field|DEM-03 all OK).
- Clump: 5–8 stalks, bases within 0.17 m of the clump centre, each leaning 3–12° (spread outward), height 0.90–1.10 m.
  Stalk = closed 3-sided spindle, 12 tris: point base sunk 1 cm into the slab, thin neck r 0.021 at h−0.21, ear widening to
  r 0.050 (bent 8° further), ear tip; stalk sides light straw (cell 0) / ochre, ear ochre (cell 1) with a shadow facet (cell 2).
- WheatField 16 × 12: 120 clumps (12 × 10 cells), 9396 tris (budget ~9000), size 16.00 × 1.17 × 12.00 m.
  WheatEdge 16 × 2: 24 cells (12 × 2), the +Z row thins out irregularly (cut edge), 1236 tris (budget ~2500), 16.00 × 1.17 × 2.00.
- No 8×6 sub-module was needed. Atlas unchanged (Demo2 f825e637…, no new cells), Demo 8b41ff7e, Red eb6768e2.
- Rounds 3 (v2): (1) stalks read as wheat but sparse; (2) denser 12 × 10 cells, thicker neck / bigger ears; (3) clump size 5–8
  for the budget. Check render vs Synty 014: %TEMP%/farmmachinery_check/DEM/wheat_v2.png (HRV-01 + ATT-03 driving into the wheat,
  low ¾ camera). Remaining difference: Synty is denser (single stalks with more ground cover); ours shows more ground between clumps.
- Headless only (no live MCP pass). Checks: non-manifold / loose / degenerate 0, coplanar 0, gaps 0; FBX re-import OK.
