import runpy,os
from pathlib import Path
ns=runpy.run_path(str(Path(__file__).with_name('build_measuring_jug.py')),run_name='handle_qa')
ns['build']();os.makedirs(ns['CHECK_DIR'],exist_ok=True)
ns['render'](os.path.join(ns['CHECK_DIR'],'handle_mount_check.png'),40,(.8,-1,.57))
