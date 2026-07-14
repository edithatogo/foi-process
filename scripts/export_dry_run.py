#!/usr/bin/env python3
from pathlib import Path
import shlex, yaml
ROOT=Path(__file__).resolve().parents[1]
data=yaml.safe_load((ROOT/'repo-exports/export-map.yaml').read_text())
for item in data['exports']:
    body=ROOT/item['issue_body']; title=body.read_text().splitlines()[0].removeprefix('# ')
    print(f"\n[{item['repo']}] branch={item['branch']} conductor={item['conductor_root']}")
    print(' ',shlex.join(['gh','issue','create','--repo',item['repo'],'--title',title,'--body-file',item['issue_body']]))
    for artefact in item['artefacts']: print('  review/promote:',artefact)
