# Headless convenience: rebuild + numeric checks, then render final preview only.
from pathlib import Path
import runpy
ns=runpy.run_path(str(Path(__file__).with_name('build_measuring_jug.py')),run_name='jug_preview')
ns['build']()
ns['render'](ns['os'].path.join(ns['ART'],'Previews',ns['NAME']+'_Preview.png'),100)
