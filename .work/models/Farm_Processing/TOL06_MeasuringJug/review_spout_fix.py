from pathlib import Path
p=Path('.work/models/Farm_Processing/TOL06_MeasuringJug/build_measuring_jug.py')
s=p.read_text();a=s.index('    # One closed section:',s.index('def jug():'));b=s.index('    for z in (.255,.105):',a)
s=s[:a]+'''    # Closed 13-vertex shell: original 12-gon plus a centre vertex at -X.
    # The shoulder vertices sit +/-40 degrees from -X; three vertices follow
    # each straight V side. Every rim and inner ring shares that exact outline.
    prof=[(0,.094),(.005,.100),(.036,.100),(.036,.096),(.195,.08382),
          (.284,.077),(.284,.081),(.296,.081),(.297,.077),(.291,.071),
          (.195,.07754),(.012,.090)]
    angles=[15,45,75,105,140,165,180,195,220,255,285,315,345]
    rings=[]
    for z,apo in prof:
        r=apo*1.3/math.cos(math.pi/12)
        ring=[]
        for deg in angles:
            ang=math.radians(deg); x,y=r*math.cos(ang),r*math.sin(ang); zz=z
            if z>.28 and 140<=deg<=220:
                # Keep +/-40 degree shoulders on the circular body outline;
                # place intermediate points on straight lines to the raised tip.
                side_y=r*math.sin(math.radians(40))
                tip_x=-(apo*1.3+.050)
                f=abs(y)/side_y
                x=tip_x*(1-f)-r*math.cos(math.radians(40))*f
                zz+=.010*(1-f)
            ring.append(Vector((x,y,zz)))
        rings.append(ring)
    P.loft('vessel',rings,lambda j,k:(15,15,15,CREAM,CREAM,METAL_D,METAL,METAL_L,METAL,CREAM_B,CREAM_B)[j],15,CREAM_D,ground=True)
    print('SPOUT shoulders +/-40deg, extension .050m, tip rise .010m, blend z .195m')
'''+s[b:]
s=s.replace("'view':(-0.12,-1.0,0.48)","'view':(-0.35,-1.0,0.57)")
s=s.replace('assert 200<=total<=450','assert 200<=total<=500').replace('BUDGET OK 200-450','BUDGET OK 200-500 (lead revised spout budget)')
p.write_text(s)
