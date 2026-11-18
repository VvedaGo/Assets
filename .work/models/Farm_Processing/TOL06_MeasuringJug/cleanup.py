from pathlib import Path
import os,shutil
base=Path(__file__).resolve().parent
for name in ['init_local.py','revise.py','revise3.py','final_fix.py','round1.log','round2.log','round3.log']:
 p=base/name
 if p.is_file():p.unlink()
d=Path(os.environ['TEMP']).resolve()/'FarmProcessing_check'/'TOL06'
assert d.resolve().parent==Path(os.environ['TEMP']).resolve()/'FarmProcessing_check'
if d.is_dir():shutil.rmtree(d)
