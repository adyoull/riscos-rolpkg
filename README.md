# riscos-rolpkg

The package repository for **RISC OS on Linux** images: RISC OS itself, the
Linux side that runs it, the kernels and RISC OS on Linux's own desktop
parts, as Debian packages. An image keeps them up to date from
**Configure → Updates** (or `*Linux apt-get full-upgrade`), alongside
Debian's own updates.

```
deb https://adyoull.github.io/riscos-rolpkg/ rol main
```

The images already have this source (`/etc/apt/sources.list.d/riscos-rolpkg.sources`)
and its key (`/usr/share/keyrings/riscos-rolpkg.gpg`, also
[`riscos-rolpkg.asc`](keys/riscos-rolpkg.asc); fingerprint
`C7CC 988D 25FD FAF8 00E0  AD6E 019A FF73 7974 A1C3`).

## The packages

| Package | What | Where it goes |
|---|---|---|
| `riscos-rom` | RISC OS (the ROM) | `/opt/riscos/RISCOS.IMG`; the one it replaces is kept in `/opt/riscos/rollback` |
| `riscos-support` | the Linux side: init, rol-fb, rol-snd, rol-netd, rol-cmd, rol-usbd, qemu-arm-riscos, NativeSupport; this repository's source and key | `/opt/riscos`, `/usr/sbin/init`, `/usr/lib/riscos` |
| `riscos-kernel-generic` | the kernel for UEFI machines (UTM, QEMU, boards) and the Pinebooks | copied onto the FAT partition (`EFI/BOOT/BOOTAA64.EFI`, `dtb/`); the old files are kept as `*.old` |
| `riscos-kernel-wdk2023` | the Windows Dev Kit 2023's kernel (it loads `blackrock.dtb`) and device tree | copied onto the Dev Kit image's EFI partition; the old files are kept as `*.old` |
| `riscos-kernel-pi` | the Raspberry Pi kernel, device trees, overlays and firmware | copied onto the FAT partition (`kernel8.img` …); `config.txt` and `cmdline.txt` are left alone |
| `riscos-harddisc` | RISC OS on Linux's desktop parts: Configure's Updates and Linux network, the hard disc icon, `*Linux` (LinuxShell), USBDriver, LinuxCodec (Linux's video decoders) | `/riscos/HardDisc4`; your own files and choices are never touched |

Only the kernel the machine starts is kept up to date: the Updates plug-in
holds any other (`apt-mark hold`), so the generic card still starts on both
a Pi and a UEFI machine. The Dev Kit image has only its own kernel
(`riscos-kernel-wdk2023` conflicts with `riscos-kernel-generic`: both write
`EFI/BOOT/BOOTAA64.EFI`).

New versions take effect at the next start (shut down and switch on).

## Going back

- **Configure → Updates → Roll back RISC OS** installs the RISC OS build
  before the one you have, from this repository (every version stays here).
- **If a new RISC OS won't start:** put the card in any computer and make an
  empty file called `ROLLBACK` on its small FAT partition. The next start puts
  the RISC OS that was replaced back in place.
- **If a new kernel won't start:** rename the `*.old` file on the FAT
  partition back (for example `EFI/BOOT/BOOTAA64.EFI.old` →
  `EFI/BOOT/BOOTAA64.EFI`, or `kernel8.img.old` → `kernel8.img` on a Pi).

## Versions

- **RISC OS itself** (`riscos-rom`) keeps RISC OS's own version, with a
  count of this project's builds of it after the hyphen: `5.31-2` (RISC OS
  5.31, second build). RISC OS shows the same: "RISC OS 5.31-2 (29 Oct
  2026)", with the date of RISC OS Open's nightly it was built from. The
  first build was published as `1.0.0001-1`.
- **Its Linux side and the desktop parts** (`riscos-support`,
  `riscos-harddisc`) carry the RISC OS on Linux build they came from:
  `1.0.<build>-1`, with a four-digit build number (`1.0.0004-1`).
- **The kernels** keep the kernel's own version, with a count of this
  project's builds of it after the hyphen: `riscos-kernel-pi` `6.6.78-2`
  (Raspberry Pi's Linux 6.6.78, second build), `riscos-kernel-generic` and
  `riscos-kernel-wdk2023` `7.2.0-1` (Linux 7.2.0, first build).
- Modules keep their own versions.

## Making a release

```sh
ROOT=<image root> BOOT=<FAT partition directory> \
  tools/build.sh site riscos-rom=5.31-2 riscos-kernel-pi=6.6.78-2 ...
tools/index.py site <key id>     # Packages, Release, InRelease (signed)
tools/publish.sh site            # the gh-pages branch, served by GitHub Pages
```

`site/pool` keeps every version ever published (it's the gh-pages branch's
`pool/`). `tools/preinstall.py ROOT DEB...` installs packages into an image
being built, as dpkg would, without running anything.

The signing key isn't in this repository.

## Licence

The tools and packaging: MIT ([LICENSE](LICENSE)). The packages hold RISC OS
(Apache 2.0, RISC OS Open), Timothy Baldwin's Linux port, QEMU (GPL-2.0),
Linux (GPL-2.0) and firmware under their own licences; see each package.

Copyright (c) 2026 Andrew Youll. MIT licence (see LICENSE).
