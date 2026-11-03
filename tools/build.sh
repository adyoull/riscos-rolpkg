#!/bin/bash
# build.sh: builds riscos-rolpkg's packages into SITE/pool.
#
#   ROOT=... BOOT=... tools/build.sh SITE PACKAGE=VERSION ...
#
# ROOT: an image's Linux root (as riscos-linux-testbed's image build
#   stages it): /opt/riscos (RISCOS.IMG and the Linux side),
#   /usr/sbin/init, and RISC OS's HardDisc4 at /riscos/HardDisc4.
# BOOT: the image's FAT partition as a directory (kernels, device trees).
# PACKAGE: riscos-rom, riscos-support, riscos-kernel-generic,
#   riscos-kernel-pi, riscos-kernel-wdk2023 (BOOT: the Dev Kit image's EFI
#   partition) or riscos-harddisc; VERSION: as in the README.
#
# Copyright (c) 2026 Andrew Youll. MIT licence (see LICENSE).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
site=$1; shift
pool=$site/pool
mk=$here/mkdeb.py
pk=$here/../packages
hd=$ROOT/riscos/HardDisc4
for spec in "$@"; do
  name=${spec%%=*}; ver=${spec#*=}
  case $name in
    riscos-rom)
      python3 "$mk" "$name" "$ver" "$pool" "$ROOT/opt/riscos/RISCOS.IMG=/opt/riscos/RISCOS.IMG" ;;
    riscos-support)
      args=()
      for f in "$ROOT"/opt/riscos/*; do
        b=$(basename "$f")
        case $b in RISCOS.IMG|rollback) continue ;; esac
        args+=("$f=/opt/riscos/$b")
      done
      python3 "$mk" "$name" "$ver" "$pool" "${args[@]}" \
        "$ROOT/usr/sbin/init=/usr/sbin/init" \
        "$pk/riscos-support/fat-partition=/usr/lib/riscos/fat-partition" \
        "$pk/riscos-support/install-boot-files=/usr/lib/riscos/install-boot-files" \
        "$pk/riscos-support/rol-info=/usr/lib/riscos/rol-info" \
        "$here/../keys/riscos-rolpkg.gpg=/usr/share/keyrings/riscos-rolpkg.gpg" \
        "$here/../riscos-rolpkg.sources=/etc/apt/sources.list.d/riscos-rolpkg.sources" \
        "$pk/riscos-support/50riscos-ca=/etc/apt/apt.conf.d/50riscos-ca" ;;
    riscos-kernel-generic)
      python3 "$mk" "$name" "$ver" "$pool" \
        "$BOOT/EFI/BOOT/BOOTAA64.EFI=/usr/lib/riscos/boot-generic/EFI/BOOT/BOOTAA64.EFI" \
        "$BOOT/dtb=/usr/lib/riscos/boot-generic/dtb" ;;
    riscos-kernel-wdk2023)
      python3 "$mk" "$name" "$ver" "$pool" \
        "$BOOT/EFI/BOOT/BOOTAA64.EFI=/usr/lib/riscos/boot-wdk2023/EFI/BOOT/BOOTAA64.EFI" \
        "$BOOT/blackrock.dtb=/usr/lib/riscos/boot-wdk2023/blackrock.dtb" ;;
    riscos-kernel-pi)
      args=()
      for f in "$BOOT"/kernel8.img "$BOOT"/*.dtb "$BOOT"/overlays "$BOOT"/bootcode.bin "$BOOT"/start*.elf "$BOOT"/fixup*.dat "$BOOT"/LICENCE.*; do
        [ -e "$f" ] && args+=("$f=/usr/lib/riscos/boot-pi/$(basename "$f")")
      done
      python3 "$mk" "$name" "$ver" "$pool" "${args[@]}" ;;
    riscos-harddisc)
      args=()
      for p in '!Boot/Resources/Configure/!ROLUpdate' '!Boot/Resources/Configure/!LinuxNet' \
               '!Boot/Resources/Configure/!WheelSetup' 'TestBed/Modules/KVMWheel,ffa' \
               '!Boot/Resources/!DiscIcon' '!Boot/Resources/!NetWatch' 'TestBed/Modules/LinuxShell,ffa' \
               'TestBed/Modules/USBDriver,ffa' 'TestBed/Codec/LinuxCodec,ffa' 'TestBed/Codec/ReadMe,fff' \
               'TestBed/Codec/VCHIQ,ffa' 'TestBed/Codec/BCMSupport,ffa' 'TestBed/Codec/PCI,ffa' 'TestBed/Codec/LoadVC,feb' 'TestBed/Codec/VCTest,fff' 'TestBed/Modules/ARMEABISupport,ffa' 'TestBed/Modules/MManager,ffa' 'TestBed/Modules/MbufRes,ffa' 'TestBed/Modules/LinuxOverlay,ffa' 'TestBed/Modules/SCSILinux,ffa' 'Utilities/!Updates' \
               'TestBed/PDFS/PDFS,ffa' 'TestBed/PDFS/README,fff' 'TestBed/PDFS/LICENSE,fff' 'TestBed/PDFS/CHANGELOG,fff' \
               'Documents/Licences' 'Documents/Source,fff'; do
        args+=("$hd/$p=/riscos/HardDisc4/$p")
      done
      python3 "$mk" "$name" "$ver" "$pool" "${args[@]}" ;;
    *) echo "build.sh: no package $name" >&2; exit 1 ;;
  esac
done
