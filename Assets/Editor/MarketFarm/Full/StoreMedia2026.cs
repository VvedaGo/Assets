using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Object = UnityEngine.Object;

namespace MarketFarm.Editor {
[InitializeOnLoad]
public static class StoreMedia2026 {
 const string Base = "Assets/Scenes/StoreMedia2026";
 const string Scene = Base + "/FarmMarket_Store.unity";
 const string Out = "AssetStore/Full/Media2026";
 static double next;
 static StoreMedia2026() { EditorApplication.update += Poll; }
 static void Poll() {
  if(EditorApplication.timeSinceStartup<next || EditorApplication.isCompiling || EditorApplication.isUpdating) return;
  next=EditorApplication.timeSinceStartup+2;
  if(!File.Exists("media-command.txt")) return;
  var cmd=File.ReadAllText("media-command.txt").Trim(); File.Delete("media-command.txt");
  try { if(cmd=="build") Build(); else if(cmd=="preview") Render(false); else if(cmd=="final") Render(true); else if(cmd=="inspect") Inspect(); else if(cmd=="editor") EditorView(); else if(cmd=="refine") Refine();
   File.WriteAllText("media-status.txt","OK "+cmd+" "+DateTime.Now);
  } catch(Exception e) { Debug.LogException(e); File.WriteAllText("media-status.txt",e.ToString()); }
 }
 static Material Mat(string name, Color color) {
  var path=Base+"/"+name+".mat"; var m=AssetDatabase.LoadAssetAtPath<Material>(path);
  if(!m){m=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(m,path);}
  m.color=color; m.SetFloat("_Smoothness",0); EditorUtility.SetDirty(m); return m;
 }
 static Color Palette(string hex) {ColorUtility.TryParseHtmlString(hex,out var c);return c.linear;}
 static void ApplyPalette(bool hero) {
  // Calibrated against captured pixels under this scene's warm lighting.
  Mat("Neutral",hero?new Color(.6485f,.722f,.642f):new Color(.795f,.834f,.806f));
  Mat("Sand",new Color(.795f,.758f,.641f));
 }
 static GameObject Spawn(string name, Transform parent, Vector3 p, float yaw=0) {
  var guid=AssetDatabase.FindAssets(name+" t:Prefab",new[]{"Assets/FarmMarketFull/Art/Prefabs"}).First(g=>Path.GetFileNameWithoutExtension(AssetDatabase.GUIDToAssetPath(g))==name);
  var go=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(AssetDatabase.GUIDToAssetPath(guid)),parent);
  go.transform.localPosition=p;go.transform.localRotation=Quaternion.Euler(0,yaw,0);return go;
 }
 static Bounds BoundsOf(GameObject go) {
  var rr=go.GetComponentsInChildren<MeshRenderer>(true).Where(r=>!r.name.EndsWith("_LOD1")&&!r.name.EndsWith("_LOD2")).ToArray();
  var b=rr[0].bounds;foreach(var r in rr.Skip(1))b.Encapsulate(r.bounds);return b;
 }
 static Transform Group(string name,Vector3 p) {var t=new GameObject(name).transform;t.position=p;return t;}
 static void Floor(Transform t, float size=70) {
  var p=GameObject.CreatePrimitive(PrimitiveType.Plane);p.name="Neutral studio floor (presentation only)";p.transform.SetParent(t,false);p.transform.localPosition=Vector3.down*.025f;p.transform.localScale=Vector3.one*size/10;
  p.GetComponent<Renderer>().sharedMaterial=Mat("Neutral",new Color(.835f,.835f,.85f));
 }
 static void Build() {
  Directory.CreateDirectory(Base);Directory.CreateDirectory(Out+"/Raw");
  var scene=EditorSceneManager.OpenScene("Assets/FarmMarketFull/Demo/Scenes/Demo_MarketSquare.unity",OpenSceneMode.Single);
  EditorSceneManager.SaveScene(scene,Scene);
  foreach(var v in Object.FindObjectsByType<Volume>(FindObjectsSortMode.None))v.enabled=false;
  RenderSettings.fog=false;RenderSettings.ambientMode=AmbientMode.Trilight;
  RenderSettings.ambientSkyColor=new Color(.65f,.68f,.74f);RenderSettings.ambientEquatorColor=new Color(.55f,.57f,.61f);RenderSettings.ambientGroundColor=new Color(.32f,.34f,.39f);
  var sun=RenderSettings.sun;sun.transform.rotation=Quaternion.Euler(48,-35,0);sun.color=new Color(1,.96f,.89f);sun.intensity=1.25f;sun.shadowStrength=.65f;sun.shadows=LightShadows.Soft;
  foreach(var l in Object.FindObjectsByType<Light>(FindObjectsSortMode.None))if(l!=sun)l.enabled=false;
  foreach(var r in Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))if(r.name=="Studio_Floor")r.sharedMaterial=Mat("Neutral",new Color(.835f,.835f,.85f));
  var hero=Group("Promo_Hero",new Vector3(600,0,0));Floor(hero,5000);
  Spawn("FMS_Comp_VegetableRow",hero,new Vector3(-2.6f,0,0),-8);
  var fruit=Spawn("FMS_Comp_FruitRow",hero,new Vector3(2.1f,0,.3f),5);
  foreach(var t in fruit.GetComponentsInChildren<Transform>())if(t.name=="FMS_Stall_Umbrella")t.gameObject.SetActive(false);
  var bakery=GameObject.Find("Zone_Bakery");
  if(bakery){var b=Object.Instantiate(bakery,hero);b.name="Rear_Bakery";b.transform.localPosition=new Vector3(.1f,0,3.6f);b.transform.localRotation=Quaternion.identity;foreach(var t in b.GetComponentsInChildren<Transform>())if(t.name.Contains("Umbrella"))t.gameObject.SetActive(false);}
  else Spawn("FMS_Comp_DairyFoodCorner",hero,new Vector3(0,0,3.8f));
  Spawn("FMS_Stall_Umbrella_Green",hero,new Vector3(3.9f,0,3.1f),10);
  var cart=Spawn("FMS_Stall_Cart_Empty",hero,new Vector3(2.7f,0,-1.9f),-30);
  var cartCrate=Spawn("FMS_Crate_Base",cart.transform,new Vector3(0,.5f,0));Spawn("FMS_Crate_Fill_Apple",cartCrate.transform,Vector3.up*.18f);
  var frontCrate=Spawn("FMS_Crate_Base",hero,new Vector3(-.9f,0,-1.9f),-8);Spawn("FMS_Crate_Fill_Cabbage",frontCrate.transform,Vector3.up*.18f);
  var sideCrate=Spawn("FMS_Crate_Base",hero,new Vector3(-.25f,0,-2.2f),8);Spawn("FMS_Crate_Fill_Potato",sideCrate.transform,Vector3.up*.18f);
  // Quiet sand patch: actual Unity geometry, separately labelled presentation scenery.
  var patch=GameObject.CreatePrimitive(PrimitiveType.Cylinder);patch.name="Sand display base (presentation only)";patch.transform.SetParent(hero,false);patch.transform.localPosition=new Vector3(0,-.07f,1);patch.transform.localScale=new Vector3(12,.06f,10);
  patch.GetComponent<Renderer>().sharedMaterial=Mat("Sand",new Color(.73f,.65f,.5f));
  BuildCategory("Produce",new[]{"Veg","Fruit"},new Vector3(700,0,0));
  BuildCategory("Containers",new[]{"Crate"},new Vector3(800,0,0));
  BuildCategory("Decor",new[]{"Deco"},new Vector3(900,0,0));
  BuildCategory("Food",new[]{"Food"},new Vector3(1000,0,0));
  BuildTechnical();
  foreach(var g in Object.FindObjectsByType<LODGroup>(FindObjectsSortMode.None))if(g.transform.root.name!="Technical_LOD")g.ForceLOD(0);
  var cam=Object.FindObjectsByType<Camera>(FindObjectsSortMode.None).First(c=>c.CompareTag("MainCamera"));
  ApplyPalette(true);
  foreach(var c in Object.FindObjectsByType<Camera>(FindObjectsSortMode.None))c.enabled=false;
  cam.enabled=true;cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=new Color(.89f,.89f,.905f);cam.GetUniversalAdditionalCameraData().renderPostProcessing=false;
  cam.transform.position=new Vector3(608,7.5f,-13);cam.transform.LookAt(new Vector3(600,1,1));cam.fieldOfView=38;
  EditorSceneManager.SaveScene(scene);AssetDatabase.SaveAssets();Inspect();Render(false);
 }
 static void BuildCategory(string name,string[] cats,Vector3 origin) {
  var t=Group("Category_"+name,origin);Floor(t);
  var paths=AssetDatabase.FindAssets("t:Prefab",new[]{"Assets/FarmMarketFull/Art/Prefabs/Single"}).Select(AssetDatabase.GUIDToAssetPath).Where(p=>cats.Any(c=>Path.GetFileName(p).StartsWith("FMS_"+c+"_"))).OrderBy(p=>p).ToArray();
  int cols=8;float cell=1.5f;
  for(int i=0;i<paths.Length;i++) {
   var go=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(paths[i]),t);
   var b=BoundsOf(go);float s=1.15f/Mathf.Max(b.size.x,b.size.y,b.size.z);go.transform.localScale=Vector3.one*s;b=BoundsOf(go);
   var pos=origin+new Vector3((i%cols-(Math.Min(cols,paths.Length-i/cols*cols)-1)*.5f)*cell,0,((paths.Length-1)/cols*.5f-i/cols)*cell);
   go.transform.position+=new Vector3(pos.x-b.center.x,-b.min.y,pos.z-b.center.z);
  }
 }
 static void BuildTechnical() {
  var t=Group("Technical_LOD",new Vector3(1100,0,0));Floor(t);
  var report=new List<string>();
  for(int i=0;i<3;i++) {
   var go=Spawn("FMS_Crate_Basket_Fill_Berries",t,new Vector3((i-1)*3.4f,0,0));go.transform.localScale=Vector3.one*24;
   foreach(var lod in go.GetComponentsInChildren<LODGroup>()) {lod.ForceLOD(i);var ll=lod.GetLODs();long tris=0;foreach(var r in ll[i].renderers){var f=r.GetComponent<MeshFilter>();if(f&&f.sharedMesh)tris+=f.sharedMesh.triangles.Length/3;} report.Add("LOD"+i+": "+tris+" tris");}
   var wire=Spawn("FMS_Crate_Basket_Fill_Berries",t,new Vector3((i-1)*3.4f,0,-3.4f));wire.transform.localScale=Vector3.one*24;
   foreach(var group in wire.GetComponentsInChildren<LODGroup>()) {
    var lods=group.GetLODs();var visible=lods[i].renderers;
    foreach(var r in wire.GetComponentsInChildren<Renderer>(true))r.enabled=false;
    foreach(var r in visible) {var f=r.GetComponent<MeshFilter>();if(!f||!f.sharedMesh)continue;var src=f.sharedMesh;var tri=src.triangles;var idx=new List<int>();for(int k=0;k<tri.Length;k+=3)idx.AddRange(new[]{tri[k],tri[k+1],tri[k+1],tri[k+2],tri[k+2],tri[k]});
     var mesh=new Mesh();mesh.vertices=src.vertices;mesh.SetIndices(idx.ToArray(),MeshTopology.Lines,0);mesh.RecalculateBounds();mesh=SaveMesh(mesh,"Wire_"+i+"_"+r.name);
     var line=new GameObject("Actual mesh edges");line.transform.SetParent(r.transform,false);line.AddComponent<MeshFilter>().sharedMesh=mesh;line.AddComponent<MeshRenderer>().sharedMaterial=LineMat("Wire",new Color(.13f,.18f,.23f));
    }
    group.enabled=false;
   }
  }
  File.WriteAllLines(Out+"/lod-measured.txt",report);
  var ct=Group("Technical_Colliders",new Vector3(1200,0,0));Floor(ct);
  string[] names={"FMS_Stall_Table_Medium_Canopy","FMS_Crate_Base","FMS_Stall_Cart_Empty"};
  for(int i=0;i<names.Length;i++) {
   var go=Spawn(names[i],ct,new Vector3((i-1)*3,0,0));
   foreach(var box in go.GetComponentsInChildren<BoxCollider>(true)) {
    var v=new Vector3[8];for(int k=0;k<8;k++)v[k]=box.center+Vector3.Scale(box.size*.505f,new Vector3((k&1)==0?-1:1,(k&2)==0?-1:1,(k&4)==0?-1:1));
    int[] ix={0,1,2,3,4,5,6,7,0,2,1,3,4,6,5,7,0,4,1,5,2,6,3,7};var m=new Mesh();m.vertices=v;m.SetIndices(ix,MeshTopology.Lines,0);m.RecalculateBounds();m=SaveMesh(m,"Collider_"+i+"_"+box.name);
    var line=new GameObject("Actual BoxCollider bounds");line.transform.SetParent(box.transform,false);line.AddComponent<MeshFilter>().sharedMesh=m;line.AddComponent<MeshRenderer>().sharedMaterial=LineMat("Collider",new Color(.05f,.5f,.28f));
   }
  }
 }
 static Mesh SaveMesh(Mesh m,string name){m.name=name;string path=Base+"/"+name+".asset";var old=AssetDatabase.LoadAssetAtPath<Mesh>(path);if(old){EditorUtility.CopySerialized(m,old);Object.DestroyImmediate(m);return old;}else AssetDatabase.CreateAsset(m,path);return m;}
 static Material LineMat(string name,Color c){var p=Base+"/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(p);if(!m){m=new Material(Shader.Find("Universal Render Pipeline/Unlit"));AssetDatabase.CreateAsset(m,p);}m.color=c;return m;}
 class Shot {public string name;public Vector3 p,t; public float f;public int w=1920,h=1080;public Shot(string n,Vector3 p,Vector3 t,float f){name=n;this.p=p;this.t=t;this.f=f;}}
 static List<Shot> Shots() {return new List<Shot>{
  new Shot("01_Hero",new Vector3(604.5f,5.2f,-11),new Vector3(600,1,1.4f),32),
  new Shot("02_Collection",new Vector3(200,13.4f,-9.6f),new Vector3(200,0,-.25f),40),
  new Shot("03_Produce_Detail",new Vector3(597.1f,1.9f,-3.2f),new Vector3(597.4f,.85f,0),36),
  new Shot("03b_Fruit_Detail",new Vector3(601.5f,1.65f,-2.6f),new Vector3(602,.8f,.3f),35),
  new Shot("04_Stalls_Furniture",new Vector3(257,8.5f,-12.5f),new Vector3(260,.8f,-.4f),39),
  new Shot("05_Produce_Collection",new Vector3(700,8,-6),new Vector3(700,0,0),47),
  new Shot("06_Containers",new Vector3(800,8,-6),new Vector3(800,0,0),47),
  new Shot("07_Food_Dairy",new Vector3(439.4f,2.45f,-3.6f),new Vector3(440.1f,.5f,-.35f),42),
  new Shot("08_Food_Collection",new Vector3(1000,8,-6),new Vector3(1000,0,0),43),
  new Shot("09_Decor",new Vector3(900,8,-6),new Vector3(900,0,0),43),
  new Shot("10_Compositions",new Vector3(319,10,-12),new Vector3(320,.4f,.4f),39),
  new Shot("11_Demo_Layout",new Vector3(-9,19,-9),new Vector3(.4f,0,.4f),38),
  new Shot("12_LOD",new Vector3(1100,8,-11),new Vector3(1100,.5f,-1.5f),57),
  new Shot("13_Colliders",new Vector3(1203,5,-11),new Vector3(1200,.7f,0),52),
  new Shot("Icon",new Vector3(379.65f,1.15f,-1.55f),new Vector3(380,.2f,-.12f),30){w=1024,h=1024},
  new Shot("Cover",new Vector3(605.5f,6,-12),new Vector3(600,1.2f,1.5f),32){w=1950,h=1300},
  new Shot("Card",new Vector3(603.5f,4.6f,-8.5f),new Vector3(600,.7f,1.5f),35){w=1260,h=530}
 };}
 static void Render(bool final) {
  if(EditorSceneManager.GetActiveScene().path!=Scene)EditorSceneManager.OpenScene(Scene);
  var cam=Object.FindObjectsByType<Camera>(FindObjectsSortMode.None).First(c=>c.CompareTag("MainCamera"));
  string dir=Out+(final?"/Raw":"/Preview");Directory.CreateDirectory(dir);
  var old=QualitySettings.renderPipeline;
  QualitySettings.renderPipeline=MarketHeroShots.HeroPipeline((UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline,Base+"/RenderSettings");
  try {
   foreach(var s in Shots()) {
    bool isHero=s.name=="01_Hero"||s.name=="Card"||s.name=="Cover"||s.name=="03_Produce_Detail"||s.name=="03b_Fruit_Detail";
    ApplyPalette(isHero);cam.backgroundColor=Palette(isHero?"#B8C8B0":"#DEE5D8");
    cam.transform.position=s.p;cam.transform.LookAt(s.t);cam.fieldOfView=s.f;cam.aspect=(float)s.w/s.h;
    int w=final?s.w:s.w/3,h=final?s.h:s.h/3;
    MarketHeroShots.Capture(cam,null,64,64,1);MarketHeroShots.Capture(cam,dir+"/"+s.name+".png",w*(final?2:1),h*(final?2:1),final?2:1);
   }
  } finally {QualitySettings.renderPipeline=old;}
  var hero=Shots()[0];cam.transform.position=hero.p;cam.transform.LookAt(hero.t);cam.fieldOfView=hero.f;cam.aspect=16f/9;
  ApplyPalette(true);AssetDatabase.SaveAssets();
  EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene());
 }
 static void Inspect() {
  Directory.CreateDirectory(Out);
  var missing=new List<string>();int renderers=0;foreach(var r in Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None)) {renderers++;foreach(var m in r.sharedMaterials)if(!m||!m.shader||m.shader.name.Contains("Error"))missing.Add(r.name);}
  File.WriteAllText(Out+"/scene-check.txt","Scene: "+EditorSceneManager.GetActiveScene().path+"\nMesh renderers: "+renderers+"\nMissing/error materials: "+missing.Count+"\n"+string.Join("\n",missing));
  var rows=new List<string>{"Prefab\tCategory\tLOD0 triangles\tLOD1 triangles\tLOD2 triangles\tBox colliders"};
  foreach(var guid in AssetDatabase.FindAssets("t:Prefab",new[]{"Assets/FarmMarketFull/Art/Prefabs/Single"})) {
   var path=AssetDatabase.GUIDToAssetPath(guid);var go=AssetDatabase.LoadAssetAtPath<GameObject>(path);var counts=new long[3];
   foreach(var group in go.GetComponentsInChildren<LODGroup>(true)) {var lods=group.GetLODs();for(int i=0;i<Math.Min(3,lods.Length);i++)foreach(var rr in lods[i].renderers)if(rr){var mf=rr.GetComponent<MeshFilter>();if(mf&&mf.sharedMesh)counts[i]+=mf.sharedMesh.triangles.Length/3;}}
   if(counts[0]==0)foreach(var mf in go.GetComponentsInChildren<MeshFilter>(true))if(mf.sharedMesh)counts[0]+=mf.sharedMesh.triangles.Length/3;
   rows.Add(go.name+"\t"+Path.GetFileName(Path.GetDirectoryName(path))+"\t"+string.Join("\t",counts)+"\t"+go.GetComponentsInChildren<BoxCollider>(true).Length);
  }
  File.WriteAllLines(Out+"/prefab-audit.tsv",rows);
 }
 static void EditorView() {
  var guid=AssetDatabase.FindAssets("FMS_Stall_Table_Medium_Canopy t:Prefab",new[]{"Assets/FarmMarketFull/Art/Prefabs/Single"})[0];
  Selection.activeObject=AssetDatabase.LoadAssetAtPath<GameObject>(AssetDatabase.GUIDToAssetPath(guid));EditorGUIUtility.PingObject(Selection.activeObject);
  var view=SceneView.lastActiveSceneView;if(view){view.LookAt(new Vector3(600,1,1),Quaternion.Euler(25,-25,0),12);view.Repaint();}
 }
 static void Refine() {
  var hero=GameObject.Find("Promo_Hero");
  foreach(var t in hero.GetComponentsInChildren<Transform>())if(t.name.StartsWith("FMS_Crate_Fill_") && t.parent.name=="FMS_Crate_Base")t.localPosition=Vector3.up*.18f;
  foreach(var g in Object.FindObjectsByType<LODGroup>(FindObjectsSortMode.None))if(g.transform.root.name!="Technical_LOD")g.ForceLOD(0);
  EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene());Inspect();Render(true);
 }
}
}
