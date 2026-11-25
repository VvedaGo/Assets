# TRL-01 Trailer_Tipper — preview prompt (Э5 → Э6)

Catalogue: TRL-01 · Prefab `FMS_Mach_Trailer_Tipper_Red` · variants Empty / Grain (this preview: Empty) · 2.5×6.6×2.7 m · Generator: Sol 6.2

## Prompt

```
Stylized low-poly 3D game asset of modern farm machinery, built from chunky simplified blocks with single chamfered edges and faceted flat shading, matte colours, no textures, no gradients, no text, logos or decals. Small flat palette: signal red body #C8473B with darker red #A8372E, cream wheel rims #F2E6C9, near-black tyres #2B2D31 with large blocky tread lugs, dark grey chassis and seat #474B51, steel grey metal #8E959B, opaque blue-grey cab glass #7FA3B5. Realistic machine proportions simplified for a game, wheels clearly separate and readable, no interior, no hoses, chains, dirt or rust. Single object shown whole, three-quarter front view from about 30 degrees above, soft studio light, plain neutral light-grey background #E9E9EC, no ground, no scene, no other objects.

A single two-axle farm tipper trailer, EMPTY, shown whole, three-quarter view from about 30 degrees above, on a plain neutral light-grey background. Long and tall rectangular silhouette about 6.6 m long, 2.5 m wide and 2.7 m high (drawbar included in the length), with a tandem pair of wheels at the rear half and a long drawbar reaching forward. Tall straight steel box bed with high solid steel side walls, a higher front headboard and a rear tailgate, all in signal red #C8473B; lower edges and the outer faces of the lower side rails in darker red #A8372E. Single 45° chamfer on the top edges of the walls and headboard, a few chunky vertical stiffener ribs on the side walls (flat, 0.08 m proud), the tailgate closed with two chunky steel latch blocks. The empty bed floor is visible from above as a flat dark red #A8372E surface, nothing inside. The bed sits on a chunky steel chassis frame in steel grey #8E959B with darker underside #6E757B and two heavy longitudinal rails; at the rear of the chassis a visible tipping hinge block at the bed's rear lower edge, and a short chunky steel hydraulic cylinder rod (simple cylinder, steel grey) leaning from the chassis up to the front underside of the bed. Four rubber tyres in near-black #2B2D31 with 16 sides and 12-16 large blocky tread lugs, cream wheel rims #F2E6C9 with darker cream inside #DCC9A0, mounted as two axles close together (tandem), wheels outside the frame under the rear half of the bed, with low dark grey #474B51 mudguards above them. At the front a steel A-frame drawbar in steel grey #8E959B narrowing to a single round eye (thick ring) at its tip, hanging low, pointing straight forward. At the rear a small steel hitch bracket under the tailgate. Small orange #E8913A reflector blocks at the rear corners. Heavy, sturdy, rubber-tyred steel trailer, clearly different from a wooden horse cart: no spoked wheels, no wooden planks, no shafts.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no photorealism, no noise texture,
not cut off, no grain or any load in the bed, no tractor, no wooden parts, no spoked wheels, no cab
```

## Exceptions

None. The Grain variant is not generated here: the grain heap is a separate object in the 3D spec (Load_Grain, slot 15 #D8B65A).

## Generations (filled by Codex)

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | Used IMP-03 as chassis, wheel and towing eye reference, clarified lowered empty steel box and tandem axles | ImageGen, session model gpt-6.2-sol | Kept: empty lowered tipper bed, visible ram, tandem running gear and low A-drawbar (1536 x 1024 px) |
