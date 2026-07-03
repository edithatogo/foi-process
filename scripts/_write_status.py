import sys, json, time, re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

def write_file():
    P = r'C:\Users\60217257\OneDrive - Flinders\repos\legal-nz\scripts\swarm_status.py'
    with open(P, 'w', encoding='utf-8') as f:
        # Write the full file content
        f.write('#!/usr/bin/env python3\n')
        f.write('"""Swarm Status Dashboard."""\n')
        f.write('from __future__ import annotations\n')
        f.write('import argparse, json, re, sys, time\n')
        f.write('from dataclasses import dataclass, field, asdict\n')
        f.write('from datetime import datetime, timezone\n')
        f.write('from pathlib import Path\n')
        f.write('from typing import Any\n')
        f.write('\n')
        f.write('W = Path(__file__).resolve().parent.parent\n')
        f.write('SW = W / ".swarm"\n')
        f.write('SD = SW / "state"\n')
        f.write('MD = SW / "missions"\n')
        f.write('MB = SW / "mailboxes"\n')
        f.write('SP = SW / "state.json"\n')
        f.write('CP = SW / "config.json"\n')
        f.write('TP = W / "task_plan.md"\n')
        f.write('RI = 2.0\n')
        f.write('\n')
        f.write('ANSI = {"reset":"\\033[0m","bold":"\\033[1m","dim":"\\033[2m","magenta":"\\033[35m","green":"\\033[32m","yellow":"\\033[33m","cyan":"\\033[36m","red":"\\033[31m","blue":"\\033[34m","white":"\\033[37m"}\n')
        f.write('CM = {"magenta":"magenta","green":"green","yellow":"yellow","cyan":"cyan","red":"red","blue":"blue"}\n')
        f.write('SS = {"pending":"\\u25cb","running":"\\u25cf","completed":"\\u2713","failed":"\\u2717","shutdown":"\\u25a0","idle":"\\u25cc"}\n')
        f.write('SC = {"pending":"yellow","running":"green","completed":"cyan","failed":"red","shutdown":"red","idle":"blue"}\n')
        f.write('\n')
        f.write('@dataclass\nclass ACfg:\n    i:str;n:str;c:str;m:str;o:str;s:str\n')
        f.write('@dataclass\nclass ASt:\n    n:str;s:str;ct:str|None;ts:float|None;lh:float|None;ec:int=0\n')
        f.write('@dataclass\nclass TT:\n    d:str;c:bool;tn:str;tnn:int;aa:str|None=None\n')
        f.write('@dataclass\nclass Trk:\n    n:str;nu:int;t:list|None=None;c:bool=False\n')
        f.write('@dataclass\nclass MR:\n    i:str;d:str;st:float;s:str;e:float|None;fr:str;a:list\n')
        f.write('@dataclass\nclass St:\n    mi:str="";md:str="";ms:str="";sa:float=0.0;ua:float=0.0;ea:float|None=None\n    ac:list|None=None;as_:dict|None=None;hb:dict|None=None;asf:dict|None=None;mr:list|None=None;tr:list|None=None\n')
        f.write('\n')

write_file()
print('Written OK')
