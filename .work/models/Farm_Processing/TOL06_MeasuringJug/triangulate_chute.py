from pathlib import Path
p=Path('.work/models/Farm_Processing/TOL06_MeasuringJug/build_measuring_jug.py');s=p.read_text();needle="    for nm,fs,_ in P.comp: print('COMP',nm,'tris',sum(len(f.verts)-2 for f in fs))"
s=s.replace(needle,"""    # Explicit triangles keep the nonplanar chute surfaces identical in render and FBX.
    comps=[]
    for nm,fs,ground in P.comp:
        result=bmesh.ops.triangulate(P.bm,faces=fs,quad_method='BEAUTY',ngon_method='BEAUTY')
        comps.append((nm,list(result['faces']),ground))
    P.comp=comps
"""+needle);p.write_text(s)
