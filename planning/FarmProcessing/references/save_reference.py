from pathlib import Path
import json,sys,shutil
root=Path(__file__).parent
item_id,source=sys.argv[1:3]
f=root/'GENERATION_MANIFEST.json'
a=json.loads(f.read_text(encoding='utf-8'))
item=next(x for x in a if x['id']==item_id)
shutil.copy2(source,root/item['file'])
item['status']='generated'
item['style_reference']='STA-01.png' if item_id!='STA-01' else None
item['generation_method']='built-in image_gen'
if item_id != 'STA-01':
 item['used_prompt'] = item['prompt'] + '\nInput image: STYLE REFERENCE ONLY, the approved first asset STA-01 of this same pack. Generate a NEW asset of the subject specified above, never another vat. Match its low-poly flat facets, matte materials, palette, neutral background, soft studio lighting and three-quarter framing. Complete object with margins, no cropping. Asset ID ' + item_id + ' (do not render text).'
if len(sys.argv) > 3:
 item['used_prompt'] = Path(sys.argv[3]).read_text(encoding='utf-8-sig')
f.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f=root.parent/'MODEL_CATALOG.md'
lines=f.read_text(encoding='utf-8').splitlines()
for i,l in enumerate(lines):
 if l.startswith('| '+item_id+' |'):
  lines[i]=l.rsplit(' | ',1)[0]+' | !['+item_id+'](references/'+item['file']+') |'
f.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(item_id+' saved and linked')
stop = root / '.stop_after_save'
if stop.exists():
 stop.unlink()
 sys.exit(2)
