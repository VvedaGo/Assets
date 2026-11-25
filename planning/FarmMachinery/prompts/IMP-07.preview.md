# IMP-07 HayRake — preview prompt (Э5 → Э6)

Catalogue: IMP-07 · Валкователь двухроторный (`HayRake`) · transport pose 2.8×5.6×3.4 m (work pose 6.8×5.6×1.4) · 5000 tris · Full · Generator: Sol 6.2

## Prompt

```
Stylized low-poly 3D game asset of modern farm machinery, built from chunky simplified blocks with single chamfered edges and faceted flat shading, matte colours, no textures, no gradients, no text, logos or decals. Small flat palette: signal red body #C8473B with darker red #A8372E, cream wheel rims #F2E6C9, near-black tyres #2B2D31 with large blocky tread lugs, dark grey chassis and seat #474B51, steel grey metal #8E959B, opaque blue-grey cab glass #7FA3B5. Realistic machine proportions simplified for a game, wheels clearly separate and readable, no interior, no hoses, chains, dirt or rust. Single object shown whole, three-quarter front view from about 30 degrees above, soft studio light, plain neutral light-grey background #E9E9EC, no ground, no scene, no other objects.

A single trailed twin-rotor hay rake in TRANSPORT pose (both rotor arms raised steeply upward and sideways, rotors tilted up), shown whole, three-quarter view from about 30 degrees above, seen from the front-left so the drawbar faces the camera. No tractor.
Silhouette: a chunky central frame in red #C8473B with darker red #A8372E side faces, with a steel-grey #8E959B A-shaped drawbar at the front ending in a drawbar eye ring and a short steel stub for a power take-off, no driveshaft. Two large wheels sit under the central frame: near-black tyres #2B2D31 with large blocky tread lugs, cream #F2E6C9 rim discs, diameter about 0.8 m. From each side of the frame a thick steel-grey boom arm hinges upward at about 70 degrees, carrying at its end a rotor: a round hub with twelve radial steel-grey tine arms (chunky flat bars, each ending in a short bent darker #6E757B tine tip) spread evenly like a wheel of spokes, the rotor tilted up with the arm, giving a tall V-shaped silhouette about 3.4 m high. Signal-orange #E8913A tips on the tine ends and a small orange reflector on each arm. Everything chunky, no thin wires, no hoses, no decals.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no tractor, no photorealism, no noise texture,
not cut off
```

## Exceptions

none (no stand; the machine is shown floating)

## Generations (filled by Codex)

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | Used IMP-03 as style anchor, specified mirrored raised rotor booms and radial tine count | ImageGen, session model gpt-6.2-sol | Rejected: wheel axle lacks chassis mounts and each rotor shows only 11 tips (1536 x 1024 px) |
| 2 | Added chassis axle hangers and moved lifting arms behind rotor hubs | ImageGen, session model gpt-6.2-sol | Rejected: axle is mounted but only 11 distinct tines are visible on each rotor (1536 x 1024 px) |
| 3 | Edited the second draft to distribute 12 tines at even pitch on each hub | ImageGen, session model gpt-6.2-sol | Kept: 12 separate tips per rotor, two raised booms and one axle attached to the chassis (1536 x 1024 px) |
