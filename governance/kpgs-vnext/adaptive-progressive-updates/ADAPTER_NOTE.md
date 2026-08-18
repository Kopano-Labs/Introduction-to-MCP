# Adapter Note

Downstream PWA/runtime implementations should pin this package by repository commit and implement the wire contract locally. They should not import the Python module into browser code or move canonical business state into a service worker.

The browser/PWA lane owns resilient interaction and local witness state. The Hub/.NET/security boundary owns privileged authority and canonical external synchronization.
