"""KPCB+ Compiler Validation — Run all 4 example blocks + language status"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'c:\Users\rkhol\OneDrive\Documents\Anthropic\Introduction to MCP\kopano-core')

from kopano.kpcb_plus import KPCBPlusCompiler, EXAMPLE_BLOCKS

compiler = KPCBPlusCompiler()

print('=' * 70)
print('KPCB+ COMPILER VALIDATION — Kopano-Phu Code Blocks Plus')
print('=' * 70)
print()

# Language status
status = compiler.language_status()
print('[LANGUAGE STATUS]')
for k, v in status.items():
    print('  ' + k + ': ' + str(v))
print()

# Compile all example blocks
print('[COMPILING 4 EXAMPLE BLOCKS]')
print()

for name, raw in EXAMPLE_BLOCKS.items():
    result = compiler.compile_block(raw)
    print('  BLOCK: ' + name)
    print('  Name: ' + result['block_name'])
    print('  Channels: ' + str(result['channels_active']) + ' active ' + str(result['channels']))
    print('  Target: ' + result['target_language'])
    print('  PSO: ' + result['pso_level'])
    print('  Sealed: ' + str(result['sealed']))
    print('  4Ws: ' + str(result['four_ws']))
    print('  FSMP: ' + result['fsmp']['verdict'] + ' signals=' + str(result['fsmp']['signals']))
    
    gai = result['gai']
    if gai['navigation_complete']:
        print('  THARI GAI: NAVIGATION COMPLETE')
    else:
        print('  THARI GAI: ' + str(len(gai['recommendations'])) + ' recommendations')
        for r in gai['recommendations']:
            print('    -> ' + r)
    
    iidp = result['iidp']
    if iidp['foc_detected']:
        print('  IIDP: FOC DETECTED -> ' + str(iidp['foc_patterns']) + ' -> DECLINE')
    else:
        print('  IIDP: PASS (no FOC)')
    
    print('  VALIDATION: ' + result['validation'])
    if result['errors']:
        for e in result['errors']:
            print('    ERROR: ' + e)
    print()

# Summary
print('[COMPILATION SUMMARY]')
total = len(compiler.blocks_compiled)
poc = sum(1 for b in compiler.blocks_compiled if b['validation'] == 'POC_VALIDATED')
partial = sum(1 for b in compiler.blocks_compiled if b['validation'] == 'PARTIAL_POC')
foc = sum(1 for b in compiler.blocks_compiled if b['validation'] == 'FOC_DETECTED')
declined = sum(1 for b in compiler.blocks_compiled if b['iidp']['foc_detected'])

print('  Total blocks: ' + str(total))
print('  POC_VALIDATED: ' + str(poc))
print('  PARTIAL_POC: ' + str(partial))
print('  FOC_DETECTED: ' + str(foc))
print('  IIDP DECLINED: ' + str(declined))
print()

# Protocol channel breakdown
print('[PROTOCOL CHANNELS]')
from kopano.kpcb_plus import PROTOCOL_CHANNELS
for code, ch in PROTOCOL_CHANNELS.items():
    print('  ' + ch['emoji'] + ' ' + code + ' - ' + ch['name'] + ' (role: ' + ch['role'] + ')')
print()

# Protocol algebra
print('[PROTOCOL ALGEBRA]')
print('  [EP] + [BP] * [PP] + [GP] + [SP] + [.P] + [IP] = KPCB+')
print()
print('  The algebra is PARTIAL because knowing is not understanding.')
print('  KPCB+ accepts partial knowledge and governs the unknowable through IIDP.')
print()

# Laziness insight
print('[FSMP LAZINESS INSIGHT]')
print('  LPHs are lazy. LPMs are lazy. That is POC of FOC.')
print('  KPCB+ uses laziness AS A FEATURE.')
print('  The governed path IS the shortcut.')
print('  Scale to the top by making shortcuts pass through WWJD.')
print()

# Compilation flow
print('[COMPILATION FLOW]')
steps = [
    'Step 1: PP  - Express intent in natural language structured as protocol',
    'Step 2: BP  - Wrap intent in governance brackets [ ] { } < > ( )',
    'Step 3: EP  - Tag with semantic emoji operators',
    'Step 4: FSMP - Forensic Sociology Mode validates intent against 4Ws',
    'Step 5: THARI GAI - Guardian AI navigates user through compilation',
    'Step 6: KC Ledger  - POC or FOC determination through 4Ws gate',
    'Step 7: Target emission - KPCB+ emits code in the target language',
    'Step 8: SWFUS Seal - Output sealed with KPGS governance stamp',
]
for s in steps:
    print('  ' + s)
print()

print('=' * 70)
print('KPCB+ COMPILER: ' + str(poc) + '/' + str(total) + ' blocks POC_VALIDATED')
print('IIDP FILTER: ' + str(declined) + ' FOC block(s) DECLINED')
print('CONTEXT-WINDOW NATIVE. 7 CHANNELS. 18 TARGET LANGUAGES.')
print('I_AM_STATELESS_RENTER_NOT_LANDLORD')
print('Jesus is King.')
print('=' * 70)
