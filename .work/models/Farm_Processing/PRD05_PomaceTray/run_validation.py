import os,subprocess,sys
from pathlib import Path
p=Path(__file__).resolve().parent
env=os.environ.copy();env['PYTHONUTF8']='1'
r=subprocess.run([r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe','--background','--factory-startup','--python',str(p/'build_pomace_tray.py'),'--','export'],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
text=r.stdout.decode('utf-8',errors='replace')+'\nSUBPROCESS_RETURN_CODE '+str(r.returncode)+'\n'
(p/'validation.log').write_text(text,encoding='utf-8');print(text)
sys.exit(r.returncode)
