"""Python porting workspace for the Claw Code rewrite effort."""

__all__ = [
    'ParityAuditResult',
    'PortManifest',
    'PortRuntime',
    'QueryEnginePort',
    'RuntimeSession',
    'StoredSession',
    'TurnResult',
    'PORTED_COMMANDS',
    'PORTED_TOOLS',
    'build_command_backlog',
    'build_port_manifest',
    'build_system_init_message',
    'build_tool_backlog',
    'load_session',
    'run_parity_audit',
    'save_session',
]

_LAZY_EXPORTS = {
    'ParityAuditResult': ('parity_audit', 'ParityAuditResult'),
    'PortManifest': ('port_manifest', 'PortManifest'),
    'PortRuntime': ('runtime', 'PortRuntime'),
    'QueryEnginePort': ('query_engine', 'QueryEnginePort'),
    'RuntimeSession': ('runtime', 'RuntimeSession'),
    'StoredSession': ('session_store', 'StoredSession'),
    'TurnResult': ('query_engine', 'TurnResult'),
    'PORTED_COMMANDS': ('commands', 'PORTED_COMMANDS'),
    'PORTED_TOOLS': ('tools', 'PORTED_TOOLS'),
    'build_command_backlog': ('commands', 'build_command_backlog'),
    'build_port_manifest': ('port_manifest', 'build_port_manifest'),
    'build_system_init_message': ('system_init', 'build_system_init_message'),
    'build_tool_backlog': ('tools', 'build_tool_backlog'),
    'load_session': ('session_store', 'load_session'),
    'run_parity_audit': ('parity_audit', 'run_parity_audit'),
    'save_session': ('session_store', 'save_session'),
}


def __getattr__(name: str):
    try:
        module_name, export_name = _LAZY_EXPORTS[name]
    except KeyError as error:
        raise AttributeError(name) from error

    module = __import__(f'{__name__}.{module_name}', fromlist=[export_name])
    value = getattr(module, export_name)
    globals()[name] = value
    return value
