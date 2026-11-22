---
name: blender-unity-assets
description: Create or prepare Blender models for Unity with project-specific references, export budgets and visual verification.
---

Read the target art project's pipeline, reference image, approved anchor and explicit style/budget. Do not apply the Farm Processing house style, branch paths, palette, model counts or iteration quotas to another project. If Tools/blender exists, inspect Tools/README and reuse its approved helpers without changing shared code casually.

Headless scripted modeling is suitable for reproducible work; live Blender MCP is optional if the task benefits from interactive inspection. Detect the installed executable and API version rather than hardcoding a user path. Missing MCP does not block an authorized headless workflow.

Confirm scale, axes, pivots, moving-part separation, topology, UV/material requirements and LOD policy. Inspect previews beside the reference, including small-size readability. Batch useful fixes and stop when acceptance is met; do not force five iterations of an already-correct result. Export selected objects only, reimport to verify hierarchy, dimensions and textures, and report numeric/visual checks honestly.

Never overwrite unrelated objects, shared atlases or the user's blend file. Paid generation/downloads require explicit spending authorization. Unity import is a distinct step; use its asset pipeline and preserve meta GUIDs. Pack-specific lessons belong in that pack's pipeline documentation.
