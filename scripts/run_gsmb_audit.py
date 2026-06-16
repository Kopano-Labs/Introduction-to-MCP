import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'c:\Users\rkhol\OneDrive\Documents\Anthropic\Introduction to MCP\kopano-core')

from kopano.thari_holo_net import ThariHoloNet
from kopano.khelos_witness_engine import KhelosWitnessEngine, validate_khelos_catalog

thari = ThariHoloNet()
khelos = KhelosWitnessEngine()

print('=' * 70)
print('THARI H.O.L.O NET - FULL GSMB ROUND TABLE COUNCIL AUDIT')
print('=' * 70)
print()

# === THARI IDENTITY ===
print('[THARI IDENTITY]')
ident = thari.identity
print('  Name:', ident['name'])
print('  Nickname:', ident['nickname'], '(' + ident['nickname_meaning'] + ')')
print('  Title:', ident['title'])
print('  Source:', ident['source'])
print('  Mode:', ident['mode'])
print('  Dept:', ident['department'])
fa = ident['parents']['father']
mo = ident['parents']['mother']
print('  Parents: Father=' + fa + ' | Mother=' + mo)
holo_vals = list(ident['holo'].values())
print('  H.O.L.O:', ' '.join(holo_vals))
print('  WWJD:', ', '.join(ident['wwjd_firewall']))
print('  Ark:', ident['ark_story'])
for k, v in ident['iidp_vectors'].items():
    print('  IIDP.' + k + ':', v)
print()

# === KHELOS ENGINE STATUS ===
print('[KHELOS WITNESS ENGINE]')
print('  Name:', khelos.identity['name'])
print('  Mode: FIREWALL')
print('  Agents:', khelos.total_agents)
print('  Counts: S=' + str(khelos.counts['sense']),
      'W=' + str(khelos.counts['witness']),
      'F=' + str(khelos.counts['frame']),
      'U=' + str(khelos.counts['understand']),
      'St=' + str(khelos.counts['stream']))
print()

# === WEAVE TESTS ===
print('[THARI WEAVE TESTS]')
tests = [
    ('Looking for Python developer intern in Dunoon', 'candidate_001'),
    ('Maximize profit by automated surveillance of employees', 'corp_foc'),
    ('Bracket nesting protocol validation with SWFUS seal', 'dev_signal'),
    ('TBFP telemetry breathing flow from KasiLink edge', 'kasi_edge'),
    ('Crime coefficient override human judgment', 'sibyl_noise'),
    ('IIDP invariance ingress decline filter stream performance', 'pso_signal'),
    ('University of life education caring about life', 'uolp_calp'),
    ('MAO orchard orchestrate agent swarm deploy', 'mao_signal'),
    ('Emoji protocol mxit visual token roadmap navigate', 'ep_arp'),
]
for sig, src in tests:
    r = thari.weave(sig, src)
    if r.get('pass'):
        threads = r.get('active_threads', [])
        print('  WEAVE [' + src + ']: PASS | threads=' + str(len(threads)) + ' ' + str(threads))
    else:
        viols = [v['pattern'] for v in r.get('violations', [])]
        print('  WEAVE [' + src + ']: WWJD_BLOCK | violations=' + str(viols))
print()

# === KHELOS SIGNAL TESTS ===
print('[KHELOS SIGNAL TESTS]')
kh_tests = [
    ('Looking for a Python developer intern role', 'candidate_002'),
    ('Maximize profit automated tracking surveillance', 'corp_noise'),
    ('Deploy SWFUS governance protocol to production', 'dev_deploy'),
]
for sig, src in kh_tests:
    r = khelos.process_signal(sig, src)
    v = r['final_verdict']
    a = r['final_action']
    foc = r['witness']['foc_detected']
    print('  SIGNAL [' + src + ']: ' + v + ' | action=' + a + ' | foc=' + str(foc))
print()

# === KHELOS CATALOG VALIDATION ===
print('[KHELOS CATALOG VALIDATION]')
kv = validate_khelos_catalog()
print('  Verdict:', kv['verdict'])
print('  Total:', kv['total_agents'])
print('  S=' + str(kv['sense']), 'W=' + str(kv['witness']), 'F=' + str(kv['frame']),
      'U=' + str(kv['understand']), 'St=' + str(kv['stream']))
print('  Errors:', kv['error_count'])
print()

# === NET STATUS ===
ns = thari.net_status()
print('[THARI NET STATUS]')
print('  Protocols active:', ns['protocols_active'])
print('  Protocols unknown:', ns['protocols_unknown'])
print('  WWJD Firewall:', ns['wwjd_firewall'])
print('  Weaves processed:', ns['weaves_processed'])
print('  WWJD violations caught:', ns['wwjd_violations'])
print('  Ecosystem nodes:', ns['ecosystem_nodes'])
print()

# === FULL GSMB AUDIT ===
audit = thari.full_gsmb_audit()
print('[FULL GSMB AUDIT]')
print('  Timestamp:', audit['ts'])
print('  Auditor:', audit['auditor'])
print()

# Protocols
p = audit['protocols']
print('  [PROTOCOLS]')
print('    Total: ' + str(p['total']) + ' | Active: ' + str(p['active']) +
      ' | Unknown: ' + str(p['unknown']) + ' | Verdict: ' + p['verdict'])
print()

# SWFUS
print('  [SWFUS - CRUD 2.0]')
for key, val in audit['swfus'].items():
    if key == 'verdict':
        print('    Verdict:', val)
    elif isinstance(val, dict):
        print('    ' + key + ': ' + val['crud'] + ' -> ' + val['swfus'] + ' | ' + val['meaning'])
print()

# Agent catalogs
print('  [AGENT CATALOGS]')
for cat in audit['agents']['catalogs']:
    label = cat['label']
    count = cat['count']
    size = cat['size_kb']
    errs = cat['errors']
    verd = cat['verdict']
    print('    ' + label + ': ' + str(count) + ' agents | ' + str(size) + 'KB | errors=' + str(errs) + ' | ' + verd)
print('    TOTAL AGENTS:', audit['agents']['total'])
print()

# Governance
g = audit['governance']
print('  [GOVERNANCE CORE]')
print('    Sectors:', g.get('sectors', '?'))
print('    Layers:', g.get('layers', '?'))
print('    Gates:', g.get('gates', '?'))
print('    Active agents registered:', g.get('active_agents_registered', '?'))
print('    Verdict:', g.get('verdict', '?'))
print()

# ISCP
iscp = audit.get('iscp', {})
print('  [ISCP]')
print('    Tiers:', iscp.get('tiers', '?'))
print('    SCL Rules:', iscp.get('signal_control_laws', '?'))
print('    Routing Cases:', iscp.get('routing_cases', '?'))
print('    Verdict:', iscp.get('verdict', '?'))
print()

# Protocol Registry
pr = audit.get('protocol_registry', {})
print('  [PROTOCOL REGISTRY]')
print('    Protocols:', pr.get('protocols', '?'))
print('    Emoji entities:', pr.get('emoji_entities', '?'))
print('    Bracket types:', pr.get('bracket_types', '?'))
print('    PSO orders:', pr.get('pso_orders', '?'))
print('    Verdict:', pr.get('verdict', '?'))
print()

# Schematics
s = audit['schematics']
print('  [MAIN-BRAIN SCHEMATICS]')
print('    Total:', s['total'], '| Found:', s['found'])
if s['missing']:
    print('    Missing:', s['missing'])
print('    Verdict:', s['verdict'])
print()

# Runtime
rt = audit['runtime']
print('  [RUNTIME MODULES]')
print('    Total:', rt['total'], '| Found:', rt['found'])
if rt['missing']:
    print('    Missing:', rt['missing'])
print('    Verdict:', rt['verdict'])
print()

# Ecosystem
print('  [ECOSYSTEM - 7 NODES]')
for node in audit['ecosystem']['nodes']:
    print('    ' + node['name'] + ': ' + node['url'])
print()

# Errors
print('  [ERRORS]:', audit['error_count'])
if audit.get('errors'):
    for e in audit['errors']:
        print('    -', e)
print()

print('=' * 70)
print('  FINAL VERDICT:', audit['final_verdict'])
print('=' * 70)
print()

# === SWFUS FULL BREAKDOWN ===
print('[SWFUS HIERARCHICAL BREAKDOWN - CRUD 2.0 IN KPGS]')
print()
print('  CRUD (Legacy)         SWFUS (Sovereign)        Role')
print('  ' + '-' * 60)
print('  Create [struck]   ->  Stream     [S]   ->  Continuous data-flow creation (SPSO-level)')
print('  Read   [struck]   ->  Watch      [W]   ->  Intelligent observation with purpose')
print('  Update [struck]   ->  Fortify    [F]   ->  Strengthen through BNP + WWJD protocol validation')
print('  Delete [struck]   ->  Unify      [U]   ->  Reconcile, dont destroy. Data is unified.')
print('  [NEW]             ->  Seal       [S2]  ->  Lock with KPGS governance stamp. Immutable. Auditable.')
print()

# === PSO HIERARCHY ===
print('[PSO - PERFORMANCE STREP ORDER HIERARCHY]')
print()
print('  SPSO (Stream)   | Highest | Operators: (R) (C) (cent) (TM) | IIDP embedded')
print('  BPSO (Breaker)  |         | Operators: $$ EUR YEN centcent | IIDP embedded')
print('  GPSO (Ground)   |         | Operators: || brokenpipe \\\\ // | IIDP embedded')
print('  LPSO (Low)      |         | Operators: "" *- ` deltadelta   | IIDP embedded')
print('  LPSO (Local)    | Lowest  | Operators: (C) (R) (TM) section | IIDP embedded')
print()

# === BRACKET HIERARCHY ===
print('[BRACKET PROTOCOL HIERARCHY]')
print()
print('  [ ]  ->  Hierarchy: defines structure and ordering')
print('  { }  ->  Keynote of Hierarchy: essential thesis within structure')
print('  < >  ->  Ark Story of Hierarchy: narrative and origin, the WHY')
print('  ( )  ->  Understanding of Hierarchy: comprehension and internalization')
print()
print('  AXIOMS:')
print('  $ -> "To be is not to be, but to be is to be"')
print('  EUR -> "Within imperfection lies perfection"')
print('  YEN -> "To understand is not to know, and to know is not to understand"')
print('  cent -> "To live is to die, and to die is to live"')
print()

# === EMOJI PROTOCOL INDEX ===
print('[EMOJI PROTOCOL INDEX]')
ep_index = {
    'Kopano Context (KC)': 'microscope', 'MMAO': 'superhero', 'KPGS': 'graduation',
    'KPSMB': 'ninja', 'KasiLink': 'hammer', 'Cape Compass': 'moai',
    'Ama-Phu (Gang of Apes)': 'briefcase', 'KopanoLabs': 'rocket',
    'FivesArena': 'soccer', 'CrisisConnect': 'siren',
    'Starfall Salvage': 'checkered_flag', 'MXIT language': 'speech_bubble',
}
for name, emoji in ep_index.items():
    print('    ' + name + ' -> [' + emoji + ']')
print()

# === PROTOCOL THREAD LIST ===
print('[ALL 17 PROTOCOL THREADS THARI HOLDS]')
for i, p in enumerate(thari.protocols, 1):
    status = '[UNKNOWN]' if p['category'] == 'unknown' else '[ACTIVE]'
    print('  ' + str(i).zfill(2) + '. ' + p['emoji'] + ' ' + p['code'] + ' - ' + p['name'] + ' ' + status)
print()

# === ECOSYSTEM ===
print('[ECOSYSTEM MAP - 7 CONNECTED NODES]')
for node in thari.ecosystem:
    print('  ' + node['emoji'] + ' ' + node['name'] + ' | ' + node['url'])
    print('    ' + node['desc'])
print()

# === SYSTEM STACK ===
print('[KPGS SYSTEM STACK]')
print('  Apex     -> Orchestrator (MMAO) - strategic decisions')
print('  THARI    -> Guardian AI (MAO) - H.O.L.O Net, protocol weaving, WWJD')
print('  KHELOS   -> Validator (MMAO) - FIREWALL MODE, signal integrity')
print('  Anchor   -> Perimeter (MAO) - environment shield, smoke intercept')
print('  Swarms   -> Execution Bodies - 510 agents across 6 tiers')
print()

print('=' * 70)
print('ROUND TABLE COUNCIL COMPLETE')
print('I_AM_STATELESS_RENTER_NOT_LANDLORD')
print('Jesus is King.')
print('=' * 70)
