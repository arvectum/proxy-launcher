# Physical x86-64 acceptance laptop: Windows 11 + Astra Linux dual boot

Updated: 2026-08-21

## Purpose

Use one separate physical x86-64 laptop with a 512 GB internal SSD as a persistent dual-platform acceptance stand:

1. keep the existing Windows 11 installation and execute the physical Windows acceptance gates that must not run on the normal owner workstation;
2. export and retain all clean-Windows evidence before changing the disk layout;
3. shrink the Windows partition without deleting Windows;
4. install Astra Linux Special Edition 1.8 x86-64 into separate GPT partitions in the newly unallocated space;
5. keep both Windows 11 and Astra Linux bootable on the laptop for future regression work;
6. execute APL-LNX-010 / Gate R8 on the real Astra installation.

This host is disposable from the product-data perspective. Do not place unique secrets, source-of-truth evidence or the only copy of any release artifact on it.

The preferred final state is **UEFI/GPT dual boot**, not two MBR-style logical disks. Windows remains on NTFS; Astra uses its own ext4 filesystem; both boot through UEFI. The existing EFI System Partition must be preserved and must never be formatted during Astra installation.

## Recommended 512 GB layout

Exact sizes may be adjusted after inspecting the current Windows layout and free space. A practical target is:

- existing EFI System Partition: preserve exactly as-is; do not format;
- existing Microsoft Reserved / Windows Recovery partitions: preserve;
- Windows `C:`: approximately 220–250 GiB NTFS;
- Astra Linux `/`: approximately 180–220 GiB ext4;
- optional shared data partition: approximately 30–50 GiB NTFS/exFAT if useful for non-secret transfer data;
- no dedicated swap partition is required for this acceptance stand unless the installed Astra configuration specifically needs one; a swapfile can be used later.

Do not reduce Windows below a comfortable working margin. If the current Windows installation already occupies substantial space, prefer a larger Windows partition and a smaller Astra partition rather than forcing the sizes above.

## Stage A — Windows 11 physical acceptance before repartitioning

### A1. Inventory before changing the machine

Record:

- laptop manufacturer/model and serial only in private operator notes if needed; do not commit sensitive identifiers;
- CPU architecture: x86-64;
- Windows edition, version and build (`winver`, `Get-ComputerInfo`);
- UEFI/Secure Boot state;
- TPM state;
- disk layout and free space;
- whether BitLocker/device encryption is enabled;
- network adapters;
- current installed third-party security/VPN/proxy software.

If BitLocker/device encryption is enabled, retain the recovery key outside the laptop before any partition or firmware change.

### A2. Determine Windows gate eligibility

APL-WIN-014 requires a separate physical Windows 11 **Pro, Enterprise or Education** host.

- If the laptop already runs Pro/Enterprise/Education: it is eligible for the APL-WIN-014 App Control for Business gate after the runbook preflight passes.
- If it runs Home: do not force App Control policy deployment. The machine is still useful for APL-REL-014 lifecycle acceptance and the optional/deferred clean-machine rebuild drill. Upgrade/reinstall a supported Windows edition first if APL-WIN-014 is to be executed on this same machine.

Canonical Windows runbooks remain authoritative:

- `docs/APL_WIN_014_LOCAL_GATE.md`;
- APL-REL-014 lifecycle evidence/runbook files already present in the repository;
- P0.2 clean-machine rebuild documentation if that deferred hardening drill is deliberately reactivated.

### A3. Windows execution order before dual boot

Recommended order:

1. capture the untouched-host inventory;
2. perform any desired P0.2 clean-machine/offline-rebuild evidence while Windows is still the only installed OS;
3. run APL-WIN-014 if the Windows edition is eligible;
4. run APL-REL-014 exact signed-set install/update/uninstall/rollback lifecycle acceptance;
5. collect diagnostics and final evidence;
6. copy all non-secret evidence to the canonical repository/evidence location and a separate retained storage location;
7. verify the copied evidence is readable and hash-stable;
8. mark the clean-Windows phase `WINDOWS CLEAN-HOST ACCEPTANCE COMPLETE`;
9. only then repartition the disk for Astra Linux.

Windows is **not** deleted after this point. The clean-host evidence simply becomes historical after the boot/disk layout changes.

## Stage B — Prepare Windows for safe partition shrink

### B1. Recovery preparation

Before touching partitions:

1. make sure all Windows acceptance evidence is stored elsewhere;
2. retain the BitLocker/device-encryption recovery key outside this laptop;
3. create or retain a Windows recovery/install USB if available;
4. verify that Windows boots normally before starting;
5. record the current partition layout using Disk Management or PowerShell.

If BitLocker/device encryption is active, **suspend protection** for the partitioning/Linux-installation operation rather than permanently removing encryption. Firmware/boot-chain changes may otherwise trigger BitLocker recovery.

### B2. Disable Windows Fast Startup / hibernation

Dual boot is safer when Windows does not leave NTFS volumes in a hibernated/fast-startup state. From an elevated terminal:

```powershell
powercfg /h off
```

This disables hibernation and Fast Startup. It can be reconsidered later after dual-boot behavior is stable.

### B3. Shrink Windows from Windows itself

Use Windows Disk Management (`diskmgmt.msc`) to shrink `C:`.

1. open **Disk Management**;
2. identify the correct internal 512 GB SSD;
3. do **not** delete the EFI, Microsoft Reserved or Recovery partitions;
4. right-click the main Windows `C:` partition and choose **Shrink Volume**;
5. shrink it to leave roughly 180–220 GiB unallocated for Astra, adjusted to actual free space;
6. leave the Linux destination as **unallocated space** — do not format it as NTFS in Windows;
7. reboot Windows once and confirm Windows still starts correctly.

If Windows cannot shrink as far as desired because of immovable files, do not use destructive third-party partitioning immediately. First reduce the requested shrink size and keep a larger Windows partition.

### B4. Optional shared partition

A shared partition is optional and is not required for APL-LNX-010.

If desired, reserve about 30–50 GiB for non-secret cross-platform transfer files. NTFS is preferable if Windows is the primary owner of that data. Do not use a shared partition as the only copy of acceptance evidence.

## Stage C — Prepare Astra Linux installation media

### C1. Target operating system

Canonical target for APL-LNX-010 on this stand:

- Astra Linux Special Edition 1.8;
- x86-64 / AMD64 build;
- graphical Fly desktop;
- UEFI installation.

Use only an official Astra Linux distribution source/account available to Arvectum. Record the exact ISO filename, release/update level and published verification value in local acceptance evidence.

### C2. Download and verify the ISO

On a trusted machine:

1. obtain the approved Astra Linux Special Edition 1.8 x86-64 installation ISO from the official Astra source available to the organization;
2. obtain the vendor-provided checksum/signature material for that exact ISO;
3. verify the ISO before writing the USB stick;
4. record the ISO filename and verified digest for APL-LNX-010 evidence.

Do not continue if the image cannot be verified.

### C3. Create the bootable USB

Astra documentation lists Rufus and Etcher as Windows approaches for preparing installation media.

Recommended path:

1. use a USB flash drive of at least 16 GB;
2. copy any needed files off it first;
3. start Rufus on a trusted Windows machine;
4. select the **correct USB device**;
5. select the verified Astra Linux ISO;
6. keep GPT/UEFI-oriented settings for this modern UEFI laptop unless hardware-specific documentation requires otherwise;
7. write the image;
8. safely eject the USB drive.

## Stage D — Install Astra alongside Windows

### D1. Firmware preparation

1. fully shut down Windows;
2. insert the Astra USB;
3. enter UEFI/BIOS setup or the one-time boot menu (`F2`, `F12`, `Esc`, `Del` or manufacturer equivalent);
4. keep **UEFI** mode; do not switch to Legacy/CSM;
5. boot the USB in its UEFI entry;
6. keep Secure Boot enabled if the chosen Astra image/install path supports it;
7. if the Astra installer cannot boot with Secure Boot enabled, first ensure BitLocker is suspended, then disable Secure Boot only as required and record the change as part of stand evidence.

Do not erase or recreate the disk's GPT partition table.

### D2. Manual partitioning — critical safety boundary

Choose **manual/custom partitioning**, not "use entire disk".

The installer must show the existing Windows partitions plus the unallocated space created in Stage B.

Rules:

1. **do not delete or format the Windows NTFS partition**;
2. **do not delete or format Windows Recovery/MSR partitions**;
3. locate the existing EFI System Partition;
4. assign the existing EFI System Partition as `/boot/efi` **without formatting it**;
5. in the unallocated space create an Astra root partition mounted as `/` with `ext4`;
6. allocate roughly 180–220 GiB to `/`, or the available amount selected during planning;
7. optionally create a separate `/home`, but it is not required for this acceptance stand;
8. a dedicated swap partition is optional; do not sacrifice large disk space to swap solely for this project;
9. install the graphical Fly environment and required NetworkManager components;
10. create a normal non-root operator account;
11. use a governed hostname such as `apl-dualboot-stand`.

Before accepting the installer's final partition-write confirmation, re-check visually that **only newly allocated Linux space is being formatted**. If the installer proposes formatting the Windows NTFS or existing EFI partition, cancel and correct the layout.

Official Astra 1.8 documentation requires a `/boot/efi` partition for UEFI installations; the existing EFI System Partition can serve this purpose as long as it is preserved rather than formatted.

### D3. Bootloader behavior

After installation:

1. reboot with the USB removed;
2. confirm Astra boots;
3. confirm a Windows Boot Manager UEFI entry still exists;
4. confirm Windows still boots, either from GRUB or from the firmware one-time boot menu;
5. do not treat automatic Windows detection in the Astra GRUB menu as mandatory — two valid UEFI boot entries are sufficient for the stand;
6. after booting Windows, confirm BitLocker/device encryption returns to its expected protected state and no unexpected recovery loop exists.

If Astra becomes the default boot entry, that is acceptable. The Windows entry must remain usable.

### D4. First Astra baseline

Before installing Proxy Launcher, capture:

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
- Windows remains bootable after at least one Astra reboot cycle;
- date/time are correct in both operating systems.

### D5. Update policy

Do not blindly dist-upgrade Astra before recording the installed version. First capture the baseline, then decide whether APL-LNX-010 targets the image as shipped or the current vendor-supported 1.8 update level.

If updating, use only official Astra repositories applicable to the installed edition/update level and record the resulting version. Do not add unrelated third-party repositories before APL-LNX-010.

## Stage E — APL-LNX-010 real Astra acceptance

After the clean Astra baseline is retained:

1. obtain the exact governed `.deb` release candidate and its hash/evidence;
2. run:

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

## Using Windows after Astra installation

The Windows installation remains a permanent second side of the stand. It can later be used for:

- Windows installer/regression acceptance;
- signed-set lifecycle regression;
- diagnostic compatibility checks;
- future Windows application-control experiments when the Windows edition is eligible.

However, once Astra has been installed and the disk/boot chain changed, this Windows installation must no longer be described as an untouched clean-machine baseline. A future P0.2 clean-machine proof that requires a truly pristine environment may need reset/reinstallation or another physical host.

## Failure handling

If Astra installation or hardware support fails:

- do not silently switch Gate R8 to Ubuntu/Debian;
- do not destroy the working Windows installation as a troubleshooting shortcut;
- record the exact hardware/installer/bootloader failure;
- first check current Astra Linux hardware/install guidance;
- use the firmware boot menu to verify Windows Boot Manager remains available;
- if the laptop is materially incompatible with Astra, classify it as unsuitable for Gate R8 and use another real Astra-capable x86-64 host.

Astra Linux 1.8 documentation notes that USB installation may in some cases stall around the kernel-installation stage; follow the current vendor workaround/documentation rather than improvising changes to the product acceptance criteria.

## Stand lifecycle after Gate R8

After Gate R8, retain **both** Windows 11 and Astra Linux on this laptop as the persistent dual-platform regression stand. Use it for later:

- Windows installer/lifecycle regression;
- Astra packaging regression;
- controlled Linux build-input mirror/recovery work;
- future privileged per-application routing prototypes when explicitly authorized;
- real cross-platform diagnostics and upgrade acceptance.

Do not repartition, reinstall or wipe either OS until its retained evidence has been copied and verified elsewhere.