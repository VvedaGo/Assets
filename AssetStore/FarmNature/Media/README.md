# Farm Nature media — revision 2

Rebuilt 2026-11-13 after visual feedback. Review `ContactSheet_v2.jpg` or `index.html`. Delivery: `FarmNature_Upload_v2.zip`. `Upload/` and `FarmNature_Upload.zip` also contain revision 2. Previous results: `FarmNature_Upload_v1.zip` and `ContactSheet_v1.jpg`.

## Design

Evergreen #203D32, apricot #ED7047, golden #F5C85D and cream #FFF9EB. Impact headlines, Arial secondary text; no font files redistributed. Step-cut plaques, angled accent ribbons, diagonal 3D corner flush with the top/left edges of Card and Cover.

Three related layout families replace the repeated footer: stepped key-image lockups; compact layered category title plates; light scene-study captions alternating sides with the composition. Crops and Modules use editorial side panels and detailed original Unity part renders. Their precise source paths are recorded in `media-manifest.json`. Remaining gallery views preserve the supplied Beauty renders at full frame.

Icon was repainted at the publisher's request as a richer stylized marketing illustration: blue sky, sunlit organic foliage, red apples, a warm curved trunk and a flush top-left coral 3D corner. Master: `01_Icon.png`, 1024x1024; current upload: `Upload/01_Icon.png`, opaque 160x160. Built-in image_gen was used with the prior icon as a subject reference and Farm Market's illustrated icon as a style reference. The full generated original, prior Unity-rendered master and exact prompt are saved in `IllustratedIcon/`. The icon is illustrative marketing artwork; the package's low-poly models are shown by the actual Unity renders in the gallery. Rebuilding media preserves the selected illustrated icon.

## Deliverables and checks

- Icon: 160×160 PNG, 1024×1024 master.
- Card: 420×280 JPEG, separate 1260×840 master.
- Cover: 1950×1300 JPEG and PNG master.
- Social: 1200×630 JPEG and PNG master, no advertising text.
- Gallery: thirteen 1920×1080 JPEGs and PNG masters.

All 17 uploads have exact dimensions and opaque RGB data. Card/Cover corner placement was checked from exported pixels. Full-size examples and the contact sheet were visually reviewed. `validation.json` records checks. `Editable/` contains self-contained SVGs with embedded source renders.

## References

Actual key images were inspected: saved Searcher sheets and freshly downloaded product images. Current key images were selected from matching product IDs in page state, excluding recommended products. `References-v2/sources.json` records source URLs. Reference artwork is not used in deliverables and is not in the upload ZIP.

- Synty Simple Farm: https://assetstore.unity.com/packages/3d/environments/industrial/simple-farm-cartoon-assets-47003
- Synty POLYGON Nature: https://assetstore.unity.com/packages/3d/vegetation/trees/polygon-nature-pack-art-by-synty-120152
- Polyperfect Low Poly Ultimate Pack: https://assetstore.unity.com/packages/3d/props/low-poly-ultimate-pack-54733
- Polytope Low Poly Farm Pack Lite: https://assetstore.unity.com/packages/3d/environments/industrial/low-poly-farm-pack-lite-188100

Applied principles: tighter subjects, condensed headlines, compact corner ribbons, layered accents, less repetitive framing. No competitor logos or artwork are used. Sales/conversion performance is not known.

## Scope

88 FBX files and 88 individual art prefabs counted; crops/beds/trees: 24/6/9 prefab files. File counts are not a geometry uniqueness audit. No untested performance, pipeline, LOD or collider promise is printed. Scene studies are not claimed as included composition prefab files.

17 images intentionally depart from the local 14-image baseline: four key images and thirteen category/scene views. A neutral-background complete catalog, wireframe/tris/LOD/collider, materials and Unity Inspector captures remain separate release tasks. Publisher Portal acceptance and slots were not checked. Nothing was uploaded or published.

Unity policy reference: https://unity.com/legal/asset-store-content-transparency . Gallery images use actual Unity renders; the selected icon is an AI-assisted illustrative marketing image requested by the publisher. Underlying 3D asset provenance is outside this review.

## Rebuild

From `AssetStore/FarmNature`: `npm install --prefix .media-tools @resvg/resvg-js sharp`, `node build_media.cjs`, `python finalize_media.py` (Pillow required). Source renders and Unity assets are unchanged. `build_media_v1.cjs` preserves the earlier design code.
