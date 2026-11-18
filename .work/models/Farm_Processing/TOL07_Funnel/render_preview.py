# Rendering is shared with the idempotent build script. Run with Blender --background --factory-startup --python render_preview.py
import os, sys
sys.argv = [sys.argv[0], "--", "export"]
exec(compile(open(os.path.join(os.path.dirname(__file__), "build_funnel.py"), encoding="utf-8").read(), "build_funnel.py", "exec"))
