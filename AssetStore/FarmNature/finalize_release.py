"""Synchronize the exact validated package back to the workspace and deliver it."""
from pathlib import Path,PurePosixPath
import hashlib,tarfile,json,shutil,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'AssetStore/FarmNature'
BUILD=ROOT/'output/FarmNature_1.0.0_Preparation'
REPORTS=BUILD/'Reports'
RELEASE=OUT/'Release'
assert (REPORTS/'prepare-success.txt').exists(),'Unity preparation has not succeeded'
assert (REPORTS/'import-success.txt').exists(),'Clean import has not succeeded'
assert 'Errors: 0' in (REPORTS/'Validation.txt').read_text(),'Unity validation has errors'
original=BUILD/'SourceBackup/FarmNature/Demo/Scenes/Demo_FarmNature_Showcase.unity'
current=ROOT/'Assets/FarmNature/Demo/Scenes/Demo_FarmNature_Showcase.unity'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
package=REPORTS/'FarmNature_1.0.0.unitypackage'
with tarfile.open(package,'r:gz') as archive:
 members={m.name:m for m in archive.getmembers()}
 entries=[]
 for name,m in members.items():
  if not name.endswith('/pathname'):continue
  pathname=archive.extractfile(m).read().decode().rstrip('\0').strip()
  posix=PurePosixPath(pathname)
  assert not posix.is_absolute() and '..' not in posix.parts
  assert pathname=='Assets/FarmNature' or pathname.startswith('Assets/FarmNature/')
  target=ROOT.joinpath(*posix.parts)
  assert target.resolve().is_relative_to((ROOT/'Assets/FarmNature').resolve())
  prefix=name[:-len('pathname')]
  entries.append((pathname,target,prefix))
 staged_scene=archive.extractfile(members[next(prefix+'asset' for path,target,prefix in entries if path.endswith('/Demo_FarmNature_Showcase.unity'))]).read()
 assert current.read_bytes() in [original.read_bytes(),staged_scene], 'Source scene changed during preparation; preserve user changes before synchronization'
 for pathname,target,prefix in entries:
  if prefix+'asset' in members:
   target.parent.mkdir(parents=True,exist_ok=True)
   target.write_bytes(archive.extractfile(members[prefix+'asset']).read())
  else:target.mkdir(parents=True,exist_ok=True)
  if prefix+'asset.meta' in members:
   Path(str(target)+'.meta').write_bytes(archive.extractfile(members[prefix+'asset.meta']).read())
RELEASE.mkdir(exist_ok=True)
shutil.copy2(package,RELEASE/package.name)
for filename in ['Validation.txt','Unity_Prefab_Audit.csv','Scene_Dependencies.txt','AssetStore_Validator.txt','CleanImport_Overview.png']:
 if (REPORTS/filename).exists():shutil.copy2(REPORTS/filename,RELEASE/filename)
(RELEASE/'package-paths.txt').write_text('\n'.join(sorted(x[0] for x in entries))+'\n',encoding='utf8')
proof={'version':'1.0.0','unity':'6000.3.10f1','urp':'17.3.0','clean_import':True,'prefabs':88,'triangles_min':60,'triangles_max':6514,'triangles_total':118908,'scene_cameras':1,'external_assets_dependencies':0,'package_bytes':package.stat().st_size,'package_sha256':sha(package),'package_paths':len(entries),'delivery':'Release/'+package.name,'official_validator_report':'Release/AssetStore_Validator.txt','scope':'Preparation, clean import, static asset validation and rendered demo. No target-platform player build or gameplay collision test.'}
(OUT/'RELEASE_VERIFICATION.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
(RELEASE/'SHA256.txt').write_text(sha(package)+'  '+package.name+'\n')
subprocess.run(['python',str(OUT/'audit_package.py')],cwd=ROOT,check=True,capture_output=True)
subprocess.run(['python',str(OUT/'write_metadata.py')],cwd=ROOT,check=True,capture_output=True)
with zipfile.ZipFile(OUT/'FarmNature_Store_Texts.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in [OUT/'PACKAGE_METADATA.md',OUT/'PUBLISHER_NOTES.md',OUT/'PACKAGE_AUDIT.json',OUT/'MODEL_INVENTORY.csv',OUT/'metadata-fields.json',OUT/'RELEASE_VERIFICATION.json',*list((OUT/'Copy_Fields').glob('*'))]:z.write(p,p.relative_to(OUT))
print('Synchronized',len(entries),'package paths. Export:',RELEASE/package.name,'bytes:',package.stat().st_size)
