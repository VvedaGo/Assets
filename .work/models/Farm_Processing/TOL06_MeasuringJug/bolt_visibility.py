from pathlib import Path
p=Path('.work/models/Farm_Processing/TOL06_MeasuringJug/build_measuring_jug.py');s=p.read_text()
s=s.replace("sweep(P,'red_hex_bolt',(x+.004,0,z),(x+.014,0,z),ngon(.010,6,math.pi/2),\n              [(0,1,0),(1,.82,0)],RED,RED_D,RED,ref=(0,1,0))", "sweep(P,'red_hex_bolt',(x+.004,-.027,z),(x+.004,.027,z),ngon(.008,6,math.pi/2),\n              [(0,1,0),(1,1,0)],RED_D,RED,RED,ref=(1,0,0))")
p.write_text(s)
