from pathlib import Path
p=Path('.work/models/Farm_Processing/PRD15_OilBottle')
a=Path('.work/models/Farm_Processing/TOL_Tools/build_tools.py').read_text(encoding='utf-8')
render=a[a.index('def render(out,'):a.index('\ndef verify(fbx):')]
(p/'render_preview.py').write_text('# Preview helper copied from approved TOL_Tools registry render; no build side effects.\nimport bpy, math\nfrom mathutils import Vector\nNAME="FMS_Workshop_PRD_15"\nCFG={"view":(-0.36,-1,0.44),"fill":(0.8,0.88)}\n'+render,encoding='utf-8')
