#!/usr/bin/env python3
"""firmware.py: gathers the firmware files the kernels' modules ask for.

  firmware.py --lf LINUX-FIRMWARE --class usb|other --out DIR
              [--without DIR] [--skip PREFIX ...] MODULES-DIR ...

LINUX-FIRMWARE is a checkout of linux-firmware. Each MODULES-DIR is a
kernel's /lib/modules/<release> (with depmod's modules.dep). Every module
names the firmware it may ask for (modinfo's "firmware" lines); those
files are copied from linux-firmware into DIR, laid out as /usr/lib/firmware.

--class usb    the firmware of modules that drive USB devices (a module
               with a "usb:" alias, and the modules it depends on)
--class other  the firmware of all the other modules
--without DIR  leave out files that are already in DIR (the other class's
               output: a file needed by both goes in one package only)
--skip PREFIX  leave out names starting PREFIX (ath12k/ is very large)

With --class usb, linux-firmware's WHENCE and every licence file go in
too (LICENSES/, with SOURCE naming the linux-firmware commit): the other
package depends on this one for them.

A name can be a pattern (brcmfmac*-sdio.*.bin); a name that WHENCE makes a
link becomes a link, with its target; Intel's iwlwifi names are the newest
the driver would take, and the newest linux-firmware has is used.
What is asked for and not in linux-firmware is listed at the end (old
drivers whose firmware was never there).

Copyright (c) 2026 Andrew Youll. MIT licence (see LICENSE).
"""
import argparse, glob, os, re, shutil, subprocess, sys


def modinfo(path, field):
    r = subprocess.run(['modinfo', '-F', field, path], capture_output=True, text=True)
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lf', required=True)
    ap.add_argument('--class', dest='cls', choices=('usb', 'other'), required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--without')
    ap.add_argument('--skip', action='append', default=[])
    ap.add_argument('modules', nargs='+')
    a = ap.parse_args()

    # WHENCE's links: name -> target (relative to the link's directory)
    links = {}
    for l in open(os.path.join(a.lf, 'WHENCE'), errors='replace'):
        m = re.match(r'Link:\s*(\S+)\s*->\s*(\S+)', l)
        if m:
            links[m.group(1)] = m.group(2)

    wanted = set()
    for md in a.modules:
        kos = {}
        for d, _, fs in os.walk(md):
            for f in fs:
                if f.endswith('.ko'):
                    p = os.path.join(d, f)
                    kos[os.path.relpath(p, md)] = p
        deps = {}
        for l in open(os.path.join(md, 'modules.dep')):
            k, _, v = l.partition(':')
            deps[k.strip()] = v.split()
        usb = set()
        for rel, p in kos.items():
            if any(al.startswith('usb:') for al in modinfo(p, 'alias')):
                usb.add(rel)
                usb.update(deps.get(rel, []))
        for rel, p in kos.items():
            if (rel in usb) != (a.cls == 'usb'):
                continue
            wanted.update(modinfo(p, 'firmware'))
        # the drivers built into the kernel ask for firmware too (a USB
        # network adapter's, say): modules.builtin.modinfo has their
        # "name.firmware=FILE" entries, and "name.file=" (the source
        # directory: one under a usb/ directory drives USB devices)
        bi = os.path.join(md, 'modules.builtin.modinfo')
        if os.path.exists(bi):
            fw, busb = {}, set()
            for e in open(bi, 'rb').read().split(b'\0'):
                m = re.match(r'([^.=]+)\.(firmware|file)=(.*)', e.decode(errors='replace'))
                if not m:
                    continue
                if m.group(2) == 'firmware':
                    fw.setdefault(m.group(1), []).append(m.group(3))
                elif '/usb/' in m.group(3) + '/':
                    busb.add(m.group(1))
            for name, fs in fw.items():
                if (name in busb) == (a.cls == 'usb'):
                    wanted.update(fs)

    def resolve(name, out):
        """the files (and links) NAME needs, added to out: {name: target or None}"""
        if name in out:
            return True
        p = os.path.join(a.lf, name)
        if name in links:
            target = os.path.normpath(os.path.join(os.path.dirname(name), links[name]))
            if resolve(target, out):
                out[name] = links[name]
                return True
            return False
        if os.path.isfile(p):
            out[name] = None
            return True
        return False

    files, missing = {}, []
    for name in sorted(wanted):
        if any(name.startswith(s) for s in a.skip):
            continue
        names = [name]
        if any(c in name for c in '*?['):
            names = [os.path.relpath(g, a.lf) for g in glob.glob(os.path.join(a.lf, name))]
            names += [n for n in links if glob.fnmatch.fnmatch(n, name)]
        ok = False
        for n in names:
            ok |= resolve(n, files)
        if not ok:
            # Intel: iwlwifi-<chip>-<api>.ucode, the newest api the driver knows
            m = re.match(r'(.*-)(\d+)(\.ucode)$', name)
            if m:
                have = []
                for g in glob.glob(os.path.join(a.lf, m.group(1) + '*' + m.group(3))):
                    m2 = re.match(re.escape(m.group(1)) + r'(\d+)' + re.escape(m.group(3)) + '$',
                                  os.path.relpath(g, a.lf))
                    if m2 and int(m2.group(1)) <= int(m.group(2)):
                        have.append((int(m2.group(1)), os.path.relpath(g, a.lf)))
                if have:
                    ok = resolve(max(have)[1], files)
        if not ok:
            missing.append(name)

    n = size = 0
    for name, target in sorted(files.items()):
        if a.without and os.path.lexists(os.path.join(a.without, name)):
            continue
        dest = os.path.join(a.out, name)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if target is None:
            shutil.copy2(os.path.join(a.lf, name), dest)
            size += os.path.getsize(dest)
        else:
            if os.path.lexists(dest):
                os.remove(dest)
            os.symlink(target, dest)
        n += 1
    if a.cls == 'usb':
        lic = os.path.join(a.out, 'LICENSES')
        os.makedirs(lic, exist_ok=True)
        shutil.copy2(os.path.join(a.lf, 'WHENCE'), os.path.join(a.out, 'WHENCE'))
        for f in sorted(os.listdir(a.lf)):
            if re.match(r'(LICEN[CS]E|GPL-|COPYING)', f, re.I) and os.path.isfile(os.path.join(a.lf, f)):
                shutil.copy2(os.path.join(a.lf, f), os.path.join(lic, f))
        r = subprocess.run(['git', '-C', a.lf, 'log', '-1', '--format=%H %cd'], capture_output=True, text=True)
        url = subprocess.run(['git', '-C', a.lf, 'remote', 'get-url', 'origin'], capture_output=True, text=True)
        with open(os.path.join(lic, 'SOURCE'), 'w') as f:
            f.write('linux-firmware %s\n(fetched from %s)\n' % (r.stdout.strip(), url.stdout.strip()))
    print('%d files and links, %.1f MB, in %s' % (n, size / 1e6, a.out))
    if missing:
        print('asked for and not in linux-firmware (%d):' % len(missing))
        for m in missing:
            print('  ' + m)


main()
