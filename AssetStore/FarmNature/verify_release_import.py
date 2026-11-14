from pathlib import Path
import json,shutil,subprocess,time
ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'output/FarmNature_1.0.0_Preparation'
DEST=BUILD/'CleanImport'
REPORTS=BUILD/'Reports'
for p in [DEST/'Assets/Editor',DEST/'Packages',DEST/'ProjectSettings']:p.mkdir(parents=True,exist_ok=True)
previous=DEST/'Assets/FarmNature'
if previous.exists():
 snapshot=BUILD/('PreviousImport_'+str(time.time_ns()))
 assert previous.resolve().is_relative_to((DEST/'Assets').resolve())
 assert snapshot.resolve().is_relative_to(BUILD.resolve())
 shutil.move(str(previous),str(snapshot))
 previous_meta=Path(str(previous)+'.meta')
 if previous_meta.exists():shutil.move(str(previous_meta),str(snapshot)+'.meta')
for marker in ['import-success.txt','import-failure.txt']:
 path=REPORTS/marker
 if path.exists():path.unlink()
shutil.copy2(ROOT/'AssetStore/FarmNature/ReleaseTools/ReleasePreparation.cs',DEST/'Assets/Editor/ReleasePreparation.cs')
shutil.copy2(ROOT/'ProjectSettings/ProjectVersion.txt',DEST/'ProjectSettings/ProjectVersion.txt')
manifest=json.loads((BUILD/'Authoring/Packages/manifest.json').read_text())
# Validator is an editor tool installed only in this isolated verification project.
shutil.copytree(ROOT/'Packages/com.unity.asset-store-tools',DEST/'Packages/com.unity.asset-store-tools',dirs_exist_ok=True)
manifest['dependencies']['com.unity.nuget.newtonsoft-json']='3.2.1'
(DEST/'Packages/manifest.json').write_text(json.dumps(manifest,indent=2))
cmd=['C:/Program Files/Unity/Hub/Editor/6000.3.10f1/Editor/Unity.exe','-batchmode','-projectPath',str(DEST),'-executeMethod','ReleasePreparation.VerifyImported','-logFile',str(REPORTS/'Unity_CleanImport.log')]
p=subprocess.Popen(cmd,creationflags=subprocess.CREATE_NO_WINDOW)
(REPORTS/'import-process.json').write_text(json.dumps({'pid':p.pid,'command':cmd},indent=2))
print('Clean import process:',p.pid)
