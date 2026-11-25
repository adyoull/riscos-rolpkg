#!/bin/bash
# build.sh: builds riscos-rolpkg's packages into SITE/pool.
#
#   ROOT=... BOOT=... tools/build.sh SITE PACKAGE=VERSION ...
#
# ROOT: an image's Linux root (as riscos-linux-testbed's image build
#   stages it): /opt/riscos (RISCOS.IMG and the Linux side),
#   /usr/sbin/init, and RISC OS's HardDisc4 at /riscos/HardDisc4.
# BOOT: the image's FAT partition as a directory (kernels, device trees).
# MODULES: for the kernel packages, the kernel's own modules as
#   "make modules_install" staged them (INSTALL_MOD_PATH): the directory
#   holding lib/modules/<release>. They go to /usr/lib/modules/<release>.
# PACKAGE: riscos-rom, riscos-support, riscos-kernel-generic,
#   riscos-kernel-pi, riscos-kernel-wdk2023 (BOOT: the Dev Kit image's EFI
#   partition), riscos-harddisc or riscos-print; VERSION: as in the README.
#
# Copyright (c) 2026 Andrew Youll. MIT licence (see LICENSE).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
site=$1; shift
pool=$site/pool
mk=$here/mkdeb.py
pk=$here/../packages
hd=${ROOT:-}/riscos/HardDisc4
# the kernel's modules, as mkdeb arguments (none without MODULES)
modargs() {
  marg=()
  [ -n "${MODULES:-}" ] || return 0
  local d
  for d in "$MODULES"/lib/modules/*/; do
    d=${d%/}
    # the links back to the build tree mean nothing on the machine
    rm -f "$d/build" "$d/source"
    marg+=("$d=/usr/lib/modules/$(basename "$d")")
  done
}
for spec in "$@"; do
  name=${spec%%=*}; ver=${spec#*=}
  case $name in
    riscos-rom)
      # always mode 755: QEMU (protected RISC OS, as the user riscos) has to
      # read it, and a ROM built elsewhere can come rwx--x--x (5.31-16, -17)
      rt=$(mktemp -d); cp "$ROOT/opt/riscos/RISCOS.IMG" "$rt/RISCOS.IMG"; chmod 755 "$rt/RISCOS.IMG"
      python3 "$mk" "$name" "$ver" "$pool" "$rt/RISCOS.IMG=/opt/riscos/RISCOS.IMG"
      rm -rf "$rt" ;;
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
        "$pk/riscos-support/qcom-gpu-firmware=/usr/lib/riscos/qcom-gpu-firmware" \
        "$pk/riscos-support/place-packman=/usr/lib/riscos/place-packman" \
        "$ROOT/usr/share/riscos/packman-app=/usr/share/riscos/packman-app" \
        "$here/../keys/riscos-rolpkg.gpg=/usr/share/keyrings/riscos-rolpkg.gpg" \
        "$here/../riscos-rolpkg.sources=/etc/apt/sources.list.d/riscos-rolpkg.sources" \
        "$pk/riscos-support/50riscos-ca=/etc/apt/apt.conf.d/50riscos-ca" ;;
    riscos-kernel-generic)
      modargs
      python3 "$mk" "$name" "$ver" "$pool" \
        "$BOOT/EFI/BOOT/BOOTAA64.EFI=/usr/lib/riscos/boot-generic/EFI/BOOT/BOOTAA64.EFI" \
        "$BOOT/dtb=/usr/lib/riscos/boot-generic/dtb" "${marg[@]}" ;;
    riscos-kernel-wdk2023)
      modargs
      python3 "$mk" "$name" "$ver" "$pool" \
        "$BOOT/EFI/BOOT/BOOTAA64.EFI=/usr/lib/riscos/boot-wdk2023/EFI/BOOT/BOOTAA64.EFI" \
        "$BOOT/blackrock.dtb=/usr/lib/riscos/boot-wdk2023/blackrock.dtb" "${marg[@]}" ;;
    riscos-kernel-pi)
      args=()
      for f in "$BOOT"/kernel8.img "$BOOT"/*.dtb "$BOOT"/overlays "$BOOT"/bootcode.bin "$BOOT"/start*.elf "$BOOT"/fixup*.dat "$BOOT"/LICENCE.*; do
        [ -e "$f" ] && args+=("$f=/usr/lib/riscos/boot-pi/$(basename "$f")")
      done
      modargs
      python3 "$mk" "$name" "$ver" "$pool" "${args[@]}" "${marg[@]}" ;;
    riscos-harddisc)
      args=()
      for p in '!Boot/Resources/Configure/!ROLUpdate' '!Boot/Resources/Configure/!LinuxNet' '!Boot/Resources/Configure/!LinuxPrint' \
               '!Boot/Resources/Configure/!WheelSetup' 'TestBed/Modules/KVMWheel,ffa' \
               '!Boot/Resources/!DiscIcon' '!Boot/Resources/!NetWatch' '!Boot/Resources/!Battery' 'TestBed/Modules/LinuxShell,ffa' \
               'TestBed/Modules/USBDriver,ffa' 'TestBed/Modules/LinuxAudio,ffa' 'TestBed/Codec/LinuxCodec,ffa' 'TestBed/Codec/ReadMe,fff' \
               'TestBed/Codec/VCHIQ,ffa' 'TestBed/Codec/BCMSupport,ffa' 'TestBed/Codec/PCI,ffa' 'TestBed/Codec/LoadVC,feb' 'TestBed/Codec/VCTest,fff' 'TestBed/Modules/ARMEABISupport,ffa' 'TestBed/Modules/MManager,ffa' 'TestBed/Modules/MbufRes,ffa' 'TestBed/Modules/LinuxOverlay,ffa' 'TestBed/Modules/SCSILinux,ffa' 'TestBed/Modules/MemMapEntries,ffa' 'TestBed/Modules/PThrTicker,ffa' 'Utilities/!Updates' \
               '!Boot/Choices/Boot/PreDesk/AArdvarkLoader,feb' 'TestBed/NVMe' 'TestBed/PDFS/PDFS,ffa' 'TestBed/PDFS/README,fff' 'TestBed/PDFS/LICENSE,fff' 'TestBed/PDFS/CHANGELOG,fff' \
               '!Boot/Resources/Configure/Monitors/Other/UTM,fff' \
               'Apps/!RiSH' 'Documents/Licences' 'Documents/Source,fff'; do
        args+=("$hd/$p=/riscos/HardDisc4/$p")
      done
      # RISC OS Open's Iconv, for place-iconv (never the test bed's lite one)
      if ! grep -q -a 'Iconv.*0\.12' "$hd/!Boot/Resources/!System/500/Modules/Iconv,ffa" ||
         grep -q -a 'lite, RISC OS for Linux' "$hd/!Boot/Resources/!System/500/Modules/Iconv,ffa"; then
        echo "build.sh: no RISC OS Open Iconv 0.12 in !System.500.Modules" >&2; exit 1
      fi
      args+=("$pk/riscos-harddisc/install-packman-packages=/usr/lib/riscos/install-packman-packages" \
             "$pk/riscos-harddisc/place-armeabisupport=/usr/lib/riscos/place-armeabisupport" \
             "$pk/riscos-harddisc/place-pthreadticker=/usr/lib/riscos/place-pthreadticker" \
             "$pk/riscos-harddisc/place-iconv=/usr/lib/riscos/place-iconv" \
             "$hd/!Boot/Resources/!System/500/Modules/Iconv,ffa=/usr/share/riscos/iconv/Iconv,ffa" \
             "$pk/riscos-harddisc/tidy-packman-names=/usr/lib/riscos/tidy-packman-names" \
             "$ROOT/usr/share/riscos/packman=/usr/share/riscos/packman")
      python3 "$mk" "$name" "$ver" "$pool" "${args[@]}" ;;
    riscos-print)
      python3 "$mk" "$name" "$ver" "$pool" \
        "$pk/riscos-print/setup-linux-printer=/usr/lib/riscos/setup-linux-printer" \
        "$pk/riscos-print/choices=/usr/share/riscos/print/choices" ;;
    *) echo "build.sh: no package $name" >&2; exit 1 ;;
  esac
done
