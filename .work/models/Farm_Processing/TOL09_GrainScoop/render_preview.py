# Run headless; rebuild and render/export from the same source.
from pathlib import Path
import sys
sys.argv=[sys.argv[0],'--','export']
exec(compile((Path(__file__).parent/'build_grain_scoop.py').read_text(),str(Path(__file__).parent/'build_grain_scoop.py'),'exec'))
