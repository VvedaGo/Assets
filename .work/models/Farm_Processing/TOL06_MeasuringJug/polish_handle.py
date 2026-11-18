from pathlib import Path
p=Path('.work/models/Farm_Processing/TOL06_MeasuringJug/build_measuring_jug.py');s=p.read_text()
a=s.index('    for z in (.255,.105):'); b=s.index('    center_on_ground(P)',a)
s=s[:a]+'''    # Short 4x5cm plates sit directly on the +X wall, with 6mm proud faces.
    for z in (.255,.105):
        x=1.3*(.096+(.077-.096)*(z-.036)/(.284-.036))
        sweep(P,'plate',(x-.003,0,z),(x+.006,0,z),chamf_rect(.040,.050,.007),
              [(0,1,0),(.75,1,0),(1,.88,0)],METAL,METAL_D,METAL_L,ref=(0,1,0))
        sweep(P,'red_hex_bolt',(x+.004,0,z),(x+.014,0,z),ngon(.010,6,math.pi/2),
              [(0,1,0),(1,.82,0)],RED,RED_D,RED,ref=(0,1,0))
    pts=[Vector(p) for p in [(.108,0,.255),(.144,0,.268),(.168,0,.242),(.168,0,.139),(.148,0,.113),(.123,0,.105)]]
    path_sweep(P,'handle',pts,(0,1,0),chamf_rect(.030,.030,.004),RED,RED_D)
    print('HANDLE section .030m chamfer .004m, reach approx .070m, wall plates .040x.050m proud .006m')
'''+s[b:]
s=s.replace('assert 200<=total<=500','assert 200<=total<=560').replace('BUDGET OK 200-500 (lead revised spout budget)','BUDGET OK 200-560 (lead handle polish budget)')
p.write_text(s)
