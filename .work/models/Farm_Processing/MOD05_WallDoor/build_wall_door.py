# MOD-05 Wall with doorway 2 m -> FMS_Workshop_MOD_05. Thin wrapper: the shared script ..\MOD03_Wall\build_wall_modules.py
# builds both MOD-03 ('plain') and MOD-05 ('door') on top of the MOD-04 wall contract.
#   blender --background --factory-startup --python build_wall_door.py -- <dry|check|export> door [round] [--pair]
import os, sys
if 'door' not in sys.argv: sys.argv += ['door'] if len(sys.argv) > sys.argv.index('--') + 1 else ['check', 'door']
_p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'MOD03_Wall', 'build_wall_modules.py')
exec(compile(open(_p, encoding='utf-8').read(), _p, 'exec'))
