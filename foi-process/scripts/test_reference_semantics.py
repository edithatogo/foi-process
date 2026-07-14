#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import reference_pipeline as rp

def main():
    rp.generate()
    # Canonical IDs ignore object-key ordering.
    assert rp.sid('test',{'b':2,'a':1}) == rp.sid('test',{'a':1,'b':2})
    deltas=[json.loads(x) for x in (ROOT/'examples/input/evidence-deltas.ndjson').read_text().splitlines()]
    replay=rp.Replay(); events=[]; statuses=[]
    for d in deltas:
        out,event,_=replay.apply(d); statuses.append(out['status'])
        if event: events.append(event)
    assert statuses == ['accepted']*5
    duplicate,_,_=replay.apply(deltas[-1]); assert duplicate['status']=='duplicate'
    stale=dict(deltas[3]); stale['delta_id']=rp.sid('delta', ['stale']); stale['revision']=1
    stale_out,_,_=replay.apply(stale); assert stale_out['status']=='stale'
    gap=dict(deltas[3]); gap['delta_id']=rp.sid('delta',['gap']); gap['revision']=4
    gap_out,_,_=replay.apply(gap); assert gap_out['status']=='gap_detected'
    sequence_replay=rp.Replay(); sequence_replay.apply(deltas[0])
    position_gap=dict(deltas[1]); position_gap['delta_id']=rp.sid('delta',['position-gap']); position_gap['position']=dict(position_gap['position'],sequence=3)
    position_gap_out,_,_=sequence_replay.apply(position_gap); assert position_gap_out['status']=='position_gap'
    position_regression=dict(deltas[1]); position_regression['delta_id']=rp.sid('delta',['position-regression']); position_regression['position']=dict(position_regression['position'],sequence=0)
    position_regression_out,_,_=sequence_replay.apply(position_regression); assert position_regression_out['status']=='position_regression'
    material=rp.materialize(events)
    extensions=[e for e in material if e['activity']=='foio:ExtensionNotified']
    assert len(extensions)==1 and extensions[0]['revision']==2
    summary=json.loads((ROOT/'examples/generated/dashboard-summary.json').read_text())
    assert summary['active_event_count']==4  # corrected extension is counted once
    public=json.loads((ROOT/'examples/generated/public-projection.json').read_text())
    assert public['metadata_only_event_count']==1
    closed=[e for e in public['events'] if e['activity']=='foio:ClosedObserved'][0]
    assert closed['evidence']==[]
    ocel=json.loads((ROOT/'examples/generated/ocel-projection.json').read_text())
    assert len([e for e in ocel['events'] if e['event_type']=='foio:ExtensionNotified'])==1
    print('ok: deterministic ids, revision/position replay, correction, privacy, summary, OCEL materialization')
if __name__=='__main__': main()
