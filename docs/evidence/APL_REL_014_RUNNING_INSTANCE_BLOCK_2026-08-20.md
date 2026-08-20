# APL-REL-014 owner-host running-instance BLOCK

The second real owner-host acceptance attempt on 2026-08-20 reached the owner-host wrapper and correctly stopped before snapshot/mutation because two processes from the exact governed Documents installation were still running.

Observed state:

- registered installer location: `%USERPROFILE%\Documents\ArvectumProxyLauncher`
- running process count: 2
- both executable paths resolved to the governed `Arvectum Proxy Launcher.exe`
- signed release set preflight had already passed
- no lifecycle snapshot or destructive lifecycle phase started in this attempt

Follow-up implemented in a separate runtime-aware wrapper:

1. validate exact installed EXE, cached repair installer, manifest, version and registration first;
2. reject any same-named foreign or path-unverifiable process before mutation;
3. record whether proxy-core and GUI were running;
4. use the product `--stop` / `--rollback` path to restore network state;
5. quiesce only exact governed processes;
6. delegate to the existing owner-host snapshot/lifecycle wrapper;
7. restore the original proxy-core / GUI running state after snapshot restoration.
