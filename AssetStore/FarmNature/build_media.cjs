/* Code-native SVG layouts. Original Unity PNGs are embedded unchanged.
   npm install --prefix .media-tools @resvg/resvg-js sharp
   node build_media.cjs
*/
const fs=require('fs'), path=require('path');
const {Resvg}=require('./.media-tools/node_modules/@resvg/resvg-js');
const sharp=require('./.media-tools/node_modules/sharp');
const ROOT=__dirname, SRC=path.join(ROOT,'Draft'), OUT=path.join(ROOT,'Media'), SVG=path.join(OUT,'Editable'), UP=path.join(OUT,'Upload');
for(const p of [OUT,SVG,UP])fs.mkdirSync(p,{recursive:true});
const C={dark:'#203D32',cream:'#FFF9EB',red:'#ED7047',muted:'#C8D9CC',gold:'#F5C85D',ink:'#294137'};
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;');
const rect=(x,y,w,h,fill)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}"/>`;
const text=(x,y,s,size,fill=C.cream,weight=700,extra='')=>`<text x="${x}" y="${y}" font-family="Arial" font-size="${size}" font-weight="${weight}" fill="${fill}" ${extra}>${esc(s)}</text>`;
const headline=(x,y,s,size,fill=C.cream,extra='')=>`<text x="${x}" y="${y}" font-family="Impact" font-size="${size}" fill="${fill}" ${extra}>${esc(s)}</text>`;
const pic=(file,x,y,w,h)=>`<image x="${x}" y="${y}" width="${w}" height="${h}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,${fs.readFileSync(path.join(SRC,file)).toString('base64')}"/>`;
const badge=(size=1)=>`<g transform="scale(${size})"><path d="M0 0H158L0 158Z" fill="${C.red}"/>${text(18,72,'3D',42,'#FFFFFF',700,'transform="rotate(-45 48 55)"')}</g>`;
const defs=`<defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="#E2EDF1"/><stop offset="1" stop-color="#AECFE6"/></linearGradient><linearGradient id="iconbg" x1="0" y1="0" x2="0.25" y2="1"><stop stop-color="#D6F1FF"/><stop offset="1" stop-color="#7EC4ED"/></linearGradient><filter id="shadow" x="-20%" y="-50%" width="150%" height="200%"><feDropShadow dx="0" dy="9" stdDeviation="9" flood-color="#17332A" flood-opacity=".16"/></filter></defs>`;
const poly=(points,fill,extra='')=>`<polygon points="${points}" fill="${fill}" ${extra}/>`;
const pill=(x,y,w,label,fill=C.dark,ink=C.cream)=>`<rect x="${x}" y="${y}" width="${w}" height="44" rx="22" fill="${fill}"/>${text(x+20,y+29,label,18,ink,700,'letter-spacing="1.6"')}`;
function titlePlate(x,y,w,title,small,color=C.red){return `<g filter="url(#shadow)">${poly(`${x},${y} ${x+w-35},${y} ${x+w},${y+35} ${x+w},${y+136} ${x},${y+136}`,C.dark)}${poly(`${x},${y} ${x+12},${y} ${x+12},${y+136} ${x},${y+136}`,color)}${headline(x+32,y+64,title,48)}${text(x+34,y+107,small,22,C.cream,400)}</g>`;}
const wrap=(w,h,body)=>`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${defs}${body}</svg>`;
const manifest=[];
async function save(name,w,h,body,source,role,small){
 const svg=wrap(w,h,body); fs.writeFileSync(path.join(SVG,name+'.svg'),svg);
 const png=new Resvg(svg,{font:{fontFiles:['C:/Windows/Fonts/arial.ttf','C:/Windows/Fonts/arialbd.ttf','C:/Windows/Fonts/impact.ttf'],loadSystemFonts:false}}).render().asPng();
 fs.writeFileSync(path.join(OUT,name+'.png'),png);
 const tw=small?small[0]:w,th=small?small[1]:h;
 const ext=name.startsWith('01_')?'png':'jpg';
 const target=path.join(UP,name+'.'+ext);
 let pipe=sharp(png).resize(tw,th).removeAlpha();
 await (ext==='jpg'?pipe.jpeg({quality:93,chromaSubsampling:'4:4:4'}):pipe.png()).toFile(target);
 manifest.push({file:path.relative(OUT,target).replaceAll('\\','/'),width:tw,height:th,master:name+'.png',editable:'Editable/'+name+'.svg',source,role,status:'composed; reviewed at export size and contact sheet'});
}
const rows=[
 ['Beauty_01_Overall.png','Hero','A WORLD OF FARM NATURE','Crops, trees, flowers and landscape pieces','Build a bright countryside scene.','SCENE OVERVIEW'],
 ['Beauty_02_1_Beds.png','Beds','GARDEN BEDS & SUPPORTS','Raised beds, soil rows, stakes and a trellis','Shape your vegetable garden.','BEDS / 6 PREFABS'],
 ['Beauty_02_2_Crops.png','Crops','CROPS & GROWTH STAGES','Seven crops in three stages, plus wheat field tiles','Swap stage prefabs as your crops grow.','CROPS / 24 PREFABS'],
 ['Beauty_02_3_Trees.png','Trees','TREES & ORCHARDS','Oak, birch, pine, willow and orchard trees','From fresh green to autumn gold.','TREES / 9 PREFABS'],
 ['Beauty_02_4_Plants.png','Plants','FLOWERS & FOLIAGE','Flowers, shrubs, hedges and ground vegetation','Add color from the ground up.','FOLIAGE COLLECTION'],
 ['Beauty_02_5_WaterRocks.png','WaterRocks','WATER, ROCKS & BRIDGES','Ponds, stream pieces, stones and wooden crossings','Shape a waterside landscape.','LANDSCAPE COLLECTION'],
 ['Beauty_02_6_Modules.png','Modules','PATHS & GROUND MODULES','Ground tiles, paths, borders and connection pieces','Combine individual pieces into a scene.','MODULAR LANDSCAPE'],
 ['Beauty_03_1_Garden.png','Garden','THE VEGETABLE GARDEN','Raised beds, climbing plants and a winding path','A small scene with room to grow.','SCENE STUDY / 01'],
 ['Beauty_03_2_Field.png','Field','THE HARVEST FIELD','Wheat, corn and sunflowers in one sunny setting','Explore the crop stages side by side.','SCENE STUDY / 02'],
 ['Beauty_03_3_Orchard.png','Orchard','THE APPLE ORCHARD','Fruit trees, blossom and a soft carpet of grass','Create a quiet corner of the farm.','SCENE STUDY / 03'],
 ['Beauty_03_4_PondBridge.png','PondBridge','THE POND & BRIDGE','Water, willow, reeds and a wooden crossing','Connect the scene with a waterside path.','SCENE STUDY / 04'],
 ['Beauty_03_5_ForestEdge.png','ForestEdge','THE FOREST EDGE','Mixed trees, rocks, fallen wood and undergrowth','Build a natural boundary for your farm.','SCENE STUDY / 05'],
 ['Beauty_03_6_FlowerPath.png','FlowerPath','THE FLOWER PATH','A curved path with hedges, flowers and greenery','Give every route a little character.','SCENE STUDY / 06'],
];
async function main(){
 const illustratedIcon=path.join(OUT,'IllustratedIcon/Generated_Original.png');
 if(fs.existsSync(illustratedIcon)){
  const bitmap=`<image x="0" y="0" width="1024" height="1024" href="data:image/png;base64,${fs.readFileSync(illustratedIcon).toString('base64')}"/>`;
  await save('01_Icon',1024,1024,bitmap,'IllustratedIcon/Generated_Original.png','AI-assisted illustrated marketing icon; blue sky and diagonal 3D corner',[160,160]);
 }else{
  await save('01_Icon',1024,1024,rect(0,0,1024,1024,'url(#iconbg)')+pic('_main/Icon_alpha.png',62,62,900,900)+badge(1.5),'Draft/_main/Icon_alpha.png','Blue sky store icon with flush diagonal 3D ribbon; exact Unity model',[160,160]);
 }
 const card=rect(0,0,1260,840,'url(#sky)')+pic('_main/Overall_alpha.png',-90,12,1440,555)
  +poly('0,558 1040,558 1090,606 1260,606 1260,840 0,840',C.dark)
  +poly('0,536 762,536 787,561 0,561',C.gold)
  +headline(50,710,'FARM NATURE',160)
  +poly('50,742 1040,742 1017,804 50,804',C.red)+text(74,785,'CROPS, TREES & LANDSCAPE',34,'#FFFFFF')
  +poly('1040,558 1260,558 1260,668 1150,668',C.gold)+text(1134,601,'88',41,C.dark)+text(1134,634,'MODELS',18,C.dark)+badge(1.05);
 await save('02_Card',1260,840,card,'Draft/_main/Overall_alpha.png','Search card: custom stepped lockup and flush corner ribbon',[420,280]);
 const cover=rect(0,0,1950,1300,'url(#sky)')+pic('_main/Overall_alpha.png',20,20,1910,975)
  +poly('0,995 1600,995 1660,1055 1950,1055 1950,1300 0,1300',C.dark)
  +poly('0,977 920,977 944,1001 0,1001',C.gold)
  +text(72,1043,'LOW POLY ENVIRONMENT COLLECTION',23,C.muted,700,'letter-spacing="4"')
  +headline(65,1196,'FARM NATURE',192)
  +poly('72,1223 1130,1223 1100,1278 72,1278',C.red)+text(95,1260,'CROPS, TREES & MODULAR LANDSCAPE',28,'#FFFFFF')
  +poly('1600,995 1950,995 1950,1200 1805,1200',C.gold)+headline(1800,1083,'88',75,C.dark)+text(1803,1120,'MODELS',23,C.dark)
  +text(1470,1261,'BUILD YOUR COUNTRYSIDE',20,C.cream,700)+badge(1.5);
 await save('03_Cover',1950,1300,cover,'Draft/_main/Overall_alpha.png','Cover: layered evergreen, apricot and golden stepped plaques');
 await save('04_Social',1200,630,rect(0,0,1200,630,'url(#sky)')+pic('_main/Overall_alpha.png',25,10,1150,610),'Draft/_main/Overall_alpha.png','Clean social preview');
 for(let i=0;i<rows.length;i++){
  const [src,slug,title,desc,sub,tag]=rows[i];
  let body;
  if(i===0){
   body=pic(src,0,0,1920,1080)
    +pill(60,44,244,'FARM NATURE')
    +poly('0,900 1030,900 1064,934 1064,1080 0,1080',C.dark)
    +poly('0,884 500,884 522,906 0,906',C.gold)
    +headline(55,991,'BUILD YOUR COUNTRYSIDE',64)+text(58,1043,desc,26)
    +pill(1515,990,345,'88 MODELS / LOW POLY',C.red,'#FFFFFF');
  }else if(i===2||i===6){
   const key=i===2?'Crops':'Modules';
   body=rect(0,0,1920,1080,'#F4ECD8')+pic('_parts02/Island_'+key+'.png',580,70,1300,940)
    +poly('0,0 530,0 610,80 610,1080 0,1080',C.dark)
    +pill(54,54,240,'FARM NATURE',C.cream,C.dark)
    +text(56,187,i===2?'GROW / HARVEST / REPEAT':'CONNECT / SHAPE / BUILD',17,C.gold,700,'letter-spacing="1.5"')
    +headline(50,293,i===2?'CROPS &':'PATHS &',88)
    +headline(50,393,i===2?'GROWTH':'GROUND',88)
    +headline(50,483,i===2?'STAGES':'MODULES',88)
    +rect(56,533,80,6,C.red)
    +text(56,600,i===2?'7 crops. 3 growth stages.':'Ground, paths and borders.',27,C.cream,400)
    +text(56,644,i===2?'Plus 3 wheat field tiles.':'Build from individual pieces.',25,C.muted,400)
    +poly('0,845 485,845 535,895 535,964 0,964',C.red)
    +headline(55,920,i===2?'24 CROP PREFABS':'MODULAR KIT',46)
    +text(56,1025,i===2?'STAGE SWAPS / NO GROWTH SYSTEM':'MESH-BASED LANDSCAPE PIECES',17,C.muted);
  }else if(i<7){
   const words={1:['GARDEN BEDS','Raised beds, soil rows, stakes and a trellis.'],3:['TREES & ORCHARDS','Oak, birch, pine, willow and orchard trees.'],4:['FLOWERS & FOLIAGE','Flowers, shrubs, hedges and ground vegetation.'],5:['PONDS, ROCKS & BRIDGES','Water pieces, stones and wooden crossings.']};
   const [head,detail]=words[i];
   body=pic(src,0,0,1920,1080)
    +pill(60,44,244,'FARM NATURE')
    +pill(1480,44,380,tag,C.cream,C.dark)
    +poly('60,879 440,879 465,904 60,904',C.red)
    +titlePlate(60,903,Math.min(1120,head.length*27+80),head,detail)
    +text(1845,1025,String(i).padStart(2,'0'),34,C.dark,700,'text-anchor="end"');
  }else{
   const sceneTitles=['VEGETABLE GARDEN','HARVEST FIELD','APPLE ORCHARD','POND & BRIDGE','FOREST EDGE','FLOWER PATH'];
   const label=sceneTitles[i-7], sceneNum=String(i-6).padStart(2,'0'), right=(i===8||i===10||i===12);
   const width=label.length*26+90,x=right?1860-width:60;
   body=pic(src,0,0,1920,1080)
    +pill(60,44,244,'FARM NATURE')
    +pill(1518,44,342,'SCENE STUDY / '+sceneNum,C.cream,C.dark)
    +poly(`${x},886 ${x+208},886 ${x+229},907 ${x},907`,C.gold)
    +titlePlate(x,906,width,label,'LOW POLY / SCENE STUDY',C.gold)
    +text(right?60:1860,1020,sub,22,C.dark,400,right?'':'text-anchor="end"');
  }
  const usedSource=i===2?'_parts02/Island_Crops.png':i===6?'_parts02/Island_Modules.png':src;
  await save(String(i+5).padStart(2,'0')+'_'+slug,1920,1080,body,'Draft/'+usedSource,'Gallery: '+title);
 }
 fs.writeFileSync(path.join(OUT,'media-manifest.json'),JSON.stringify({date:'2026-11-13',revision:2,style:C,base_standard:14,delivered:17,deviation:'Three related layout families; 1 hero, 6 categories, 6 scene studies. Crops and Modules use original detailed Unity part renders. Technical evidence remains separate and pending.',model_fbx_files:88,individual_prefabs:88,images:manifest},null,2));
 const cards=manifest.map(m=>`<figure><a href="${m.master}"><img src="${m.file}" loading="lazy"></a><figcaption>${m.master} &middot; ${m.width} &times; ${m.height}</figcaption></figure>`).join('');
 fs.writeFileSync(path.join(OUT,'index.html'),`<!doctype html><html lang="en"><meta charset="utf-8"><title>Farm Nature / Media v2</title><style>body{margin:40px;background:#fff9eb;color:#203d32;font:16px Arial}h1{font-size:44px;margin-bottom:8px}p{color:#486252}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:24px}figure{margin:0;background:#fff;padding:12px;border-top:4px solid #ed7047}img{width:100%;height:auto}figcaption{padding:12px 0;font-size:14px}a{color:inherit}</style><h1>FARM NATURE / v2</h1><p>Evergreen / apricot / golden cream. 4 key images + 13 gallery images.</p><p>Three related layout families. Flush diagonal 3D ribbons. Bright icon. <a href="Concepts/Icon_imagegen_bright_1024.png">Generated icon variant</a>.</p><div class="grid">${cards}</div></html>`);
 console.log('Built '+manifest.length+' layouts in '+OUT);
}
main().catch(e=>{console.error(e);process.exit(1)});
