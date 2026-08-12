#!/usr/bin/env python3
"""Standard-library invariant validator for AI Frontier Map JSONL records."""
from __future__ import annotations
import argparse,json
from pathlib import Path
CLASSIFICATIONS={'safeskill_fork','other_fork','detached_fork','oya_authored','oya_agent_generated','unresolved'}
DECISIONS={'ADOPT','ADAPT','STUDY','MONITOR','REJECT'}
REUSE_MODES={'code_reuse','architectural_reuse','research_only'}
SIGNALS={'mcp-server','model-context-protocol','agent-skills','claude-skill','claude-code','openclaw','curated-list','npm','smithery','unknown'}
WEIGHTS={'novelty':.20,'technical_depth':.20,'composability':.20,'ecosystem_relevance':.15,'kpgs_relevance':.15,'current_activity':.10}
def validate(r:dict,n:int)->list[str]:
    e=[]; pfx=f'line {n}: '
    for k in ('provenance','discovery','safeskill','technical_intelligence','capability_surface','reuse_governance','frontier_score','convergence','evidence'):
        if k not in r:e.append(pfx+f'missing top-level field {k}')
    p=r.get('provenance',{}); cls=p.get('classification')
    if cls not in CLASSIFICATIONS:e.append(pfx+f'invalid classification: {cls!r}')
    if cls in {'safeskill_fork','other_fork','detached_fork'} and not p.get('upstream_repo'):e.append(pfx+f'{cls} requires upstream_repo')
    s=r.get('safeskill',{})
    if cls=='safeskill_fork' and not(s.get('scan_branch') or s.get('pr_url')):e.append(pfx+'safeskill_fork requires scan_branch or pr_url evidence')
    d=r.get('discovery',{})
    if d.get('signal') not in SIGNALS:e.append(pfx+f"invalid discovery signal: {d.get('signal')!r}")
    g=r.get('reuse_governance',{}); mode=g.get('mode')
    if mode not in REUSE_MODES:e.append(pfx+f'invalid reuse mode: {mode!r}')
    if mode=='code_reuse':
        if not(g.get('spdx') or g.get('license')):e.append(pfx+'code_reuse requires an explicit licence')
        if not g.get('source_commit'):e.append(pfx+'code_reuse requires source_commit')
        if not g.get('provenance_url'):e.append(pfx+'code_reuse requires provenance_url')
    if r.get('convergence',{}).get('decision') not in DECISIONS:e.append(pfx+'invalid convergence decision')
    score=r.get('frontier_score',{}); vals={k:score.get(k) for k in WEIGHTS}; present=[v is not None for v in vals.values()]
    if any(present) and not all(present):e.append(pfx+'frontier score must be fully scored or fully unscored')
    if all(present):
        for k,v in vals.items():
            if not isinstance(v,(int,float)) or not 0<=v<=5:e.append(pfx+f'{k} must be 0..5')
        expected=round(sum(vals[k]*WEIGHTS[k] for k in WEIGHTS)/5*100,2); total=score.get('total')
        if total is None or abs(float(total)-expected)>.02:e.append(pfx+f'frontier total {total!r} != weighted total {expected}')
    c=score.get('confidence_score')
    if c is not None and not 0<=c<=100:e.append(pfx+'confidence_score must be 0..100')
    ev=r.get('evidence',[])
    if not isinstance(ev,list) or not ev:e.append(pfx+'at least one evidence receipt is required')
    else:
        for x in ev:
            if not x.get('kind') or not x.get('url'):e.append(pfx+'every evidence receipt requires kind + url')
    return e
def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('paths',nargs='+');a=ap.parse_args();errs=[];count=0
    for raw in a.paths:
        path=Path(raw)
        with path.open(encoding='utf-8') as f:
            for n,line in enumerate(f,1):
                if not line.strip():continue
                count+=1
                try:r=json.loads(line)
                except json.JSONDecodeError as exc:errs.append(f'{path}:{n}: invalid JSON: {exc}');continue
                errs.extend(f'{path}:{x}' for x in validate(r,n))
    if errs:print('\n'.join(errs));print(f'FAILED: {len(errs)} invariant error(s)');return 1
    print(f'PASS: {count} provenance record(s) satisfy AI Frontier Map invariants');return 0
if __name__=='__main__':raise SystemExit(main())
