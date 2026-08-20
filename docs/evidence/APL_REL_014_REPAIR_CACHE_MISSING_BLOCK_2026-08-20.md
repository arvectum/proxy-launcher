# APL-REL-014 pre-existing repair-cache drift

A real owner-host acceptance attempt on 2026-08-20 reached the runtime-aware APL-REL-014 preflight and stopped before runtime/process/network mutation because the registered 0.2.3 installation did not contain `Arvectum Proxy Launcher Repair.exe`.

The signed production release itself is not implicated:

- the sealed 0.2.3 Inno Setup definition caches the setup executable as `Arvectum Proxy Launcher Repair.exe` after installation;
- canonical signed-set lifecycle acceptance already verifies that the cache exists after fresh install, matches the sealed installer SHA-256, and successfully repairs a deliberately damaged application binary through that cached copy;
- therefore the missing file is classified as pre-existing owner-host drift/history, not a signed-release failure.

Compatibility handling is transactional: a drift wrapper verifies the exact signed release and the governed installed identity, stages the exact signed setup only as the temporary missing repair cache required by the proven wrappers, delegates the unchanged runtime-aware acceptance chain, and removes the staged cache afterward so the pre-existing host state is restored exactly.
