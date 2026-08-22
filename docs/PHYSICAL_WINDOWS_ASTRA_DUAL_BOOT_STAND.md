# Physical x86-64 acceptance stand: Windows 10 → Windows 11 + Astra Linux dual boot

Updated: 2026-08-22

## Purpose

Use one separate physical x86-64 laptop with a 512 GB SSD as a persistent two-platform acceptance stand.

Current state:

- physical x86-64 laptop;
- 512 GB internal SSD;
- Windows 10 currently installed;
- target final state: Windows 11 + Astra Linux Special Edition 1.8 x86-64 dual boot under UEFI/GPT.

The machine is disposable from the product-data perspective. Do not keep the only copy of any release artifact, acceptance evidence, secret or recovery key on it.

## Stage A — inventory current Windows 10 before changing anything

Record privately or in non-secret evidence as appropriate:

```powershell
winver
Get-ComputerInfo
Get-Disk
Get-Partition
Get-Volume
Get-Tpm
Confirm-SecureBootUEFI
```

Also record:

- exact Windows edition/build;
- CPU model and architecture;
- firmware mode (UEFI preferred);
- TPM 2.0 availability;
- Secure Boot capability/state;
- current SSD partition layout and free space;
- BitLocker/device-encryption state;
- network hardware;
- currently installed security/VPN/proxy software.

Before firmware or partition work, save any BitLocker/device-encryption recovery key outside the laptop.

## Stage B — move the Windows side to Windows 11

Canonical Windows acceptance should use Windows 11, not retained Windows 10.

1. Confirm that the laptop officially satisfies Windows 11 requirements.
2. Update firmware/BIOS only if required by the manufacturer for supported Windows 11 operation.
3. Upgrade or clean-install Windows 11.
4. For APL-WIN-014, final edition must be **Windows 11 Pro, Enterprise or Education**. Home may be used for other regression/lifecycle work but is not the canonical App Control for Business host for this roadmap.
5. Install Windows updates and device drivers required for a normal supported baseline.
6. Before installing Proxy Launcher, record the clean Windows 11 baseline.

If P0.2 is deliberately executed, prefer a clean/reset Windows 11 environment and perform P0.2 before installing product test artifacts or repartitioning for Astra.

## Stage C — Windows acceptance before Linux repartitioning

Recommended order:

1. optional P0.2 clean-machine endpoint-denied rebuild;
2. APL-WIN-014 App Control for Business acceptance;
3. APL-REL-014 exact signed-set fresh install / upgrade / repair / uninstall / rollback acceptance;
4. diagnostics/evidence export;
5. hash-verify copied evidence outside the laptop.

After this point Windows remains installed permanently, but once the disk/boot chain changes for Astra it is no longer an untouched clean-machine baseline.

## Stage D — prepare Windows for safe dual boot

### D1. Disable Fast Startup / hibernation

From an elevated PowerShell/Terminal:

```powershell
powercfg /h off
```

This prevents Windows from leaving NTFS in a hibernated state that is unsafe for dual-boot access.

### D2. BitLocker/device encryption

If active:

- ensure the recovery key is stored safely elsewhere;
- suspend protection before boot-chain/partition changes rather than permanently deleting encryption;
- after dual boot is proven, verify Windows encryption returns to the intended protected state.

### D3. Shrink Windows from Windows itself

Open:

```text
diskmgmt.msc
```

Rules:

1. identify the correct internal 512 GB SSD;
2. do not delete EFI, Microsoft Reserved (MSR) or Windows Recovery partitions;
3. right-click the Windows `C:` partition and choose **Shrink Volume**;
4. leave the destination for Astra as **unallocated space**;
5. reboot Windows and verify it still boots before installing Linux.

Practical target for 512 GB SSD:

- existing EFI/MSR/Recovery: preserve;
- Windows `C:`: roughly 220–260 GiB;
- Astra `/`: roughly 180–220 GiB ext4;
- optional shared data: 20–50 GiB NTFS if genuinely useful.

Exact sizes depend on actual free space. Do not force a risky shrink just to hit these numbers.

## Stage E — prepare Astra installation media

Target:

- Astra Linux Special Edition 1.8;
- x86-64 / AMD64;
- graphical Fly desktop;
- UEFI installation.

1. Obtain the installation ISO only from an official Astra source/account available to Arvectum.
2. Obtain vendor checksum/signature verification data for that exact ISO.
3. Verify the image before writing USB.
4. Record exact ISO identity and digest for APL-LNX-010 evidence.
5. Write a bootable USB (16 GB or larger is sufficient) using a trusted tool such as Rufus/Etcher, preserving a UEFI/GPT-oriented installation path.

Do not continue with an unverified ISO.

## Stage F — install Astra alongside Windows

Boot the Astra USB through its **UEFI** boot entry.

Choose **manual/custom partitioning**. Never choose an option that erases the whole disk.

Critical partition rules:

- do not format/delete Windows NTFS;
- do not delete Windows Recovery/MSR;
- identify the existing EFI System Partition;
- mount the existing EFI System Partition at `/boot/efi` **without formatting it**;
- create Astra root `/` as ext4 only in the unallocated space;
- optional separate `/home` is not required for this acceptance stand;
- dedicated swap partition is optional; a swapfile can be used if needed.

Before accepting the installer's final disk-write confirmation, visually confirm that only the newly allocated Linux space is being formatted.

If Secure Boot prevents the chosen Astra media from booting, first ensure BitLocker is safely suspended, then make only the minimum firmware change required and record it in evidence.

## Stage G — verify the dual boot

After installation:

1. remove the USB;
2. boot Astra;
3. verify Windows Boot Manager still exists in UEFI;
4. boot Windows successfully;
5. boot Astra again;
6. verify Windows encryption/security state is sane;
7. record the final disk layout and boot entries.

GRUB does not have to display Windows automatically as long as both valid UEFI boot entries remain usable.

## Stage H — capture clean Astra baseline

Before installing Proxy Launcher:

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

Expected architecture: `x86_64`.

Also verify:

- Fly graphical session starts normally;
- wired/Wi-Fi connectivity works as applicable;
- NetworkManager manages the primary connection;
- reboot/shutdown/resume are stable enough for acceptance;
- Windows still boots after Astra has rebooted at least once;
- date/time are correct on both OSes.

Do not blindly dist-upgrade before recording the installed Astra release/update level. If updates are applied, use only the official repositories applicable to that edition and record the resulting version.

## Stage I — APL-LNX-010 / Gate R8

Obtain the exact governed `.deb` candidate and verify its identity, then run:

```bash
bash qa/collect_astra_acceptance_preflight.sh
```

Execute the real-host matrix:

- `.deb` install/remove/update;
- GUI start;
- Astra/runtime/backend detection;
- NetworkManager preflight;
- PolicyKit authorization UX;
- enable/sync/disable;
- exact proxy rollback;
- autostart/login;
- crash/restart/reboot recovery;
- user-state preservation;
- diagnostics/support-bundle privacy review.

Gate R8 closes only from PASS evidence on this real Astra installation.

## Persistent stand policy

After Gate R8 retain both Windows 11 and Astra Linux on this laptop. It becomes the permanent regression stand for:

- Windows installer/lifecycle checks;
- Windows application-control experiments when authorized;
- Astra `.deb` regression;
- Linux diagnostics and upgrades;
- future controlled Linux build-input/recovery work;
- future privileged routing prototypes after the relevant STOP-GATE is resolved.

Do not repartition or reinstall either OS until retained evidence has been copied and verified elsewhere.