#!/usr/bin/env python3
"""Small development-oracle benchmark. Not a Rust performance claim."""
from __future__ import annotations
import json, time, tracemalloc
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import reference_pipeline as rp

def make_events(cases:int):
    events=[]
    activities=['foio:RequestSent','foio:AuthorityResponseReceived','foio:ExtensionNotified','foio:InformationReleased','foio:ClosedObserved']
    for i in range(cases):
        case=f'urn:bench:request:{i}'
        for j,a in enumerate(activities):
            logical=f'urn:bench:event:{i}:{j}'
            events.append({
                'event_id':f'{logical}:r1','logical_event_id':logical,'revision':1,'operation':'upsert',
                'case_id':case,'activity':a,'event_time':{'timestamp':f'2025-01-{j+1:02d}T00:00:00Z'},
                'position':{'sequence':i*len(activities)+j},
            })
        if i % 20 == 0: # correction for 5% of cases
            e=events[-3].copy(); e['revision']=2; e['event_id']=e['logical_event_id']+':r2'; e['event_time']={'timestamp':'2025-01-03T01:00:00Z'}; events.append(e)
    return events

def run(cases):
    events=make_events(cases); tracemalloc.start(); t=time.perf_counter(); out=rp.summary(events); elapsed=time.perf_counter()-t; current,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
    return {'cases':cases,'input_event_revisions':len(events),'materialized_events':out['active_event_count'],'seconds':round(elapsed,6),'events_per_second':round(len(events)/elapsed,1),'peak_python_bytes':peak}

def main():
    report={'warning':'Python development oracle only; not representative of Rust4PM/foi-process performance.','runs':[run(n) for n in (1000,10000)]}
    path=ROOT/'examples/generated/reference-benchmark.json'; path.write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2))
if __name__=='__main__': main()
