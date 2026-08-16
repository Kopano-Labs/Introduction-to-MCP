#!/usr/bin/env python3
"""Collect provenance-first metadata for the OyaAIProd public repository corpus.

The collector records GitHub-observable facts and conservative classifications.
It intentionally leaves technical-intelligence conclusions for source review.
"""
from __future__ import annotations
import argparse, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path
from typing import Any
API='https://api.github.com'
SAFE_PR_TITLE='Add SafeSkill security badge'
SAFE_TOPICS={'mcp-server','model-context-protocol','agent-skills','claude-skill','claude-code-skill','claude-code','openclaw','mcp-tools'}

class GitHub:
    def __init__(self, token: str|None): self.token=token
    def get(self, path_or_url: str)->Any:
        url=path_or_url if path_or_url.startswith('http') else API+path_or_url
        headers={'Accept':'application/vnd.github+json','User-Agent':'Kopano-AI-Frontier-Map/1.0','X-GitHub-Api-Version':'2022-11-28'}
        if self.token: headers['Authorization']=f'Bearer {self.token}'
        req=urllib.request.Request(url,headers=headers)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req,timeout=45) as resp: return json.load(resp)
            except urllib.error.HTTPError as exc:
                if exc.code in (403,429) and attempt<3:
                    time.sleep(max(int(exc.headers.get('Retry-After','10')),2)); continue
                raise
    def paginate(self,path:str,per_page:int=100,max_pages:int=100)->list[dict]:
        out=[]; sep='&' if '?' in path else '?'
        for page in range(1,max_pages+1):
            chunk=self.get(f'{path}{sep}per_page={per_page}&page={page}')
            if not isinstance(chunk,list) or not chunk: break
            out.extend(chunk)
            if len(chunk)<per_page: break
        return out

def parse_score(body:str|None)->float|None:
    if not body:return None
    m=re.search(r'Overall Score\*\*\s*\|\s*\*\*(\d+(?:\.\d+)?)/100',body) or re.search(r'SafeSkill[^0-9]*(\d+(?:\.\d+)?)/100',body)
    return float(m.group(1)) if m else None

def collect_safeskill_prs(gh:GitHub,author:str)->dict[str,list[dict]]:
    query=urllib.parse.quote(f'author:{author} is:pr "{SAFE_PR_TITLE}"')
    by_target={}
    for page in range(1,11):
        data=gh.get(f'/search/issues?q={query}&sort=created&order=asc&per_page=100&page={page}')
        items=data.get('items',[])
        if not items: break
        for item in items:
            repo_url=item.get('repository_url','')
            target=repo_url.split('/repos/')[-1] if '/repos/' in repo_url else ''
            if target: by_target.setdefault(target.lower(),[]).append(item)
        if len(items)<100: break
    return by_target

def candidate_signals(repo:dict)->list[str]:
    topics=set(repo.get('topics') or [])
    candidates=sorted(topics & SAFE_TOPICS)
    text=' '.join([repo.get('name') or '',repo.get('description') or '',*topics]).lower()
    if 'mcp' in text and 'mcp-server' not in candidates: candidates.append('mcp-server')
    return sorted(set(candidates))

def blank_score():
    return {'novelty':None,'technical_depth':None,'composability':None,'ecosystem_relevance':None,'kpgs_relevance':None,'current_activity':None,'total':None,'confidence_score':None}

def make_record(detail:dict,safe_prs:dict[str,list[dict]])->dict:
    parent=detail.get('parent') if detail.get('fork') else None
    upstream=parent.get('full_name') if parent else None
    pr=(safe_prs.get(upstream.lower(),[]) or [None])[0] if upstream else None
    if detail.get('fork') and pr: classification='safeskill_fork'
    elif detail.get('fork'): classification='other_fork'
    elif (detail.get('name') or '').startswith('oya-agent-'): classification='oya_agent_generated'
    else: classification='unresolved'
    lic=(parent or detail).get('license') or {}; owner=(parent or {}).get('owner') or {}
    evidence=[{'kind':'oya_repository','url':detail.get('html_url'),'note':'GitHub repository metadata snapshot'}]
    if parent: evidence.append({'kind':'upstream_repository','url':parent.get('html_url'),'note':'GitHub native parent relationship'})
    if pr: evidence.append({'kind':'safeskill_pr','url':pr.get('html_url'),'note':'SafeSkill badge PR authored by OyaAIProd'})
    return {
      'provenance':{'oya_repo':detail.get('full_name'),'oya_repo_id':detail.get('id'),'oya_created_at':detail.get('created_at'),'classification':classification,'upstream_repo':upstream,'upstream_owner':owner.get('login') if parent else None,'upstream_owner_type':owner.get('type') if parent else None,'upstream_repo_id':parent.get('id') if parent else None,'original_repo_created_at':parent.get('created_at') if parent else None,'upstream_commit_sha':None},
      'discovery':{'signal':'unknown','candidate_signals':candidate_signals(parent or detail),'evidence':'candidate_signals are inferred from current public metadata; historical SafeSkill discovery source is not asserted','discovered_at':detail.get('created_at')},
      'safeskill':{'scan_branch':None,'scan_score':parse_score(pr.get('body')) if pr else None,'scan_grade':None,'findings':{},'pr_url':pr.get('html_url') if pr else None,'pr_number':pr.get('number') if pr else None,'pr_created_at':pr.get('created_at') if pr else None,'maintainer_response':'unknown'},
      'technical_intelligence':{'problem':None,'architecture':None,'protocols':[],'dependencies':[],'integrations':[],'agent_pattern':None,'security_pattern':None,'novel_mechanism':None},
      'capability_surface':{'filesystem':None,'network':None,'secrets':None,'database':None,'browser':None,'process_execution':None,'repository_mutation':None,'cloud_access':None,'authentication':None,'external_apis':[],'prompt_injection':None,'taint_flow':None},
      'reuse_governance':{'mode':'research_only','license':lic.get('name'),'spdx':lic.get('spdx_id'),'reusable_code':None,'attribution_required':None,'architecture_only':None,'restrictions':'No reuse decision made by automated collection.','provenance_url':parent.get('html_url') if parent else detail.get('html_url'),'source_commit':None},
      'frontier_score':blank_score(),
      'convergence':{'target_systems':[],'reusable_primitive':None,'integration_pattern':None,'gaps':None,'decision':'STUDY'},
      'evidence':evidence}

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument('--owner',default='OyaAIProd'); p.add_argument('--output',default='data/ai-frontier-map/oya-corpus.jsonl'); p.add_argument('--limit',type=int,default=0)
    a=p.parse_args(); gh=GitHub(os.getenv('GITHUB_TOKEN'))
    repos=gh.paginate(f'/users/{a.owner}/repos?sort=created&direction=asc')
    if a.limit: repos=repos[:a.limit]
    safe_prs=collect_safeskill_prs(gh,a.owner); records=[]
    for i,repo in enumerate(repos,1):
        detail=gh.get(f"/repos/{repo['full_name']}"); records.append(make_record(detail,safe_prs)); print(f"[{i}/{len(repos)}] {repo['full_name']}",file=sys.stderr)
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',encoding='utf-8') as f:
        for r in records:f.write(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n')
    print(f'Wrote {len(records)} records to {out}'); return 0
if __name__=='__main__': raise SystemExit(main())
