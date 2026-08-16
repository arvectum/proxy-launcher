# APL-SEC-004 — Atomic configuration writes

Status: **IMPLEMENTED**

Settings and `no_proxy.txt` now use a same-directory atomic writer:

1. create a unique temporary file in the target directory;
2. write the complete payload;
3. flush Python buffers;
4. `fsync` the file;
5. atomically replace the target with `os.replace`;
6. `fsync` the parent directory where supported;
7. remove any leftover temporary file on failure.

Before replacing a valid active settings file, its validated serialized form is atomically stored as `proxy_settings.lastgood.json` (except plaintext legacy Windows credentials, which are never duplicated).

Injected replace failures preserve the previous primary configuration.
