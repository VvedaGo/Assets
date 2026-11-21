# SML-04 Hedgehog - spec (Farm Animals, skeleton Q-S, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/SML-04.png` (1536x1024). Chubby hedgehog seen from the front-left
(~40 deg off the front, ~15-18 deg above): face towards the camera (head slightly turned to the camera - pose, modelled
straight), spiky dome to the right/back. The reference shows 5 legs (AI artefact) - modelled 4.
Catalogue: FARM_ANIMALS_PACK.md 5.4 SML-04 - spikes of 40-60 wedges, light face, 0.25 x 0.15 m, 600 tris, Q-S.
Lead brief: ~0.25 m long, 0.15 m tall incl. spikes, target ~1100 tris, up to ~1600 if it improves the look.
Anchors followed: Mouse (`../Mouse/build_mouse.py`: Model/loft, shared joint rings + hidden apex overlap cones,
ray-cast eyes, shade by normal, COM shift, objects/export/verify/preview, coplanar_true), Sheep (lobes as separate
closed solids grouped per bone: Wool_* -> here Spikes_*), Kitten (eye discs proud, round head).
`_common` and `Tools/blender` imported read-only. Script: `build_hedgehog.py -- SML-04 build|look|export`.

## Measured from the reference (ground ~940 px mid depth, spike top 65 px -> 0.15 m => ~0.000171 m/px;
head is nearest the camera -> ~0.00016 m/px there)
| Feature | px | model (m) |
|---|---|---|
| total height (spike tips) | 875 | 0.150 |
| head (face) width / height | ~600 / ~430 | 0.106-0.112 / 0.079 (z 0.022..0.101) |
| hood edge (top of the face) | y 400-440 | head top ~0.10, brown cap over the head top behind the ears |
| ear w x h above the head | ~140 x ~130 | 0.025 x ~0.022, 9 mm thick, cream, darker inner facet |
| ear spacing (centres) | ~490 | x +-0.040 |
| eye dia / spacing | ~60 / ~285 (turned head) | 0.011 (8-gon), x +-0.026 |
| eye height | y 545 | z ~0.075 |
| nose w x h | ~115 x 85 | 0.017 x 0.013, 8-gon faceted dome, z ~0.055 |
| leg width / visible length | ~150-185 / ~160-185 | 0.024 dia (8-gon) / ~0.03 |
| spike length | 110-190 | 0.020 (front) -> 0.030 (rump) |
| spike base | 120-180 | 0.024-0.030 |

## Features (must read at 128 px)
Big round faceted cream head (12-gon superellipse loft, cheeks wider than the brow) with a short blunt muzzle, round
dark-brown 8-gon nose dome, two dark-brown 8-gon eye discs widely spaced, two small rounded-triangle cream ears with a
darker inner facet. Dark-brown dome body (hidden 12-gon core, brown hood over the back of the head) covered by ~57
separate thick 4-sided pyramid spikes in 8 staggered rows from behind the head to the rump and down the sides to the
legs, pointing up/back, longer towards the rump. Four short thick 8-gon cream legs with flared flat feet.
Shading: cream in 3 tones by face normal (top/front light, side mid, under dark); spikes: faces on the ridge side
light (normal up) or mid, back faces dark; core/hood brown; belly underside cream dark.

## Material class
Flat palette `T_FarmAnimals_Hedgehog_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Hedgehog`: 0 cream light #F4DCBC,
1 cream mid #EBCBA5, 2 cream dark #D9B48C, 3 ear inner #DDB089, 4 spike light #6B443D, 5 spike mid #5A3430,
6 spike dark #462823, 7 core/hood #4F2E29, 8 eye #2E1A15, 9 nose #4A2A22, 10 sole #C8A07A, 11-15 series spares.

## Parts (object `FMS_Hedgehog_<Part>`, direct children of empty `FMS_Hedgehog`, pivot on the joint)
Pelvis, Spine1, Spine2 (dome core), Neck1, Neck2, Head, Jaw, Ear.L/R, Eye.L/R, Nose, FrontUpper/Lower/Foot.L/R,
HindUpper/Lower/Foot.L/R, Spikes_Pelvis, Spikes_Spine1, Spikes_Spine2, Spikes_Neck. Neck1/Neck2/Jaw/Upper legs are
hidden connectors (Q-S short neck). No tail (Q-S Tail1-3 not built: no tail visible in the reference).
Later skin binding (weight 1.0): Spikes_Pelvis -> Pelvis, Spikes_Spine1 -> Spine1, Spikes_Spine2 -> Spine2,
Spikes_Neck -> Neck1 (front spike row over the head's back). Each spike group's pivot = its bone's pivot.
Body joints share the joint ring exactly (no seam line), each part closes with a hidden cone into the neighbour.

## NOT modelled
tail, whiskers, mouth, teeth, eyelids/pupils/highlights, claws/toes, fur strands, ground, head turn (pose), 5th leg.

## Rounds (Workbench sheet, then EEVEE sheet: ref angle, preview, side, front, back, top + 128 px thumbnail)
1. Dome too low vs the head (head top at 71% of the height, reference ~58%) -> legs read long; spikes thin flat shards
   (tilted 40-56 deg, narrow bases); spikes stop at z 0.032. -> core top 0.126 (separate bottom radius), spikes to v 136,
   tilt 30-48 deg, bases 0.030 x 0.029, head 1 cm lower; warmer cream.
2. Head small/narrow next to the dome, sticking forward like a mouse head; cream almost white; centre spike crest. ->
   head group x1.18 wide / x1.10 tall, 6 mm back; cream #F0CDA3 -> #EDC79C; spikes broader (0.033 x 0.032) and lower.
3. Side view: head in front of the dome, no spikes flanking it; long muzzle with a step under it. -> head 12 mm into
   the dome, blunter dome front (exponent 3.2), muzzle 5 mm shorter and fuller.
4. Dome smaller than the reference, model 0.229 long; light lip under the chin (hidden Jaw poking through a facet). ->
   core x1.09 / y1.10 / top 1.07, Jaw fully inside, anchored in the nose root.
5. Ears swallowed by the bigger dome; front spike crest. -> ears 8 mm forward, 4 mm out, +7%; neck row 15% lower, +8 deg.
6. (preview) Legs slim vs the reference (leg/face width 0.19 vs 0.25) -> lower legs 0.028-0.030, feet 0.033 wide.
Polish round 2 (review 4/5): 8 rows -> 14 rows / 125 thin spikes + zig-zag hood border (superseded by round 3).
Rework round 3 (second review 3/5: ~125 thin needles, messy crown tuft, dark hole under the near ear, high preview
camera without horizon):
8. Spine field -> 29 broad low pyramids: base 0.050 x 0.054 (~0.2-0.25 x body length), height 0.030 (0.6 x base),
   tilted 35 deg back; 4 main staggered rows (u -0.82/-0.72 front, -0.24, 0.24, 0.70) + 2 low side pairs between the
   legs (u -0.60, 0.10); base corners ray-projected onto the real shell/head facets (no floating edge on the curved
   body). All spikes the same size (low side ones 0.6-0.95), no crown tuft. Spike tris 6 each (base split F-B).
9. Shell front blunter (front exponent 3.2 -> 5) so the brown shell meets the cheeks; shell colour #42261F -> #4C2B26
   (reads as shell, not as a hole); belly cream only on faces looking down (n.z < -0.85; was a cream sliver at the side).
10. Jagged face border: front-row centre spike rooted on the head at the hood line (front corner over the forehead) +
    brown triangle teeth on the forehead; head facets around the ears cream; ears 4 mm forward and dish floor lifted so
    neither the shell nor the hood cuts through the ear (dark sliver gone).
11. Preview with the pack's standard low 3/4 camera (0.85, -1.0, 0.22) = ~10 deg above the ground, horizon + sky.
Checks added: spike triangles vs face (n.y < -0.6)/eyes/nose, vs ears, vs visible legs (z < 0.035) = 0; spikes that
would cut an ear or a visible leg are pruned (0 pruned in the final layout).
Remaining (nitpicks): head straight (reference turns it to the camera); fewer, bigger spikes than the reference's ~40-50
(29, as the review asked); the smooth brown shell shows between the spike rows on the lower sides.

## Result
tris 1166 (target ~1100, limit ~1900): Spikes_Pelvis 42 (7 spikes), Spikes_Spine1 48 (8), Spikes_Spine2 54 (9),
Spikes_Neck 30 (5, of them 1 on the head top) = 29 spikes x 6, Head 164, Pelvis 118, Spine2 94, Spine1 72, Foot 60 x4,
Lower legs 28 x4, Nose 44, Ear 32 x2, Eye 14 x2, Upper legs 8 x4, Neck1/Neck2/Jaw 8.
Size: width 0.190 (side spikes; head 0.129) x length 0.220 (nose -> rump spikes) x height 0.153 (spike tips);
head z 0.020..0.098, ear tips 0.116, belly 0.027, lowest spike 0.015.
Pivot: root on the ground under the volume centroid (geometry shifted +0.0019 m in Y); parts pivot on their joints;
spike groups share their bone's pivot (Spikes_Neck incl. the head-top spike -> Neck1).
Checks: non-manifold 0, loose 0, degenerate 0, mirror 0.000000, worst contact gap 0, coplanar (shared) 0, x10 0,
coplanar_true 0, spike cuts face/eyes/nose 0, ears 0, visible legs 0, min z 0 (feet).
FBX re-import: 28 meshes + root, 1166 tris, dims 0.190 x 0.220 x 0.153, texture found in FMS_Hedgehog.fbm (256x256).

## Deviations
- Head straight (the reference pose turns it to the camera); 4 legs (the reference shows 5).
- Length 0.220 (catalogue/brief 0.25): broad backward-tilted pyramids end at the rump instead of trailing behind it;
  width 0.190 (low side spikes stick out); height 0.153.
- tris 1166 vs catalogue 600 (brief target ~1100).
- Preview camera ~10 deg above the ground (pack template Sheep/Lamb/Ram/Cat), not 20 deg: at 20 deg with the pack's
  50 mm lens the horizon leaves the frame.
- No tail part (Q-S Tail1-3 not built); Spikes_* bound 1.0 to Pelvis/Spine1/Spine2/Neck1; the head-top spike binds to
  Neck1 (group name kept).
- Eyes 11 mm (8-gon), slightly larger than the reference for 128 px readability.

## Rig + clips (2026-11-21) - `rig_hedgehog.py -- SML-04 bend|anim|curlviews|export`, `hedgehog_clips.py`
New skeleton "QS" (22 bones, Q names kept so the shared IK/metrics work): Root > Pelvis > Spine1 > Spine2 > Neck1 > Neck2 >
Head > Nose (snout) + Ear.L/R; Front/Hind Upper > Lower > Foot .L/.R (Upper on Spine2 / Pelvis). No Jaw/Tail bones.
Knee bone joint at z 0.028 (mid visible leg; the 12 mm hidden Upper part would make IK angles explode).
Binding: shell Pelvis/Spine1/Spine2 path blend (50/50 at the joints); Spikes_* rigid to Pelvis/Spine1/Spine2;
Spikes_Neck: head-top spike -> Head, the 4 shell spikes -> Spine2 (deviation from the mesh-round note "-> Neck1": they sit
on the shell and must not lift off when the head tucks); Head/Jaw/Eyes -> Head; Nose -> Nose; Lower leg top ring -> Upper,
bottom ring (inside the paw) -> Foot. Mesh unchanged (1166 tris, 28 parts).
- Idle 3.0 s (91 fr): 3 sniff bouts (head lifts/turns, snout 8 Hz twitch), ear flicks, breaths.
- Walk 0.5 s (16 fr): lateral-sequence patter 0.11 m/s, step 0.034 m, shell roll/sway, head bob, snout sniffs.
- Curl_Up 3.0 s (91 fr, loop): ears fold, head tucks (keyed translation 5.2 cm back into the shell), back arches
  (Pelvis -12, Spine1 +20, Spine2 +40), legs pulled up 4 cm into the shell, ball held frames ~31..55 with 2 breaths,
  uncurl (legs, back, head last). Lowest vertex set to 0 every frame. Location keys: Pelvis, Head, Ear.L/R, *Upper.
Metrics: loop closure 0.000 deg / 0 m all; lowest vertex 0 / -0.7 mm (Walk) / 0; Walk slip 2.54% of step; joint-limit
violations 0 (curl limits: Pelvis x -40, Spine1/2 x up to 35/45); hidden check in the held ball (3 frames): 0 face/ear/leg
vertices visible (26-direction ray test vs shell + spikes + ground). FBX re-import: 22 bones, 28 meshes, 1166 tris,
3 takes, vertex error 0.0 m, texture found.
Known: the ball is an arched dome (no true sphere: rigid shell parts), the front shell cap shows as a dark brown facet;
ear/foot slivers can show for 1-3 frames during curl/uncurl transitions.

## Animation fixes round 1 (2026-11-21, ANIMATION_FIXES.md 9)
Curl_Up: shell closes into a loop (Pelvis -115, Spine1 +115, Spine2 +115; curl-only limits raised to 130), shell bbox in
the ball 0.140 x 0.127 x 0.132 m (was 0.14 x 0.185 x 0.127 dome). Head and leg sub-chains moved rigidly to the ball
centre (location keys) and shrunk (bone scale keys: Head 0.55, legs 0.5; scale = 1 keyed in Idle/Walk too); head tucks in
sync with the shell. Hidden check in the held ball: 0 visible face/ear/leg vertices (3 frames).
Known (mesh): the spike-free shell band shows as a smooth brown strip on top of the ball and as a flat facet for ~0.2 s
during curl/uncurl; the head/legs emerge under the ball in the last 0.3 s of the uncurl (by design).
