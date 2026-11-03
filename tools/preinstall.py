#!/usr/bin/env python3
# Copyright (c) 2026 Andrew Youll. MIT licence (see LICENSE).
"""preinstall.py: installs packages into an image's root as dpkg would,
without running anything (for building an image on another machine).

  preinstall.py ROOT DEB...

Unpacks each .deb into ROOT and records it in ROOT/var/lib/dpkg (status,
info/PKG.list, .md5sums, .conffiles and the maintainer scripts), so apt
on the image sees it installed and upgrades it later. The postinst isn't
run: the image builder sets up what it would have.
"""
import hashlib, os, re, subprocess, sys, tempfile

def main():
    root = sys.argv[1]
    adm = os.path.join(root, 'var/lib/dpkg')
    status_p = os.path.join(adm, 'status')
    status = open(status_p).read()
    for deb in sys.argv[2:]:
        ctrl = subprocess.run(['dpkg-deb', '-f', deb], check=True, capture_output=True, text=True).stdout.rstrip('\n')
        name = re.search(r'^Package: (.+)$', ctrl, re.M).group(1)
        with tempfile.TemporaryDirectory() as t:
            subprocess.run(['dpkg-deb', '-e', deb, t + '/DEBIAN'], check=True)
            subprocess.run(['dpkg-deb', '-x', deb, root], check=True)
            files = subprocess.run(['dpkg-deb', '-c', deb], check=True, capture_output=True, text=True).stdout
            paths = []
            for l in files.splitlines():
                p = l.split(None, 5)[5].split(' -> ')[0]
                p = '/' + p.lstrip('./').rstrip('/')
                paths.append('/.' if p == '/' else p)
            md5 = []
            for p in paths:
                full = os.path.join(root, p.lstrip('/'))
                if os.path.isfile(full) and not os.path.islink(full):
                    md5.append('%s  %s' % (hashlib.md5(open(full, 'rb').read()).hexdigest(), p.lstrip('/')))
            info = os.path.join(adm, 'info')
            open(os.path.join(info, name + '.list'), 'w').write('\n'.join(paths) + '\n')
            open(os.path.join(info, name + '.md5sums'), 'w').write('\n'.join(md5) + '\n')
            conff = ''
            for s in ('preinst', 'postinst', 'prerm', 'postrm', 'conffiles'):
                src = os.path.join(t, 'DEBIAN', s)
                if os.path.exists(src):
                    data = open(src, 'rb').read()
                    dst = os.path.join(info, name + '.' + s)
                    open(dst, 'wb').write(data)
                    os.chmod(dst, 0o644 if s == 'conffiles' else 0o755)
                    if s == 'conffiles':
                        for c in data.decode().split():
                            h = hashlib.md5(open(os.path.join(root, c.lstrip('/')), 'rb').read()).hexdigest()
                            conff += '\n %s %s' % (c, h)
        # the status stanza: replace any earlier one for this package
        stanzas = [s for s in status.strip('\n').split('\n\n') if not re.search(r'^Package: %s$' % re.escape(name), s, re.M)]
        lines = ctrl.split('\n')
        lines.insert(1, 'Status: install ok installed')
        if conff:
            lines.append('Conffiles:' + conff)
        stanzas.append('\n'.join(lines))
        status = '\n\n'.join(stanzas) + '\n'
        print('preinstalled', name)
    open(status_p, 'w').write(status)

main()
