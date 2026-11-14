"""Build store copy from the checked Farm Nature inventory."""
from pathlib import Path
import json,html,re
from datetime import date
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).parent
UPDATED=date.today().isoformat()
A=json.loads((OUT/'PACKAGE_AUDIT.json').read_text())
FIELDS=OUT/'Copy_Fields';FIELDS.mkdir(exist_ok=True)
title='Farm Nature - Low Poly Crops, Trees & Landscape'
summary='Build colorful countryside scenes with 88 low-poly models: crops in 3 growth stages, orchard and forest trees, flowers, ponds, paths and ground pieces. Includes a showcase scene.'
tags='low poly, stylized, farm, farming, nature, crops, growth stages, trees, foliage, flowers, garden, orchard, modular, landscape, URP'
description='''Bring your countryside to life.

Farm Nature is a colorful low-poly art pack for farm games, cozy countryside scenes and stylized outdoor worlds. Build a vegetable garden, surround it with an orchard, connect areas with paths and streams, then finish the scene with flowers, rocks and woodland details.

The pack contains 88 individual models and 88 ready-to-place prefabs. It focuses on the plants and landscape around a farm, with a consistent faceted style across crops, trees, ground pieces and decorations.

KEY FEATURES

- Seven crops with three separate growth-stage models each: wheat, corn, carrot, cabbage, tomato, pumpkin and sunflower.
- Three wheat field tiles: green, golden and stubble.
- Fruit and blossom apple trees, green and autumn oak, birch, spruce and willow.
- Individual path, ground, stream and hedge pieces for building your own layouts.
- Raised beds, soil rows, a trellis and stakes for garden scenes.
- Ponds, puddles, lily pads, a wooden bridge, rocks, logs and firewood.
- One Box Collider on each of the 88 art prefabs.
- One showcase scene with category displays, an overall landscape and six local scene studies.

WHAT'S INSIDE

24 crop models — seven crops in three growth stages, plus three wheat field tiles.
9 trees — large green oak, autumn oak, two birch sizes, two spruce sizes, willow, fruiting apple tree and apple blossom tree.
6 garden bed and support models — a soil row, two raised bed sizes, a 4x4 plot, a trellis and a row of stakes.
5 flower models — daisy, lavender, meadow flowers, poppy and tulip.
4 grass and reed models — small and medium grass tufts, tall grass and reeds.
3 bushes — round, flowering and berry bushes.
3 hedge pieces — straight, corner and end.
1 fern.
6 ground pieces — grass and dirt tiles, hill, edge, inner corner and outer corner.
7 path models — dirt straight, curve, T-junction and end; stone straight and curve; stepping stones.
9 water and crossing models — round and oval ponds, two puddles, straight/curved/end stream sections, lily pads and a wooden bridge.
6 rocks — small, medium and large rocks, a boulder, a flat rock and a rock cluster.
5 wood details — stump, log, fallen log, firewood pile and firewood stack.

SCENE EXAMPLES

Explore a vegetable garden, harvest field, apple orchard, pond and bridge, forest edge and flower path in Demo_FarmNature_Showcase. The local studies are arranged inside the demo scene; they are not separate composition prefab assets.

CROP STAGES

Each crop stage is a separate static prefab, so your game can replace one stage with the next. Farming logic, growth timers, harvesting interactions, saving and economy systems are not included.

RENDERING AND SCOPE

The supplied art materials use Universal Render Pipeline/Lit. The authoring project uses Unity 6000.3.10f1 and URP 17.3.0. Built-in and HDRP material sets are not supplied.

This is a static 3D art pack. There are no LOD levels, rigs, animation clips, animated wind or water simulation. Water is represented by stylized static meshes and materials. Box Colliders provide simple bounds; they do not follow every contour of irregular objects or water surfaces.

Farm buildings, animals, characters, vehicles and a complete farming game are outside this pack's scope. Source models are supplied as FBX and textures as PNG; native Blender/Maya project files are not included.'''
stats=A['category_stats'];s=A['summary']
labels={'Bed':'Garden beds and supports','Bush':'Bushes','Crop':'Crops and field tiles','Flower':'Flowers','Grass':'Grass and reeds','Ground':'Ground','Hedge':'Hedges','Path':'Paths','Plant':'Fern','Rock':'Rocks','Tree':'Trees','Water':'Water and crossing pieces','Wood':'Wood details'}
tris_lines='\n'.join(f"{labels[k]}: {v['model_files']} models; {v['triangles_min']:,}-{v['triangles_max']:,} triangles per model; {v['triangles_sum']:,} triangles total." for k,v in stats.items())
technical=f'''ASSETS AND PREFABS
88 FBX model files, containing 88 mesh objects; 88 individual art prefabs. Crop stages, size variants and shape/color variants are counted separately. The count is not 88 different item types. Six local scene studies are inside the demo scene; no separate composition prefabs are supplied.

POLYGON COUNT
Base mesh / LOD0 equivalent: {s['triangles_min']:,}-{s['triangles_max']:,} triangles per model; mean {s['triangles_mean']:,.2f}; total {s['triangles_sum']:,} across the 88 model files, with each file counted once. Repeated objects in the demo scene are not included in this total.

Measured from source FBX polygon indices, triangulating each n-sided polygon as n-2 triangles. These are source mesh figures, not draw-call counts or runtime scene totals. Unity import output has not been independently compared against these values.

{tris_lines}

LODS
None. No LODGroup components in the 88 art prefabs; generated mesh LODs are disabled in the model import settings.

TEXTURES
Art: 27 PNG Base Color textures, all 256x256, RGB, opaque.
Demo only: 2 additional RGB PNG textures — grass at 256x256 and sky panorama at 512x512.
29 PNG texture files in total. No normal, metallic, roughness, occlusion, emission or height texture maps are supplied. The art textures use color-palette/atlas-style UV layouts; they are not a single shared atlas. Art texture import settings use Point filtering with mipmaps disabled.

MATERIALS AND SHADERS
Art: 27 materials using Universal Render Pipeline/Lit.
Demo only: 8 additional materials, 7 using URP/Lit and 1 using FarmNature/Demo/URP Panorama Sky.
35 material files total. One custom URP-compatible sky shader source is included under Demo/Shaders for the demo panorama. Water materials are opaque static stylized surfaces, without a water simulation or animated water shader.

UVS
One UV channel per source mesh. No second lightmap UV channel is present in the source geometry; automatic secondary UV generation is disabled in the current import settings.

RIGGING AND ANIMATIONS
Static meshes. No skeletons, skinned renderers, Animator components or animation stacks/clips were found in the model/prefab files. Crop growth stages are separate model variants rather than animations.

COLLIDERS
88 Box Colliders, one per individual art prefab. No Mesh Colliders. The colliders use whole-object bounds, so exact contact on curved paths, ponds, bridge openings and irregular vegetation requires project-specific collider adjustment.

SCALE AND SETUP
Prefab root position (0,0,0), rotation identity, scale (1,1,1). FBX import scale is 1; file units have UnitScaleFactor 100 (metre-scale files in FBX's centimetre convention), with Y as the source up axis. Geometry is at or near ground level; smallest source Y offsets are 0-0.001462 units. Art prefab names use the FMS_ prefix. Grid fitting, snapping and gameplay placement should be checked for each piece in the target scene; no automatic terrain or road-building tool is supplied.

FILES AND SOURCES
88 FBX models, 88 Unity prefabs, 29 PNG textures, 35 Unity materials and 1 Unity scene under Assets/FarmNature, plus Unity .meta files. No native DCC project files, runtime scripts, audio or video files are included in that folder. Editor build/render helpers are maintained separately under Assets/Editor/FarmNature; they are production tools rather than a runtime farming system.

DEMO
One scene: Assets/FarmNature/Demo/Scenes/Demo_FarmNature_Showcase.unity.
Contains six category displays, six local scene studies, an overall composition and an icon vignette. The scene uses URP lighting metadata and additional demo ground/sky materials and textures. No scripted demo camera controls or player controller are included. Inspect the scene with normal Unity Scene view controls.

COMPATIBILITY AND DEPENDENCIES
Authoring project: Unity 6000.3.10f1; com.unity.render-pipelines.universal 17.3.0. These identify the current source configuration; a clean-project import test and platform benchmarks have not been completed as part of this metadata audit.
URP is required for the supplied Lit materials. Built-in and HDRP conversions are not supplied. Individual static art prefabs contain no custom runtime scripts. Their use does not require a farming framework, third-party controller, or another farm asset pack.

PACKAGE SIZE
Final exported .unitypackage size is not yet available. The raw Assets/FarmNature folder is {s['raw_folder_bytes']:,} bytes ({s['raw_folder_bytes']/1048576:.2f} MiB), including .meta files; this is not the compressed Asset Store download size.'''
release='''Initial release content:
- 88 low-poly models and 88 individual prefabs.
- Seven crops in three growth stages, plus three wheat field tiles.
- Trees, bushes, flowers, grasses, hedges, fern, ground, paths, water pieces, rocks and wood details.
- Box Colliders on all 88 individual art prefabs.
- 27 art materials and 27 Base Color textures, plus demo materials and textures.
- One showcase scene with six local scene studies.

Static art assets. No LODs, rigs, animation clips or farming gameplay system. Supplied art materials target URP.'''
compat='''Authoring environment: Unity 6000.3.10f1 with Universal Render Pipeline 17.3.0.
Supplied art materials: Universal Render Pipeline/Lit.
Built-in/HDRP material sets: not included.
Other Unity versions, clean-project import and target-device performance: not independently tested in this preparation pass.'''
deps='''Universal Render Pipeline is required for the supplied art materials. The authoring project uses com.unity.render-pipelines.universal 17.3.0 with Unity 6000.3.10f1.

Individual art prefabs contain no custom runtime scripts. No separate farming system, controller or other farm pack is required for those prefabs. The demo uses the same render pipeline, plus its included demo materials/textures and its included URP Panorama Sky shader. Other packages in the development project's manifest are not declared as requirements of this art pack.'''
notes='''Farm Nature is a static art package containing 88 source FBX models and 88 individual prefabs. Counts include crop growth stages and size/appearance variants. Local compositions are objects inside Demo_FarmNature_Showcase, not separate composition prefab assets.

Source geometry ranges from 60 to 6,514 triangles per model. Each art prefab has one Box Collider. No LODs, rigs or animations are provided. Supplied art materials use URP/Lit. Crop growth, wind, water simulation and farming gameplay are not included.

The technical description distinguishes art resources from demo resources and source folder size from exported download size. Gallery and key images show actual project renders with vector graphic overlays. The selected product icon is an AI-assisted stylized marketing illustration derived from the project's apple-tree render; it is not a screenshot of the supplied model.'''
verification_path=OUT/'RELEASE_VERIFICATION.json'
verification=json.loads(verification_path.read_text()) if verification_path.exists() else None
if verification and verification.get('clean_import'):
    compat='''Verified clean .unitypackage import and static demo rendering in Unity 6000.3.10f1 with Universal Render Pipeline 17.3.0. All 88 art prefabs passed mesh, material, root transform and collider-count checks. The showcase has one enabled camera and no references to Assets outside Assets/FarmNature.
Supplied art materials: Universal Render Pipeline/Lit. Optional demo renderer/pipeline assets are included; importing the package does not automatically override project graphics settings.
Built-in/HDRP material sets: not included. Other Unity versions and target-platform player builds/performance have not been tested.'''
    technical=technical.replace('Unity import output has not been independently compared against these values.','Verified against imported Unity Mesh.triangles for all 88 art prefabs in a separate project; min, max and total match the source measurements.')
    technical=technical.replace('No native DCC project files, runtime scripts, audio or video files are included in that folder.','No native DCC project files, runtime scripts, audio or video files are included in that folder. An editor-only Getting Started window, user documentation, model inventory and Changelog are included.')
    technical=technical.replace('Inspect the scene with normal Unity Scene view controls.','Inspect the scene with normal Unity Scene view controls or the Getting Started window. The release hierarchy groups the overview, six scene studies, category collection and presentation resources. Extra production cameras and the icon-only vignette are removed; one overview camera remains.')
    technical=technical.replace('Contains six category displays, six local scene studies, an overall composition and an icon vignette.','Contains six category displays, six local scene studies and an overall composition.')
    start=technical.index('COMPATIBILITY AND DEPENDENCIES\n')
    technical=technical[:start]+'COMPATIBILITY AND DEPENDENCIES\n'+compat+'\nURP is required for the supplied Lit materials. Individual static art prefabs contain no runtime scripts and do not require another farm pack or gameplay framework.\n\nPACKAGE SIZE\n'+f"Version 1.0.0 exported .unitypackage: {verification['package_bytes']:,} bytes ({verification['package_bytes']/1048576:.2f} MiB). Only Assets/FarmNature paths are included."
    notes+='\n\nThe final .unitypackage was imported into a separate Unity 6000.3.10f1 / URP 17.3.0 project. Static prefab checks and demo rendering completed; imported mesh triangle counts matched the source inventory. No cross-pack Assets dependencies were found. See the retained validation report for scope and any Asset Store Tools warnings.'
    release+='\n- Organized release demo with one camera, documentation, model inventory, optional URP demo settings and an editor-only Getting Started window.\n- Verified clean import and static asset checks in Unity 6000.3.10f1 / URP 17.3.0.'
version='1.0.0'
support='For questions and support, contact sergvved@gmail.com. Please include your Unity version, render pipeline version and a description of the issue.'
release='Version '+version+' — '+release[0].lower()+release[1:]
field_values={'Title':title,'Category':'3D / Environments / Landscapes','Price':'9.99 USD','Version':version,'Support':support,'Support_Email':'sergvved@gmail.com','Tags':tags,'Summary':summary,'Description':description,'Technical_Details':technical,'Changelog':release,'Release_Notes':release,'Compatibility':compat,'Dependencies':deps,'Submission_Notes':notes}
for name,value in field_values.items():(FIELDS/(name+'.txt')).write_text(value+'\n',encoding='utf8')
def to_html(text):
 blocks=[]
 for b in text.split('\n\n'):
  if b.isupper() and len(b)<90:blocks.append('<h3>'+html.escape(b.title())+'</h3>')
  elif all(x.startswith('- ') for x in b.splitlines()):blocks.append('<ul>'+''.join('<li>'+html.escape(x[2:])+'</li>' for x in b.splitlines())+'</ul>')
  else:blocks.append('<p>'+html.escape(b).replace('\n','<br>')+'</p>')
 return '\n'.join(blocks)
for name in ['Description','Technical_Details']:(FIELDS/(name+'.html')).write_text(to_html(field_values[name]),encoding='utf8')
media=json.loads((OUT/'Media/media-manifest.json').read_text())
media_rows='\n'.join(f"| `{x['file']}` | {x['width']}x{x['height']} | Prepared, local review complete |" for x in media['images'])
meta=f'''# Farm Nature — Asset Store package metadata

Updated: {UPDATED}. Scope: current Assets/FarmNature source files. Status: descriptions prepared; remaining publisher information is tracked in PUBLISHER_NOTES.md and completed release validation in RELEASE_VERIFICATION.json. No portal fields were changed.

Copy-ready English fields are below and in [Copy_Fields](Copy_Fields). Business fields and unresolved release checks are tracked separately in [PUBLISHER_NOTES.md](PUBLISHER_NOTES.md). Audit evidence: [PACKAGE_AUDIT.json](PACKAGE_AUDIT.json), [MODEL_INVENTORY.csv](MODEL_INVENTORY.csv).

Title length: {len(title)} characters. Summary length: {len(summary)} characters including spaces, excluding the terminating newline. Tags: {len(tags.split(', '))}. These are local preparation figures; current authenticated portal limits have not been inspected.

'''
for name,value in field_values.items():meta+='## '+name.replace('_',' ')+'\n\n```text\n'+value+'\n```\n\n'
meta+='''## Media

| File, relative to Media | Dimensions | Status |
|---|---|---|
'''+media_rows+'''

Video: none prepared. Social: included above. The selected default icon is an AI-assisted stylized illustration with a blue background and diagonal 3D corner, derived from the apple-tree render. The original generation, reference backup and prompt are retained in Media/IllustratedIcon. It is illustrative marketing artwork; the gallery shows the actual low-poly asset appearance.

## Publication fields still awaiting publisher data

Publisher website and final documentation link; AI origin/tool disclosure and third-party license confirmation. Price is 9.99 USD, release version is 1.0.0, and the publisher-provided support email is sergvved@gmail.com. No introductory discount has been configured. See PUBLISHER_NOTES.md for precise status and next actions.
'''
(OUT/'PACKAGE_METADATA.md').write_text(meta,encoding='utf8')
(OUT/'metadata-fields.json').write_text(json.dumps({'updated':UPDATED,'release_status':'copy prepared; remaining publisher information in PUBLISHER_NOTES.md; completed validation in RELEASE_VERIFICATION.json','fields':field_values,'counts':{'title_characters':len(title),'summary_characters':len(summary),'tags':len(tags.split(', '))},'publisher_fields_pending':['publisher_website','documentation_link','functional_asset_ai_tools_and_modifications','third_party_licenses'],'evidence':'PACKAGE_AUDIT.json'},ensure_ascii=False,indent=2),encoding='utf8')
print('Wrote PACKAGE_METADATA.md, '+str(len(field_values))+' copy fields, 2 HTML fields, metadata-fields.json')
print('Title:',len(title),'Summary:',len(summary),'Tags:',len(tags.split(', ')))
