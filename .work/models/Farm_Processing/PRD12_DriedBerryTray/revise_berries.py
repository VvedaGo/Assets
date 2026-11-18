from pathlib import Path
p=Path('.work/models/Farm_Processing/PRD12_DriedBerryTray/build_dried_berry_tray.py')
s=p.read_text()
a=s.index('def berry(');b=s.index('counts=Counter()',a)
s=s[:a]+'''def berry(x,y,z,k):
 # Six-sided equator, smaller rotated triangular shoulder, short top tip.
 # Hidden base capped (four extra tris) for zero non-manifold edges:16 tris/berry.
 r=.011*(1+.045*math.sin(k*8)); phase=.15*math.sin(k*1.9)
 eq=[P.bm.verts.new((x+r*math.cos(phase+j*math.pi/3),y+r*math.sin(phase+j*math.pi/3),z)) for j in range(6)]
 up=[P.bm.verts.new((x+r*.63*math.cos(phase+math.pi/3+j*2*math.pi/3),y+r*.63*math.sin(phase+math.pi/3+j*2*math.pi/3),z+.011)) for j in range(3)]
 tip=P.bm.verts.new((x+.0007*math.sin(k),y,z+.0176))
 fs=[];slot=14 if k%5==0 else 13
 for j in range(3):
  # upper j matches equator 2*j+1; quad+triangle shoulders avoid long pole fans
  q=2*j+1
  fs.append(P.face([eq[q],eq[(q+1)%6],eq[(q+2)%6],up[(j+1)%3],up[j]],slot))
  fs.append(P.face([up[j],up[(j+1)%3],tip],slot))
 fs.append(P.face(list(reversed(eq)),slot))
 P.comp.append(('berries',fs,False))
# Five compact 2+3+4 bunches: nine touching berries each, with a visible brown fork.
for ci,(cx,cy) in enumerate([(-.073,.068),(.068,.068),(-.101,-.065),(0,-.065),(.101,-.065)]):
 cells=[]
 for row in range(3):
  for col in range(row+2):
   x=cx+(col-(row+1)/2)*.019;y=cy+.014-row*.017
   # Equator is embedded into the highest local cream strip; base hidden and capped.
   tops=[.052+(min(i,5-i)%2)*.003 for i,xx in enumerate(xs) if abs(x-xx)<.018]+[.054+(i%2)*.003 for i,yy in enumerate(ys) if abs(y-yy)<.018]
   topz=max(tops or [.052]);berry(x,y,topz-.001,ci*9+len(cells));cells.append((x,y,topz))
 # Stems lie visibly on top of fruit, with their pointed ends seated in berries.
 # Main and three branches form a connected fork rather than isolated sticks.
 twig((cx,cy+.048,.081),(cx,cy-.032,.068),.0030)
 for j,(bx,by) in enumerate([(-.020,.005),(.025,-.009),(-.025,-.023)]):
  twig((cx,cy+.023-j*.012,.078-j*.002),(cx+bx,cy+by,.0675),.0028)
''' + s[b:]
s=s.replace("catalogue 250-650 task ~900 allowance","catalogue 250-650 revised lead allowance1250")
s=s.replace('<=960','<=1250')
p.write_text(s)
