# Physical x86-64 acceptance laptop: Windows 11 -> Astra Linux

Updated: 2026-08-21

## Purpose

Use one separate physical x86-64 laptop as a sequential two-stage acceptance stand:

1. keep the existing Windows 11 installation long enough to execute the physical Windows acceptance gates that must not run on the normal owner workstation;
2. export and retain all Windows evidence;
3. only after the Windows stage is explicitly closed, wipe the laptop and install Astra Linux Special Edition 1.8 x86-64;
4. keep that installation as the real Astra Linux stand for APL-LNX-010 and Gate R8.

This host is disposable from the product-data perspective. Do not place unique secrets, source-of-truth evidence or the only copy of any release artifact on it.

## Stage A — Windows 11 physical acceptance

### A1. Inventory before changing the machine

Record:

- laptop manufacturer/model and serial only in private operator notes if needed; do not commit sensitive identifiers;
- CPU architecture: x86-64;
- Windows edition, version and build (`winver`, `Get-ComputerInfo`);
- Secure Boot state;
- TPM state;
- disk layout and free space;
- whether BitLocker/device encryption is enabled;
- network adapters;
- current installed third-party security/VPN/proxy software.

If device encryption/BitLocker is enabled, retain the recovery key outside the laptop before any destructive work.

### A2. Determine Windows gate eligibility

APL-WIN-014 requires a separate physical Windows 11 **Pro, Enterprise or Education** host.

- If the laptop already runs Pro/Enterprise/Education: it is eligible for the APL-WIN-014 App Control for Business gate after the runbook preflight passes.
- If it runs Home: do not force App Control policy deployment. The machine is still useful for APL-REL-014 lifecycle acceptance and the optional/deferred clean-machine rebuild drill. Upgrade/reinstall a supported Windows edition first if APL-WIN-014 is to be executed on this same machine.

Canonical Windows runbooks remain authoritative:

- `docs/APL_WIN_014_LOCAL_GATE.md`;
- APL-REL-014 lifecycle evidence/runbook files already present in the repository;
- P0.2 clean-machine rebuild documentation if that deferred hardening drill is deliberately reactivated.

### A3. Windows execution order on this laptop

Recommended order:

1. capture the untouched-host inventory;
2. perform any desired clean-machine/offline-rebuild evidence while the machine is still disposable and before product installation;
3. run APL-WIN-014 if the Windows edition is eligible;
4. run APL-REL-014 exact signed-set install/update/uninstall/rollback lifecycle acceptance;
5. collect diagnostics and final evidence;
6. copy all non-secret evidence to the canonical repository/evidence location and a separate retained storage location;
7. verify the copied evidence is readable and hash-stable;
8. mark the Windows stage `WINDOWS ACCEPTANCE COMPLETE` before wiping the disk.

Do not convert the machine to Linux while any Windows real-host gate still depends on it.

## Stage B — Prepare Astra Linux installation media

### B1. Target operating system

Canonical target for APL-LNX-010 on this stand:

- Astra Linux Special Edition 1.8;
- x86-64 / AMD64 build;
- graphical Fly desktop;
- UEFI installation where supported by the laptop.

Use only an official Astra Linux distribution source/account available to Arvectum. Record the exact ISO filename, release/update level and published verification value in local acceptance evidence.

Astra Linux documentation for 1.8 supports x86-64 AMD/Intel systems and BIOS/UEFI. Astra recommends at least 4 GB RAM and 40 GB disk for normal graphical use.

### B2. Download and verify the ISO

On a separate trusted machine, not from an unverified mirror:

1. obtain the current approved Astra Linux Special Edition 1.8 x86-64 installation ISO from the official Astra Linux source available to the organization;
2. obtain the vendor-provided checksum/signature verification material for that exact ISO;
3. verify the ISO before writing the USB stick;
4. record the ISO filename and verified digest in the future APL-LNX-010 evidence.

Do not continue if the image cannot be verified.

### B3. Create the bootable USB from Windows

Astra Linux documentation lists Rufus and Etcher as supported approaches for preparing Astra Linux USB media from Windows.

Recommended Windows path:

1. use a USB flash drive of at least 16 GB;
2. copy any needed files off it first — the device will be erased;
3. start Rufus on the trusted Windows machine;
4. select the **correct USB device**;
5. select the verified Astra Linux ISO;
6. keep UEFI/GPT-oriented defaults for a modern UEFI laptop unless hardware-specific documentation requires otherwise;
7. write the image and wait for successful completion;
8. safely eject the USB drive.

Do not use the future Astra system disk itself as installation media.

## Stage C — Wipe Windows and install Astra Linux

**Destructive boundary:** everything on the laptop's internal disk may be removed. Before continuing, verify that Stage A evidence and any BitLocker recovery information have been copied elsewhere.

### C1. Firmware preparation

1. power the laptop off;
2. insert the Astra installation USB;
3. enter UEFI/BIOS setup or the one-time boot menu using the laptop manufacturer's key (`F2`, `F12`, `Esc`, `Del` or equivalent);
4. prefer UEFI mode rather than Legacy/CSM;
5. select the USB device as the temporary boot source;
6. if the Astra installation media does not boot with Secure Boot enabled, follow the Astra 1.8 installation guidance and temporarily disable Secure Boot for this stand; record that state in acceptance evidence rather than hiding it;
7. boot the Astra installer.

### C2. Installation choices

For this dedicated acceptance stand:

1. choose the graphical installation path/Fly desktop;
2. choose Russian or English UI as convenient for testing, but record the choice;
3. use the internal system disk as the target;
4. because the laptop becomes a dedicated Linux stand, select full-disk replacement rather than Windows dual boot;
5. for UEFI installation, ensure an EFI System Partition is created/mounted at `/boot/efi`;
6. use a normal Linux filesystem such as ext4 for the root filesystem;
7. create a normal non-root operator account and use `sudo` for administration;
8. configure hostname, for example `apl-astra-stand`, unless another governed test hostname is chosen;
9. install the graphical Fly environment and NetworkManager components required for desktop networking;
10. complete installation and reboot;
11. remove the USB stick when prompted / before the machine boots the installer again.

Do not create a Windows dual-boot configuration for this stand unless a later explicit testing requirement needs one. A single-OS Astra installation is simpler and gives cleaner acceptance evidence.

### C3. First boot baseline

Before installing Proxy Launcher, capture the clean Astra baseline:

```bash
cat /etc/os-release
uname -a
uname -m
lsblk -f
ip link
nmcli --version
nmcli general status
nmcli general permissions
nmcli connection show
printf 'XDG_SESSION_TYPE=%s\nXDG_CURRENT_DESKTOP=%s\n' "$XDG_SESSION_TYPE" "$XDG_CURRENT_DESKTOP"
```

Expected architecture is `x86_64`.

Also verify:

- graphical Fly session starts normally;
- wired/Wi-Fi connectivity works as applicable;
- NetworkManager is active and manages the primary connection;
- reboot/shutdown/resume are stable enough for acceptance;
- date/time are correct.

Save this as clean-host evidence before application installation.

### C4. Update policy

Do not blindly dist-upgrade the stand before recording the installed Astra version. First capture the baseline, then decide whether APL-LNX-010 targets the installation image as shipped or the current vendor-supported 1.8 update level.

If updating, use only the official Astra repositories applicable to the installed edition/update level and record the resulting version. Do not add unrelated third-party repositories before APL-LNX-010.

## Stage D — APL-LNX-010 real Astra acceptance

After the clean Astra baseline is retained:

1. obtain the exact governed `.deb` release candidate and its hash/evidence;
2. run the repository preflight collector:

```bash
bash qa/collect_astra_acceptance_preflight.sh
```

3. execute the APL-LNX-010 real-host matrix, including:
   - package install;
   - application start and GUI;
   - Astra/runtime/backend detection;
   - NetworkManager preflight and PolicyKit authorization UX;
   - enable/sync/disable;
   - exact rollback;
   - autostart/login behavior;
   - crash/restart/reboot recovery;
   - update/remove behavior and user-state preservation;
   - diagnostics/support-bundle privacy review;
4. retain logs/evidence outside the stand as well as in the governed repository evidence package;
5. close Gate R8 only if the real-host matrix passes.

Ubuntu CI or another Linux distribution is not a substitute for this gate.

## Failure handling

If Astra installation or hardware support fails:

- do not silently switch the gate to Ubuntu/Debian;
- record the exact hardware/installer failure;
- first check the current Astra Linux hardware/install guidance;
- if the laptop is materially incompatible with Astra, classify the host as unsuitable and use another real Astra-capable x86-64 host.

Astra Linux 1.8 documentation notes that installation from USB may in some cases stall around the kernel-installation stage; follow the current vendor workaround/documentation rather than improvising changes to the product acceptance criteria.

## Stand lifecycle after Gate R8

After Gate R8, keep Astra Linux installed on this laptop as the persistent Linux/Astra regression stand. Use it for later:

- Astra packaging regression;
- controlled Linux build-input mirror/recovery work;
- future privileged per-application routing prototypes when explicitly authorized;
- real Linux diagnostics and upgrade acceptance.

Do not repurpose or wipe the stand until its retained evidence has been copied and verified elsewhere.