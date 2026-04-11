"""Legacy compatibility wrapper for write_file.

The filesystem tool consolidated read/write operations into one module.
Older tests and callers still import ``orch.tools.write_file`` directly.
"""

from .filesystem import write_file

__all__ = ["write_file"]

