from pathlib import Path
p=Path(r'C:\Users\Sergv\AppData\Local\Temp\FarmProcessing_check\PRD15')
assert p.resolve()==p
for f in p.glob('*.png'): f.unlink()
p.rmdir()
