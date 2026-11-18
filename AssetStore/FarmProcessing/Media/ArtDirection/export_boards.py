"""Export the authored HTML layouts using the Orca browser already selected for this task."""
from pathlib import Path
import argparse,json,subprocess,shutil,struct

ROOT=Path(__file__).resolve().parent
CLI=r'C:\Users\Sergv\AppData\Local\Programs\orca\resources\bin\orca.exe'
SHOTS=['01_Icon','02_Card','03_Cover','04_Social','05_Hero','06_FullCollection','07_Closeups','08_VariantsAndModules','09_Technical','10_DemoAndVersion','11_CategoryDetails','12_Compositions','13_Materials','14_UnityAndComparison','15_StationsCatalog','16_ModulesCatalog']
DIMS={'01_Icon':(1024,1024),'02_Card':(1260,840),'03_Cover':(1950,1300),'04_Social':(1200,630)}

def cli(*args):
    p=subprocess.run([CLI,*args,'--json'],capture_output=True,text=True,encoding='utf-8',timeout=60)
    try:r=json.loads(p.stdout)
    except Exception:raise RuntimeError(p.stdout+p.stderr)
    if not r.get('ok'):raise RuntimeError(json.dumps(r,ensure_ascii=False))
    return r['result']

def export(page,shot,w,h,destination):
    cli('eval','--page',page,'--expression',f'window.setShot({json.dumps(shot)})')
    cli('viewport','--page',page,'--width',str(w),'--height',str(h),'--scale','1')
    result=cli('eval','--page',page,'--expression',"(async()=>{await document.fonts.ready;await Promise.all(Array.from(document.images).map(x=>x.decode().catch(()=>null)));return {shot:window.currentShot,width:innerWidth,height:innerHeight,images:document.images.length,missing:Array.from(document.images).filter(x=>!x.naturalWidth).map(x=>x.src)}})()")
    metrics=json.loads(result['result']) if isinstance(result.get('result'),str) else result.get('result',result)
    assert not metrics['missing'],metrics
    assert metrics['width']==w and metrics['height']==h,metrics
    r=cli('screenshot','--page',page)
    shutil.copy2(r['path'],destination)
    data=destination.read_bytes()
    assert struct.unpack('>II',data[16:24])==(w,h)
    print(shot,str(w)+'x'+str(h),'saved',flush=True)
    return metrics

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--page',required=True);ap.add_argument('--shots',nargs='*');args=ap.parse_args()
    audit=[]
    for shot in args.shots or SHOTS:
        w,h=DIMS.get(shot,(1920,1080))
        dest=ROOT/('Layouts' if shot in ['09_Technical','13_Materials','14_UnityAndComparison'] else 'Boards')/(shot+'.png')
        audit.append(export(args.page,shot,w,h,dest))
    if not args.shots:
        for shot,w,h in [('01_Icon',160,160),('02_Card',420,280)]:
            export(args.page,shot,w,h,ROOT/'Boards'/(shot+f'_{w}x{h}.png'))
    (ROOT/'export-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
