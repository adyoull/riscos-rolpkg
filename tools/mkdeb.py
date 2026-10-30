#!/usr/bin/env python3
"""mkdeb.py: builds one of riscos-rolpkg's packages.

  mkdeb.py PACKAGE VERSION OUTDIR SRC=DEST [SRC=DEST ...]

PACKAGE is a directory under packages/ holding `control` (without
Version) and any maintainer scripts (preinst, postinst, prerm, postrm,
conffiles). Each SRC=DEST copies a file or directory SRC to DEST inside
the package (DEST is an absolute path on the installed system). Files are
owned by root; the package's postinst fixes anything that must belong to
RISC OS (uid 1000). The .deb is written to OUTDIR/PACKAGE_VERSION_ARCH.deb.
"""
import os, shutil, subprocess, sys, tempfile

def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    name, version, out = sys.argv[1:4]
    here = os.path.dirname(os.path.abspath(__file__))
    pdir = os.path.join(here, '..', 'packages', name)
    control = open(os.path.join(pdir, 'control')).read().rstrip('\n')
    arch = [l.split(':', 1)[1].strip() for l in control.splitlines() if l.startswith('Architecture:')][0]
    with tempfile.TemporaryDirectory() as t:
        root = os.path.join(t, 'root')
        os.makedirs(os.path.join(root, 'DEBIAN'))
        for m in sys.argv[4:]:
            src, dest = m.split('=', 1)
            target = os.path.join(root, dest.lstrip('/'))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            if os.path.isdir(src):
                shutil.copytree(src, target, symlinks=True)
            else:
                shutil.copy2(src, target)
        cr = os.path.join(pdir, 'copyright')
        if os.path.exists(cr):
            d = os.path.join(root, 'usr/share/doc', name)
            os.makedirs(d, exist_ok=True)
            shutil.copy(cr, os.path.join(d, 'copyright'))
        size = 0
        for d, _, fs in os.walk(root):
            for f in fs:
                p = os.path.join(d, f)
                if not os.path.islink(p):
                    size += os.path.getsize(p)
        with open(os.path.join(root, 'DEBIAN', 'control'), 'w') as f:
            lines = control.splitlines()
            lines.insert(1, 'Version: ' + version)
            lines.insert(3, 'Installed-Size: %d' % ((size + 1023) // 1024))
            f.write('\n'.join(lines) + '\n')
        for s in ('preinst', 'postinst', 'prerm', 'postrm', 'conffiles'):
            p = os.path.join(pdir, s)
            if os.path.exists(p):
                shutil.copy(p, os.path.join(root, 'DEBIAN', s))
                os.chmod(os.path.join(root, 'DEBIAN', s), 0o644 if s == 'conffiles' else 0o755)
        os.makedirs(out, exist_ok=True)
        deb = os.path.join(out, '%s_%s_%s.deb' % (name, version, arch))
        subprocess.run(['dpkg-deb', '--root-owner-group', '-Zxz', '--build', root, deb], check=True,
                       stdout=subprocess.DEVNULL)
        print(deb)

main()
