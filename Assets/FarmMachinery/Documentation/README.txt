FARM MACHINERY  (v1.0.0)
Stylized low poly farm machinery: 26 models (41 prefabs with colour, pose and load variants) + 5 ready compositions.
Tractors, implements, trailers, combine and forage harvesters with swappable headers, round baler and grain yard.
Gameplay-ready hierarchy: separate wheels, named attach points, moving parts on their pivots, LOD1, Box Colliders.

REQUIREMENTS
- Unity 6000.3 (built with 6000.3.10f1).
- Universal Render Pipeline (URP) 17.3. Built-in Render Pipeline and HDRP are not supported.
- No scripts, no other packages.

QUICK START
1. Open Demo/Scenes/Demo_Harvest.unity or Demo_FieldWork.unity and press Play (or look through the Game view).
2. Demo/Scenes/Demo_Catalog.unity shows all 41 prefabs in rows.
3. Drag any prefab from Art/Prefabs/<Category> into your scene. Art/Prefabs/CMP holds the ready compositions.

FOLDERS
Art/Models          FBX meshes (LOD0 + LOD1 parts), one FBX per model, grouped by category
Art/Textures        3 colour atlases, 256 x 256 PNG (Red, Green, Blue)
Art/Materials       3 URP/Lit materials: M_FarmMachinery_Red / Green / Blue
Art/Prefabs         Prefabs by category (TRC, IMP, TRL, ATT, HRV, EQP, PRP) and compositions (CMP)
Demo                Demo scenes and demo-only assets (island ground, fields, wheat, road, grass, bales, clouds,
                    sky, post-processing volume). Not counted as product models. Safe to delete.
Documentation       This file and the changelog

PREFABS  (naming: FMS_Mach_<Name> for a base prefab, FMS_Mach_<Name>_<Variant> for a Prefab Variant)
TRC Tractors (2)    Tractor_Cab, Tractor_Large                         + _Green, _Blue of each
IMP Implements (7)  Plough, Seeder, Sprayer, Mower, DiscHarrow, Cultivator, HayRake
                    + Sprayer_Work, Mower_Work, DiscHarrow_Work, HayRake_Work (work poses; the base is the transport pose)
TRL Trailers (6)    Trailer_Tipper, Trailer_Flatbed, Trailer_Tank, GrainCart, Trailer_Bale, Trailer_Header
                    + Trailer_Tipper_Grain, GrainCart_Full (grain load on; the base is empty)
ATT Attachments (5) QuickHitch, FrontWeight, Header_Grain, Header_Corn, Header_Pickup
HRV Harvesters (3)  Combine, ForageHarvester (+ _Green, _Blue of each), Baler_Round (+ Baler_Round_Open)
EQP Grain yard (2)  GrainAuger, GrainBin
PRP Field prop (1)  Windrow (4 m module, snaps end to end)
CMP Compositions(5) CMP_01_Ploughing, CMP_02_GrainHaul, CMP_03_MachineYard, CMP_04_Harvest, CMP_05_Haymaking
                    (built only from the prefabs above; they add no new models)

GAMEPLAY-READY CONTRACT
- Scale 1 unit = 1 m, Y up, every machine faces +Z. The root pivot is on the ground (Y = 0) at the centre of the
  footprint; root scale 1, rotation 0.
- Wheels: every wheel is its own child object (tyre + rim) with the pivot at the wheel centre and the spin axis on
  local X. Names: Wheel_<Axle><Side> - axles F / M / R from front to rear, sides L / R (Wheel_FL, Wheel_RR);
  a single axle uses Wheel_L / Wheel_R, a plough gauge wheel is Wheel_Gauge. Steer by rotating about local Y.
  The pack has no WheelCollider: add your own on empty objects at the wheel centres if you use Unity physics.
- Attach points are empty GameObjects (+Z forward, +Y up). A pair matches in position and rotation:
    Hitch_Rear  (tractor / combine drawbar pin)  <->  Hitch_Front  (trailer or trailed implement drawbar eye)
    Link3P_Rear (tractor 3-point linkage)        <->  Link3P_Front (mounted implement)
    PTO_Rear    (tractor PTO shaft end)          <->  PTO_Front    (implement PTO input)
    Feeder_Front (combine / forage harvester)    <->  Feeder_Rear  (header)
    Link3P_Front of Tractor_Large                <->  Link3P_Rear of FrontWeight
  Standard rest heights: Hitch 0.55 m, Link3P 0.60 m, PTO 0.70 m. Link3P_* points are children of the Linkage_*
  part and rise with it. Service points: Seat, Auger_Out, Spout_Out, Bale_Out (baler) and Header_Rest (header trailer).
- To attach B to A: rotate and move B so that B's point lies exactly on A's point, e.g. in a script
      Quaternion rel = Quaternion.Inverse(b.rotation) * bPoint.rotation;
      Vector3 local = b.InverseTransformPoint(bPoint.position);
      Quaternion rot = aPoint.rotation * Quaternion.Inverse(rel);
      b.SetPositionAndRotation(aPoint.position - rot * local, rot);
      b.SetParent(aPoint, true);   // optional: B now follows A
  All 5 compositions are assembled this way (0.0 mm joint error).
- Combine and forage harvester prefabs come without a header: put Header_Grain, Header_Corn or Header_Pickup on
  Feeder_Front. QuickHitch, FrontWeight and the headers are modelled at their mounted height, so they float above
  Y = 0 when placed alone.
- Moving parts are separate objects with the pivot on their hinge axis (rest = transport / closed): doors (Door_L),
  tractor links (Linkage_Rear / Linkage_Front), tipper Bed and Tailgate, sprayer Boom_L/R, seeder Lid and
  Marker_L/R, mower Bar, harrow Wing_L/R, cultivator Roller, tank Hatch, combine Feeder, Reel_Arm / Reel,
  Auger_Cross and Auger_Unload, forage Spout / Spout_Tip, baler Pickup and Tailgate, rake Arm_L/R and Rotor_L/R,
  grain cart Auger_Unload, bin Door and Roof_Hatch. Load_Grain is a child mesh switched on in the _Grain / _Full variants.
  These are not animations: rotate them from your own code or animation clips.

COLOUR VARIANTS
- One material per prefab. Green and Blue differ from Red only in the body-colour cells of the atlas.
- Tractors, combine and forage harvester ship as Red / Green / Blue prefabs. Implements and trailers ship in Red:
  assign M_FarmMachinery_Green or M_FarmMachinery_Blue to all their renderers to recolour them.

LOD AND COLLIDERS
- LOD Group with LOD0 + LOD1 (about 50% triangles) on 22 of 26 models; LOD1 meshes are children of their moving
  parts (*_Low1), so a rotated wheel or part keeps both levels aligned. No LOD on QuickHitch, FrontWeight,
  Trailer_Header and Windrow.
- One BoxCollider per prefab around the whole model (including wheels); pose variants have their own box.
- Triangles LOD0: 76 (Windrow) to 3,708 (DiscHarrow) per model, 54,464 for all 26 models.

URP SETUP
- The materials use Universal Render Pipeline/Lit. The project must use a URP pipeline asset.
- The demo scenes use a URP Volume (Demo/Settings/FarmMachinery_DemoVolume_V2) for post-processing, a panorama sky and
  unlit clouds (Demo/Shaders). Post-processing must be enabled on the URP renderer / camera to see the grade.

DEMO SCENES
- Demo_FieldWork: ploughing, grain haul and the machine yard (CMP_01-03) on a farm island.
- Demo_Harvest: harvest and haymaking (CMP_04-05), forage harvester with pickup header and a tipper, combine with corn
  header, header trailer with grain header, grain bins and auger, on a farm island with wheat and stubble.
- Demo_Catalog: all 41 prefabs in rows on a neutral background.
- Each demo scene has one active camera (Cam_Overview / Main Camera). Other Cam_* objects are inactive viewpoints:
  activate one and deactivate the others to look through it. There is no camera controller.

NOT INCLUDED
No scripts, driving physics, WheelColliders, Rigidbodies, rigs or animation clips. Cab glass is opaque, no cab
interior. Drive shafts are not modelled. Blender files and build scripts are not included.

LITE VERSION
Farm Machinery Lite is a free subset of this pack (13 tractor, implement and trailer models) with the same file names
and GUIDs, so importing this pack over Lite updates it in place.

SUPPORT
Contact us through the publisher profile on the Asset Store. Reviews are appreciated.
