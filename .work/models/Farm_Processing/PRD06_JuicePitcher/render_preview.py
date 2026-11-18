from pathlib import Path
import runpy
ns=runpy.run_path(str(Path(__file__).with_name('build_juice_pitcher.py')),run_name='pitcher_preview')
ns['build']()
ns['render'](ns['os'].path.join(ns['ART'],'Previews',ns['NAME']+'_Preview.png'),100)
