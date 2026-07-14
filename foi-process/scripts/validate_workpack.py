#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parents[1]
checks={
 'examples/generated/normalized-bundle.json':'normalized-bundle',
 'examples/generated/dashboard-summary.json':'dashboard-summary',
 'examples/generated/ocel-projection.json':'ocel-projection',
 'examples/generated/public-projection.json':'public-projection',
 'examples/generated/document-bundle.json':'document-bundle',
 'examples/generated/document-signal.json':'document-signal',
 'examples/generated/human-review-record.json':'human-review-record',
 'examples/generated/conformance-trace.json':'conformance-trace',
 'examples/generated/validation-finding.json':'validation-finding',
 'examples/generated/stream-checkpoint.json':'stream-checkpoint',
 'examples/generated/replay-snapshot.json':'replay-snapshot',
 'examples/generated/mining-run-manifest.json':'mining-run-manifest',
}
failed=False
for rel,name in checks.items():
    data=json.loads((ROOT/rel).read_text())
    schema=json.loads((ROOT/'schemas/portable'/f'{name}.schema.json').read_text())
    errors=sorted(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(data),key=lambda e:list(e.path))
    if errors:
        failed=True; print('FAIL',rel)
        for e in errors: print(' ',list(e.path),e.message)
    else: print('ok',rel)
# NDJSON contracts
for rel,name in [('examples/input/evidence-deltas.ndjson','evidence-delta'),('examples/input/process-events.ndjson','process-event')]:
    schema=json.loads((ROOT/'schemas/portable'/f'{name}.schema.json').read_text()); validator=Draft202012Validator(schema,format_checker=FormatChecker())
    for n,line in enumerate((ROOT/rel).read_text().splitlines(),1):
        errors=list(validator.iter_errors(json.loads(line)))
        if errors:
            failed=True; print('FAIL',rel,n,errors[0].message)
    if not failed: print('ok',rel)
if failed: sys.exit(1)
