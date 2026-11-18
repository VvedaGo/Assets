import subprocess,os
from pathlib import Path
folder=Path(__file__).resolve().parent
cmd=[r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe','--background','--factory-startup','--python',str(folder/'build_funnel.py'),'--','build','0,-1,-0.65']
r=subprocess.run(cmd,env=dict(os.environ,PYTHONUTF8='1'),capture_output=True,text=True,encoding='utf-8');print(r.stdout);print('BLENDER_RETURN_CODE',r.returncode);assert r.returncode==0
cmd[-3:]=['--','export']
r=subprocess.run(cmd,env=dict(os.environ,PYTHONUTF8='1'),capture_output=True,text=True,encoding='utf-8');(folder/'validation.log').write_text(r.stdout+'\n'+r.stderr+'\nBLENDER_RETURN_CODE '+str(r.returncode),encoding='utf-8');print(r.stdout);print('BLENDER_RETURN_CODE',r.returncode);assert r.returncode==0
assert 'VERIFY nodes 2 total tris 348' in r.stdout and "True, (256, 256)" in r.stdout
