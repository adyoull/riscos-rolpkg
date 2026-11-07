#!/usr/bin/env python3
# Copyright (c) 2026 Andrew Youll. MIT licence (see LICENSE).
"""index.py: writes the apt repository's indexes and signs them.

  index.py SITE [KEYID]

SITE holds pool/*.deb (the last two versions of each package, so that an
update can be rolled back). Writes SITE/dists/rol/main/binary-{arm64,all}/
Packages(.xz) and SITE/dists/rol/{Release,InRelease,Release.gpg}, signed
with KEYID (gpg; GNUPGHOME chooses the keyring). Also SITE/changes.txt,
each package version's changes from CHANGELOG.md (tools/changes.py), which
Updates shows.
"""
import hashlib, lzma, os, subprocess, sys, time

SUITE, COMPONENT, ARCHES = 'rol', 'main', ('arm64', 'all')

def control(deb):
    return subprocess.run(['dpkg-deb', '-f', deb], check=True, capture_output=True, text=True).stdout.strip()

def hashes(data):
    return {'MD5sum': hashlib.md5(data).hexdigest(), 'SHA256': hashlib.sha256(data).hexdigest()}

def main():
    site = sys.argv[1]
    key = sys.argv[2] if len(sys.argv) > 2 else None
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, os.path.join(here, 'changes.py'),
                    os.path.join(here, '..', 'CHANGELOG.md'), os.path.join(site, 'changes.txt')], check=True)
    debs = sorted(f for f in os.listdir(os.path.join(site, 'pool')) if f.endswith('.deb'))
    stanzas = {a: [] for a in ARCHES}
    for f in debs:
        p = os.path.join(site, 'pool', f)
        data = open(p, 'rb').read()
        c = control(p)
        arch = [l.split(':', 1)[1].strip() for l in c.splitlines() if l.startswith('Architecture:')][0]
        h = hashes(data)
        s = c + '\nFilename: pool/%s\nSize: %d\nMD5sum: %s\nSHA256: %s\n' % (f, len(data), h['MD5sum'], h['SHA256'])
        stanzas[arch].append(s)
    files = []
    for a in ARCHES:
        d = os.path.join(site, 'dists', SUITE, COMPONENT, 'binary-' + a)
        os.makedirs(d, exist_ok=True)
        text = '\n'.join(stanzas[a]).encode()
        for name, data in (('Packages', text), ('Packages.xz', lzma.compress(text))):
            open(os.path.join(d, name), 'wb').write(data)
            files.append(('%s/binary-%s/%s' % (COMPONENT, a, name), data))
    rel = ['Origin: riscos-rolpkg', 'Label: RISC OS on Linux', 'Suite: %s' % SUITE, 'Codename: %s' % SUITE,
           'Date: ' + time.strftime('%a, %d %b %Y %H:%M:%S UTC', time.gmtime()),
           'Architectures: arm64 all', 'Components: %s' % COMPONENT,
           'Description: RISC OS on Linux: RISC OS, its Linux side and kernels']
    for field, fn in (('MD5Sum', hashlib.md5), ('SHA256', hashlib.sha256)):
        rel.append(field + ':')
        for name, data in files:
            rel.append(' %s %d %s' % (fn(data).hexdigest(), len(data), name))
    d = os.path.join(site, 'dists', SUITE)
    open(os.path.join(d, 'Release'), 'w').write('\n'.join(rel) + '\n')
    if key:
        for out, opt in (('InRelease', '--clearsign'), ('Release.gpg', '--detach-sign')):
            o = os.path.join(d, out)
            if os.path.exists(o):
                os.unlink(o)
            subprocess.run(['gpg', '--batch', '--yes', '--armor', '--local-user', key, opt,
                            '-o', o, os.path.join(d, 'Release')], check=True)
    print('%d packages indexed' % len(debs))

main()
