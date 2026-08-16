# APL-SEC-001 — Configuration model

Status: **IMPLEMENTED**

The runtime configuration now has an explicit governed schema (`arvectum.proxy.settings.v1`) and `config_version = 1`.

Security/validation rules:

- only known top-level and upstream keys are accepted;
- local HTTP, SOCKS5 and PAC ports must be integers in `1..65535` and must be distinct;
- PAC path is a bounded absolute local path with query/fragment, whitespace and control characters rejected;
- upstream entries are bounded to 16, hosts are host/address values rather than URLs, and port types/ranges are validated;
- future unsupported schema versions fail closed;
- missing legacy version metadata is accepted as version 0 and normalized to the current runtime model.

Malformed or structurally invalid configuration is never trusted as runtime state.
