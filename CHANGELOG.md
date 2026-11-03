# Changelog

What each package update changed. Newest first within each package. The
updates arrive through Configure → Updates (or `apt full-upgrade`); the
next images include them.

## Coming next (built, not yet packaged)

- **Kernels:** the fast SWI entry is in the kernels already; nothing else
  waiting.

## riscos-rom (RISC OS itself)

| Version | Date | What changed |
|---|---|---|
| 5.31-13 | 3 Nov 2026 | **Files over 2GB on HardDisc4 and USB discs** (up to RISC OS's 4GB - 1): IXFS stopped every file at 2GB ("File too large": LanMan98 copies failed there). |
| 5.31-12 | 3 Nov 2026 | **A connection closed by the other end is seen:** `select()` and Socket_Select report it at once instead of waiting out their timeout (ClawsMail's feed and calendar fetches took a minute each). **Saving to HardDisc4 from editors that check the free space first** (StrongEd) works: IXFS's free space always failed. (5.31-11, the free-space fix alone, wasn't released.) |
| 5.31-10 | 2 Nov 2026 | **FileCore discs:** USB sticks and SD cards in RISC OS's own format appear as `SCSI::` drives, with RISC OS Open's SCSISwitch, SCSIFS and SCSIFiler as on a native Raspberry Pi (HForm can format them). Needs riscos-support 1.0.0018-1 and riscos-harddisc 1.0.0018-1. **The keyboard LEDs** (Caps Lock, Num Lock, Scroll Lock) follow RISC OS. (5.31-9, the LEDs alone, wasn't released.) |
| 5.31-8 | 2 Nov 2026 | **Files get the type of their extension** when nothing else says (no `,xxx`, no stored type), as on DOS discs: files on USB discs and files Linux programs wrote show as JPEG, Text, Archive and so on (`photo/jpg` is a JPEG), with their names unchanged. Saving to a USB disc adds `,xxx` only when the name doesn't already say the type. `IXFS#M:` turns it off. Includes 5.31-7's changes (below). |
| 5.31-7 | 2 Nov 2026 | Not packaged on its own (its changes are in 5.31-8). **MbufManager in the ROM**, as in every RISC OS 5 ROM: !Omni's LanManFS and Access work. **Network servers answer their clients:** a connection's first data, sent before the server accepted it, is seen (RDPServer said "server not responding"). |
| 5.31-6 | 1 Nov 2026 | Socket options for GLib programs (SO_TYPE), unknown TCP options refused, Socket_Sendmsg_1 (found by the web browser project). |
| 5.31-5 | 31 Oct 2026 | The Internet module reports version 5.73, so `RMEnsure Internet 5.xx` checks pass: !Omni's LanManager and !Internet start. |
| 5.31-4 | 31 Oct 2026 | Socket_Select returns when its time runs out (TubeSearch and Reel could hang the machine); a locked file can't be renamed. |
| 5.31-3 | 31 Oct 2026 | Proper RISC OS errors from HardDisc4 ("The disc has no more available space", "This item is locked", "This file is already open") instead of Linux's, the Locked attribute obeyed, delete failures no longer lost; physical memory pool areas done by the kernel itself (GCCSDK's ARMEABISupport 1.08). |
| 5.31-2 | 31 Oct 2026 | All the RAM Linux can give RISC OS (up to 4GB) instead of a fixed figure, and the Task Manager's free memory from it; network statistics for NetStats and InetStat; the version reads "RISC OS 5.31-2 (29 Oct 2026)". |
| 1.0.0001-1 | 30 Oct 2026 | The first (ROM build 5.31-1): RISC OS Open's 5.31 nightly of 29 October 2026 merged into Timothy Baldwin's Linux port, which was RISC OS 5.29. ROL-ROM's CHANGELOG has what that took. |

## riscos-support (the Linux side: start-up, screen, keyboard, sound, network, USB)

| Version | Date | What changed |
|---|---|---|
| 1.0.0024-1 | 3 Nov 2026 | rol-cmd runs commands as RISC OS's own Linux user (riscos) when asked, with no password: for *IXRun and the new *LinuxUser (riscos-harddisc 1.0.0023-1). It can't change the system or gain root's rights. |
| 1.0.0023-1 | 3 Nov 2026 | rol-info gives Updates the changes of each RISC OS on Linux package: Check for updates fetches the list, and Updates' Changes button shows what the versions newer than the one installed change (with riscos-harddisc 1.0.0021-1). |
| 1.0.0022-1 | 3 Nov 2026 | **Programs run faster natively:** NativeSupport 0.18 returns to programs without a Linux signal each time (RiscOSM's map drawing spent about 10 of its 30 seconds on them, against 17 seconds on native RISC OS). USB discs: Eject tries again for a second if the disc is busy, and if a file on it is still open !DiscIcon says so (riscos-harddisc 1.0.0020-1) instead of nothing happening. |
| 1.0.0021-1 | 3 Nov 2026 | The boot (FAT) partition is never left mounted at a restart or shutdown. Before, restarting while the start-up logs were being copied to it (every 15 seconds for the first few minutes) could leave it marked "not properly unmounted", and Linux then warns at every mount ("Volume was not properly unmounted ... Please run fsck") until the disc is checked. |
| 1.0.0020-1 | 2 Nov 2026 | An SD card in the machine's own slot (a Pi's, a laptop's) is treated like a USB stick: mounted if it's FAT, exFAT, NTFS or ext, given to RISC OS as a removable `SCSI::` drive if it's FileCore. The card RISC OS on Linux itself runs from is never touched, and soldered-on eMMC and the other internal discs are left alone. |
| 1.0.0019-1 | 2 Nov 2026 | rol-usbd: a USB disc RISC OS set up (FileCore across the whole disc, even with a partition table, like a RISC OS Pi card or SSD with its FAT Loader inside) is given to RISC OS whole, and none of its partitions is mounted; a USB hard disc is a fixed drive (`SCSI::4` on) and a stick or card removable (`SCSI::0` on), as on a native Pi; a stricter check that a disc is FileCore. Only USB discs and removable cards are looked at, never the machine's internal discs. |
| 1.0.0018-1 | 2 Nov 2026 | rol-fb sets the keyboard's LEDs as RISC OS has them (with RISC OS 5.31-10). rol-usbd gives RISC OS a disc in FileCore format instead of trying to mount it: listed, then handed to SCSILinux opened exclusively (Linux can't mount it meanwhile), with every write reaching the disc before RISC OS is told it's done. |
| 1.0.0017-1 | 2 Nov 2026 | NativeSupport 0.16: turns on the fast SWI entry where the kernel has it (RISC OS's SWIs about three times faster on a Raspberry Pi 4); `*NativeSupport FastSWI On\|Off`. With other kernels, SWIs go the usual way. (1.0.0015-1 and 1.0.0016-1 had brought back 0.15, which replaced a 0.16 installed by hand.) |
| 1.0.0016-1 | 2 Nov 2026 | Files on USB discs aren't marked executable, so RISC OS no longer calls them all UNIX Ex (with RISC OS 5.31-8 they get their extensions' types). |
| 1.0.0015-1 | 2 Nov 2026 | **Video in hardware on the Raspberry Pi:** rol-fb gives VideoOverlay (Reel) the display's video plane, scaled by the display and changed at the vertical blank (no tearing); the pointer, windows and menus stay on top. `*USBDevices` can list Linux's USB devices; a USB disc that can't be mounted is described in the Linux log. |
| 1.0.0014-1 | 1 Nov 2026 | **USB discs and SD cards in RISC OS:** FAT, exFAT, NTFS and ext discs are mounted when plugged in (named by their volume labels) and appear on the icon bar. |
| 1.0.0013-1 | 31 Oct 2026 | Shutdown and restart leave Linux's disc clean (no 14-second disc check at the next start). |
| 1.0.0012-1 | 31 Oct 2026 | Updates shows apt's progress line by line as it comes. |
| 1.0.0011-1 | 31 Oct 2026 | The screen: only what changed is redrawn, and moving the pointer doesn't redraw the screen. |
| 1.0.0009-1 | 31 Oct 2026 | Restart (Ctrl+Break, Restart in the Shutdown box, `*Reset`) restarts the machine instead of switching it off. |
| 1.0.0008-1 | 31 Oct 2026 | `/dev/pts` mounted (apt couldn't write its log). |
| 1.0.0007-1 | 31 Oct 2026 | Alt+Shift+Backspace works as Break, for keyboards without a Break key. |
| 1.0.0006-1 | 31 Oct 2026 | A start-up screen that says what's happening, and a quieter console; setting the root password no longer prints PAM's note on the screen. |
| 1.0.0004-1 | 31 Oct 2026 | The clock set by NTP all the time and kept across starts (a Pi no longer starts in 1970); RISC OS's RAM from what Linux has free. |
| 1.0.0002-1 | 31 Oct 2026 | Linux's partition grows to fill the card or disc; start-up logs copied to the FAT partition (LOGS); rol-fb says which screen it uses. |
| 1.0.0001-1 | 30 Oct 2026 | The first. |

## riscos-harddisc (the desktop parts on HardDisc4)

| Version | Date | What changed |
|---|---|---|
| 1.0.0026-1 | 3 Nov 2026 | **RDPServer** 0.2 (use the RISC OS desktop from Windows Remote Desktop, the Windows App, FreeRDP or !RDPClient) in HardDisc4.Apps.Network, where PackMan installs it, and recorded in PackMan as installed, so PackMan upgrades and removes it as its own. It's installed once, only if PackMan has no record of RDPServer, so a newer one from PackMan, or a removal, is kept. MIT, with xrdp and Mbed TLS (Apache-2.0); the licences are in the app. |
| 1.0.0025-1 | 3 Nov 2026 | *IXRun always goes through *LinuxUser (as RISC OS's own Linux user, no password), not only in protected RISC OS, and through the shell, so a command's name is enough (*IXRun ls, not only *IXRun /bin/ls). Restart afterwards. |
| 1.0.0024-1 | 3 Nov 2026 | PDFS 0.16.2 beta in HardDisc4.TestBed.PDFS (with its README, CHANGELOG and licence), kept up to date by Updates from now on: phones, tablets and cameras answer reliably (every USB read in whole packets, from DeviceFS's buffer). *RMLoad it, or put it in !Boot.Choices.Boot.PreDesk to load it at start-up. |
| 1.0.0023-1 | 3 Nov 2026 | *IXRun runs Linux programs as RISC OS's own Linux user, with no password (in protected RISC OS it always failed with ENOENT, as RISC OS's own view of the files has no Linux programs): through the new *LinuxUser (LinuxShell 0.03), with riscos-support 1.0.0024-1. *Linux still runs commands as root, after asking for the password. |
| 1.0.0022-1 | 3 Nov 2026 | *IXRun works: in protected RISC OS (the standard set-up) it always failed with ENOENT, as RISC OS's own view of the files has no Linux programs or terminals; it now goes through *Linux, which runs the command outside it (as root, after asking for the password). |
| 1.0.0021-1 | 3 Nov 2026 | Updates: a Changes button under the RISC OS on Linux packages opens a window of what each newer version changes, so you can see what an update brings before installing it (with riscos-support 1.0.0023-1; Check for updates fetches the list). |
| 1.0.0020-1 | 3 Nov 2026 | !DiscIcon: a USB disc's directory windows close when it's ejected or pulled out; Eject works when a directory on the disc was the last one listed (it kept the disc busy), and a disc that's still in use is reported (with riscos-support 1.0.0022-1). |
| 1.0.0019-1 | 2 Nov 2026 | SCSILinux reports a disc as removable or fixed as Linux says (with riscos-support 1.0.0019-1). |
| 1.0.0018-1 | 2 Nov 2026 | SCSILinux, loaded at start-up: the driver that gives RISC OS's SCSIFS the FileCore discs Linux hands over (RISC OS 5.31-10 and riscos-support 1.0.0018-1). |
| 1.0.0017-1 | 2 Nov 2026 | LinuxOverlay (with riscos-support 1.0.0015-1: Reel's video in hardware), loaded at start-up; `*USBDevices` also lists Linux's own USB devices (keyboard, mouse, discs, card readers) and what's on their discs. |
| 1.0.0016-1 | 1 Nov 2026 | USB discs and cards get the removable drive icon; MbufManager (and its messages) loaded at start-up when the ROM hasn't one, so !Omni works on RISC OS before 5.31-7. |
| 1.0.0015-1 | 1 Nov 2026 | GCCSDK's ARMEABISupport 1.05 is the installed version (1.08 isn't stable on RISC OS on Linux), in !System where PackMan's package puts it. |
| 1.0.0014-1 | 31 Oct 2026 | The VideoCore stand-ins (VCHIQ, BCMSupport, PCI) loaded at start-up where Linux has the Pi's VideoCore, for ReelHWAccel's H.264. |
| 1.0.0013-1 | 31 Oct 2026 | Updates stays open while installing or rolling back, and only one runs at a time. |
| 1.0.0012-1 | 31 Oct 2026 | NetWatch reads Linux's network status in one go. |
| 1.0.0010-1 | 31 Oct 2026 | LinuxCodec loaded at start-up. |
| 1.0.0009-1 | 31 Oct 2026 | LinuxCodec 0.03 (whole pictures to the decoder: split pictures had turned green) and its ReadMe. |
| 1.0.0007-1 | 31 Oct 2026 | LinuxCodec: the Raspberry Pi's H.264 decoder for RISC OS programs. |
| 1.0.0006-1 | 31 Oct 2026 | NetWatch lets null events through; Updates' details use the desktop font's line height. |
| 1.0.0004-1 | 31 Oct 2026 | NetWatch: name servers follow the network when a link or Wi-Fi comes up after the desktop; the wireless regulatory database's licence. |
| 1.0.0001-1 | 30 Oct 2026 | The first. |

## Kernels

| Package | Version | Date | What changed |
|---|---|---|---|
| riscos-kernel-pi | 6.6.78-4 | 2 Nov 2026 | **The fast SWI entry:** RISC OS's SWIs go straight to RISC OS instead of through Linux's security filter and a signal (with NativeSupport 0.16, riscos-support 1.0.0017-1): about 2.4 µs down to 745 ns per SWI on a Raspberry Pi 4. Only RISC OS's own process is affected. |
| riscos-kernel-generic, riscos-kernel-wdk2023 | 7.2.0-3 | 2 Nov 2026 | The same fast SWI entry. |
| riscos-kernel-pi | 6.6.78-3 | 1 Nov 2026 | NTFS discs (and exFAT, already there). |
| riscos-kernel-generic, riscos-kernel-wdk2023 | 7.2.0-2 | 1 Nov 2026 | exFAT discs (SD cards and sticks over 32GB) and UAS (fast USB discs). |
| riscos-kernel-pi | 6.6.78-2 | 31 Oct 2026 | The kernels keep their own versions from here. |
| riscos-kernel-generic, riscos-kernel-wdk2023 | 7.2.0-1 | 31 Oct 2026 | The same. |

Copyright (c) 2026 Andrew Youll. MIT licence (see LICENSE).
