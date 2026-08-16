# APL-WIN-008 — Single-instance mutex and duplicate-launch handling

## Status

Implemented for the Windows interactive GUI boundary.

## Production contract

1. The interactive Windows GUI has one canonical instance per Windows session.
2. The boundary is established before `Tk()` construction and before local/network repair side effects.
3. A session-local Win32 named mutex is the authoritative process sentinel. Kernel handle lifetime makes the boundary crash-safe: process termination releases the object automatically.
4. A session-local auto-reset Win32 event carries duplicate-launch activation requests to the primary process without sockets, temp files, lock files, or mutable user data.
5. A duplicate GUI launch does not start a second `Tk()` tree, does not repair Run entries, does not mutate proxy/network state, and exits successfully after notifying the primary instance.
6. Duplicate handling requests restoration/foregrounding twice: best-effort Win32 activation from the newly launched process, plus an event consumed by the primary Tk event loop. The primary performs a bounded topmost pulse and immediately clears it.
7. `--doctor`, `--doctor-json`, `--start`, `--stop`, `--status`, and `--rollback` remain outside the GUI mutex. They are operational commands, not second GUI instances.
8. Portable self-handoff remains authoritative: a portable EXE first hands execution to the managed canonical copy; the canonical GUI then participates in the single-instance boundary.
9. Mutex/event names include an Arvectum-specific GUID and use the `Local\` namespace so unrelated products and other Terminal Services sessions do not share the GUI sentinel.
10. Any failure to establish the Windows mutex/event boundary is fail-closed for GUI startup and is written to the existing application log.

## Acceptance scenarios

- Launch the canonical EXE once: one GUI opens normally.
- Launch it again while visible: no second GUI is created; the existing window is surfaced.
- Minimize the first GUI, then launch again: the existing window is restored/surfaced.
- Rapidly launch the EXE twice: the first process owns the mutex; the second signals the activation event and exits.
- Kill the primary process, then launch again: the new process becomes primary because Windows closed the dead process handles.
- Keep the GUI open and execute `--status` / `--start` / `--stop`: the command is not blocked by the GUI mutex.
- Launch a portable copy while the managed canonical GUI is already open: portable handoff reaches canonical execution, which activates the existing canonical GUI instead of creating another one.

## Regression coverage

`tests/test_single_instance.py` verifies primary/duplicate classification, activation signaling, non-blocking event polling, crash-safe handle cleanup semantics, fail-closed setup cleanup, duplicate-launch side-effect isolation, service-command bypass, and Tk activation scheduling.
