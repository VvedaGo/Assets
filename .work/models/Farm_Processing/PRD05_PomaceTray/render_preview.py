import os,sys
sys.argv=[sys.argv[0],'--','export']
exec(compile(open(os.path.join(os.path.dirname(__file__),'build_pomace_tray.py'),encoding='utf-8').read(),'build_pomace_tray.py','exec'))
