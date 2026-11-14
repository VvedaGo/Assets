/* Code-native SVG layouts. Original Unity PNGs are embedded unchanged.
   npm install --prefix .media-tools @resvg/resvg-js sharp
   node build_media.cjs
*/
const fs=require('fs'), path=require('path');
const {Resvg}=require('./.media-tools/node_modules/@resvg/resvg-js');
const sharp=require('./.media-tools/node_modules/sharp');
const ROOT=__dirname, SRC=path.join(ROOT,'Draft'), OUT=path.join(ROOT,'Media'), SVG=path.join(OUT,'Editable'), UP=path.join(OUT,'Upload');
for(const p of [OUT,SVG,UP])fs.mkdirSync(p,{recursive:true});
const C={dark:'#20242A',cream:'#F2E6C9',red:'#C8473B',muted:'#C5C8C7'};
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;');
const rect=(x,y,w,h,fill)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}"/>`;
const text=(x,y,s,size,fill=C.cream,weight=700,extra='')=>`<text x="${x}" y="${y}" font-family="Arial" font-size="${size}" font-weight="${weight}" fill="${fill}" ${extra}>${esc(s)}</text>`;
const pic=(file,x,y,w,h)=>`<image x="${x}" y="${y}" width="${w}" height="${h}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,${fs.readFileSync(path.join(SRC,file)).toString('base64')}"/>`;
const badge=(size=1)=>`<g transform="translate(${26*size} ${26*size}) scale(${size})"><path d="M0 0H108V48L92 64H0Z" fill="${C.red}"/>${text(19,45,'3D',40)}</g>`;
const defs=`<defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="#D9E8EF"/><stop offset="1" stop-color="#A9C7E4"/></linearGradient><radialGradient id="iconbg"><stop stop-color="#595347"/><stop offset="1" stop-color="#20242A"/></radialGradient></defs>`;
const wrap=(w,h,body)=>`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${defs}${body}</svg>`;
const manifest=[];
async function save(name,w,h,body,source,role,small){
 const svg=wrap(w,h,body); fs.writeFileSync(path.join(SVG,name+'.svg'),svg);
 const png=new Resvg(svg,{font:{fontFiles:['C:/Windows/Fonts/arial.ttf','C:/Windows/Fonts/arialbd.ttf'],loadSystemFonts:false}}).render().asPng();
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
 await save('01_Icon',1024,1024,rect(0,0,1024,1024,'url(#iconbg)')+pic('_main/Icon_alpha.png',102,102,820,820),'Draft/_main/Icon_alpha.png','Opaque store icon; actual Unity model',[160,160]);
 await save('02_Card',1260,840,rect(0,0,1260,840,'url(#sky)')+pic('_main/Overall_alpha.png',-50,8,1360,510)+rect(0,522,1260,234,C.dark)+rect(0,522,1260,7,C.red)+text(44,678,'FARM NATURE',132)+rect(0,756,1260,84,C.red)+text(46,811,'LOW POLY NATURE',40)+badge(1.4),'Draft/_main/Overall_alpha.png','Search card, separately composed',[420,280]);
 await save('03_Cover',1950,1300,rect(0,0,1950,1300,'url(#sky)')+pic('_main/Overall_alpha.png',15,24,1920,960)+rect(0,1000,1950,222,C.dark)+rect(0,1000,1950,7,C.red)+text(72,1152,'FARM NATURE',142)+text(1500,1080,'CROPS / TREES',27,C.muted)+text(1500,1125,'LANDSCAPE',27,C.muted)+rect(0,1222,1950,78,C.red)+text(72,1274,'88 MODELS  /  LOW POLY NATURE',34)+badge(1.7),'Draft/_main/Overall_alpha.png','Store cover');
 await save('04_Social',1200,630,rect(0,0,1200,630,'url(#sky)')+pic('_main/Overall_alpha.png',45,20,1110,590),'Draft/_main/Overall_alpha.png','Clean social preview');
 for(let i=0;i<rows.length;i++){
  const [src,slug,title,desc,sub,tag]=rows[i];
  const {data,info}=await sharp(path.join(SRC,src)).removeAlpha().raw().toBuffer({resolveWithObject:true});
  const rgb=offset=>'#'+Array.from(data.subarray(offset,offset+3)).map(n=>n.toString(16).padStart(2,'0')).join('');
  const sky=`<defs><linearGradient id="gallerySky" x2="0" y2="1"><stop stop-color="${rgb(0)}"/><stop offset="1" stop-color="${rgb((info.width*info.height-1)*3)}"/></linearGradient></defs>`;
  const body=sky+rect(0,0,1920,960,'url(#gallerySky)')+pic(src,0,0,1920,960)+rect(0,960,1920,120,C.dark)+rect(0,960,1920,4,C.red)+rect(0,964,12,116,C.red)+text(40,996,'FARM NATURE',20,C.muted)+text(40,1049,title,40)+text(1040,1009,desc,24)+text(1040,1046,sub,21,C.muted,400)+rect(1600,34,280,44,C.dark)+text(1616,1067,String(i+1).padStart(2,'0')+' / 13',16,C.muted)+text(1616,64,tag,17);
  await save(String(i+5).padStart(2,'0')+'_'+slug,1920,1080,body,'Draft/'+src,'Gallery: '+title);
 }
 fs.writeFileSync(path.join(OUT,'media-manifest.json'),JSON.stringify({date:'2026-11-13',style:C,base_standard:14,delivered:17,deviation:'13 gallery images retain all supplied beauty renders: 1 hero, 6 categories, 6 scene studies. Technical evidence remains separate and pending.',model_fbx_files:88,individual_prefabs:88,images:manifest},null,2));
 const cards=manifest.map(m=>`<figure><a href="${m.master}"><img src="${m.file}" loading="lazy"></a><figcaption>${m.master} В· ${m.width} Г— ${m.height}</figcaption></figure>`).join('');
 fs.writeFileSync(path.join(OUT,'index.html'),`<!doctype html><html lang="en"><meta charset="utf-8"><title>Farm Nature В· Media</title><style>body{margin:40px;background:#171b20;color:#f2e6c9;font:16px Arial}h1{font-size:44px;margin-bottom:8px}p{color:#c5c8c7}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:24px}figure{margin:0;background:#20242a;padding:12px;border-top:4px solid #c8473b}img{width:100%;height:auto}figcaption{padding:12px 0;font-size:14px}a{color:inherit}</style><h1>FARM NATURE</h1><p>Graphite / cream / terracotta В· 4 key images + 13 gallery images</p><p>Scene studies show layouts, not a promise of included composition prefabs. Wireframe, materials proof and Unity Inspector still require dedicated captures.</p><div class="grid">${cards}</div></html>`);
 console.log('Built '+manifest.length+' layouts in '+OUT);
}
main().catch(e=>{console.error(e);process.exit(1)});
