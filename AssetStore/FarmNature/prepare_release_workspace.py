from pathlib import Path
import shutil,json,subprocess,os
ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'output/FarmNature_1.0.0_Preparation'
STAGE=BUILD/'Authoring'
REPORTS=BUILD/'Reports'
for p in [STAGE/'Assets/Editor',STAGE/'Packages',STAGE/'ProjectSettings',REPORTS]:p.mkdir(parents=True,exist_ok=True)
source=ROOT/'Assets/FarmNature'
if not (BUILD/'SourceBackup/FarmNature').exists():
 shutil.copytree(source,BUILD/'SourceBackup/FarmNature')
 shutil.copy2(ROOT/'Assets/FarmNature.meta',BUILD/'SourceBackup/FarmNature.meta')
shutil.copytree(source,STAGE/'Assets/FarmNature',dirs_exist_ok=True)
shutil.copy2(ROOT/'Assets/FarmNature.meta',STAGE/'Assets/FarmNature.meta')
shutil.copy2(ROOT/'AssetStore/FarmNature/ReleaseTools/ReleasePreparation.cs',STAGE/'Assets/Editor/ReleasePreparation.cs')
shutil.copy2(ROOT/'ProjectSettings/ProjectVersion.txt',STAGE/'ProjectSettings/ProjectVersion.txt')
deps={'com.unity.render-pipelines.universal':'17.3.0','com.unity.modules.physics':'1.0.0','com.unity.modules.audio':'1.0.0','com.unity.modules.imageconversion':'1.0.0','com.unity.modules.imgui':'1.0.0','com.unity.modules.jsonserialize':'1.0.0'}
(STAGE/'Packages/manifest.json').write_text(json.dumps({'dependencies':deps},indent=2))
unity=Path('C:/Program Files/Unity/Hub/Editor/6000.3.10f1/Editor/Unity.exe')
cmd=[str(unity),'-batchmode','-projectPath',str(STAGE),'-executeMethod','ReleasePreparation.Prepare','-logFile',str(REPORTS/'Unity_Prepare.log')]
p=subprocess.Popen(cmd,creationflags=subprocess.CREATE_NO_WINDOW)
(REPORTS/'prepare-process.json').write_text(json.dumps({'pid':p.pid,'project':str(STAGE),'command':cmd},indent=2))
print('Unity batch process:',p.pid,'Project:',STAGE)
