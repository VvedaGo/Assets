FARM MACHINERY LITE  (v1.0.0)
Stylized low poly farm machinery: 13 models (21 prefabs with colour, pose and load variants) + 3 ready compositions.
Two tractors, six implements, three trailers, quick hitch and front weight.
Gameplay-ready hierarchy: separate wheels, named attach points, moving parts on their pivots, LOD1, Box Colliders.

REQUIREMENTS
- Unity 6000.3 (built with 6000.3.10f1).
- Universal Render Pipeline (URP) 17.3. Built-in Render Pipeline and HDRP are not supported.
- No scripts, no other packages.

QUICK START
1. Open Demo/Scenes/Demo_FieldWork.unity and press Play (or look through the Game view).
2. Demo/Scenes/Demo_Catalog_Lite.unity shows all 21 prefabs in rows.
3. Drag any prefab from Art/Prefabs/<Category> into your scene. Art/Prefabs/CMP holds the ready compositions.

FOLDERS
Art/Models          FBX meshes (LOD0 + LOD1 parts), one FBX per model, grouped by category
Art/Textures        3 colour atlases, 256 x 256 PNG (Red, Green, Blue)
Art/Materials       3 URP/Lit materials: M_FarmMachinery_Red / Green / Blue
Art/Prefabs         Prefabs by category (TRC, IMP, TRL, ATT) and compositions (CMP)
Demo                Demo scenes and demo-only assets (island ground, fields, road, grass, clouds, sky,
                    post-processing volume). Not counted as product models. Safe to delete.
Documentation       This file and the changelog

PREFABS  (naming: FMS_Mach_<Name> for a base prefab, FMS_Mach_<Name>_<Variant> for a Prefab Variant)
TRC Tractors (2)    Tractor_Cab, Tractor_Large                         + _Green, _Blue of each
IMP Implements (6)  Plough, Seeder, Sprayer, Mower, DiscHarrow, Cultivator
                    + Sprayer_Work, Mower_Work, DiscHarrow_Work (work poses; the base is the transport pose)
TRL Trailers (3)    Trailer_Tipper, Trailer_Flatbed, Trailer_Tank      + Trailer_Tipper_Grain (grain load on)
ATT Attachments (2) QuickHitch, FrontWeight
CMP Compositions(3) CMP_01_Ploughing, CMP_02_GrainHaul, CMP_03_MachineYard
                    (built only from the prefabs above; they add no new models)

GAMEPLAY-READY CONTRACT
- Scale 1 unit = 1 m, Y up, every machine faces +Z. The root pivot is on the ground (Y = 0) at the centre of the
  footprint; root scale 1, rotation 0.
- Wheels: every wheel is its own child object (tyre + rim) with the pivot at the wheel centre and the spin axis on
  local X. Names: Wheel_<Axle><Side> - axles F / M / R from front to rear, sides L / R (Wheel_FL, Wheel_RR);
  a single axle uses Wheel_L / Wheel_R, a plough gauge wheel is Wheel_Gauge. Steer by rotating about local Y.
  The pack has no WheelCollider: add your own on empty objects at the wheel centres if you use Unity physics.
- Attach points are empty GameObjects (+Z forward, +Y up). A pair matches in position and rotation:
    Hitch_Rear  (tractor drawbar pin)          <->  Hitch_Front  (trailer or trailed implement drawbar eye)
    Link3P_Rear (tractor 3-point linkage)      <->  Link3P_Front (mounted implement)
    PTO_Rear    (tractor PTO shaft end)        <->  PTO_Front    (implement PTO input)
    Link3P_Front of Tractor_Large              <->  Link3P_Rear of FrontWeight
  Standard rest heights: Hitch 0.55 m, Link3P 0.60 m, PTO 0.70 m. Link3P_* points are children of the Linkage_*
  part and rise with it. Service point: Seat.
- To attach B to A: rotate and move B so that B's point lies exactly on A's point, e.g. in a script
      Quaternion rel = Quaternion.Inverse(b.rotation) * bPoint.rotation;
      Vector3 local = b.InverseTransformPoint(bPoint.position);
      Quaternion rot = aPoint.rotation * Quaternion.Inverse(rel);
      b.SetPositionAndRotation(aPoint.position - rot * local, rot);
      b.SetParent(aPoint, true);   // optional: B now follows A
  The 3 compositions are assembled this way (0.0 mm joint error).
- QuickHitch and FrontWeight are modelled at their mounted height, so they float above Y = 0 when placed alone.
- Moving parts are separate objects with the pivot on their hinge axis (rest = transport / closed): doors (Door_L),
  tractor links (Linkage_Rear / Linkage_Front), tipper Bed and Tailgate, sprayer Boom_L/R, seeder Lid and
  Marker_L/R, mower Bar, harrow Wing_L/R, cultivator Roller, tank Hatch. Load_Grain is a child mesh switched on in
  Trailer_Tipper_Grain. These are not animations: rotate them from your own code or animation clips.

COLOUR VARIANTS
- One material per prefab. Green and Blue differ from Red only in the body-colour cells of the atlas.
- Tractors ship as Red / Green / Blue prefabs. Implements and trailers ship in Red: assign M_FarmMachinery_Green or
  M_FarmMachinery_Blue to all their renderers to recolour them.

LOD AND COLLIDERS
- LOD Group with LOD0 + LOD1 (about 50% triangles) on 11 of 13 models; LOD1 meshes are children of their moving
  parts (*_Low1). No LOD on QuickHitch and FrontWeight.
- One BoxCollider per prefab around the whole model (including wheels); pose variants have their own box.
- Triangles LOD0: 312 (FrontWeight) to 3,708 (DiscHarrow) per model, 28,872 for all 13 models.

URP SETUP
- The materials use Universal Render Pipeline/Lit. The project must use a URP pipeline asset.
- The demo scenes use a URP Volume (Demo/Settings/FarmMachinery_DemoVolume_V2) for post-processing, a panorama sky and
  unlit clouds (Demo/Shaders). Post-processing must be enabled on the URP renderer / camera to see the grade.

DEMO SCENES
- Demo_FieldWork: ploughing, grain haul and the machine yard (CMP_01-03) on a farm island.
- Demo_Catalog_Lite: all 21 prefabs in rows on a neutral background.
- Each demo scene has one active camera (Cam_Overview / Main Camera). Other Cam_* objects are inactive viewpoints:
  activate one and deactivate the others to look through it. There is no camera controller.

NOT INCLUDED
No scripts, driving physics, WheelColliders, Rigidbodies, rigs or animation clips. Cab glass is opaque, no cab
interior. Blender files and build scripts are not included.

FULL VERSION
Farm Machinery (Full) adds a combine harvester and a forage harvester with 3 swappable headers, a round baler, a hay
rake, a grain cart, bale and header trailers, a grain auger, a grain bin and a windrow module: 26 models, 41 prefabs,
5 compositions and a harvest demo scene. Lite and Full share file names and GUIDs, so importing Full over Lite
updates it in place.

SUPPORT
Contact us through the publisher profile on the Asset Store. Reviews are appreciated.
