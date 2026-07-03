import sys from pathlib import Path p=Path(sys.argv[1]);f=p.open('w',encoding='utf-8') f.write('hello') f.close() 
