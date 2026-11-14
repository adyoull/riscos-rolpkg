#!/usr/bin/env python3
# Copyright (c) 2026 Andrew Youll. MIT licence (see LICENSE).
"""changes.py CHANGELOG OUT: the changes of each package version, for the
Updates plug-in, from CHANGELOG.md's tables. One line each:

  PACKAGE <tab> VERSION <tab> DATE <tab> WHAT CHANGED

newest first, plain text (no markdown). The kernels' table has a Package
column that may name several packages: one line for each. index.py writes
it to SITE/changes.txt; rol-info --fetch fetches it, and keeps only the
versions newer than (and the one equal to) what is installed.
"""
import re, sys

def plain(t):
    t = t.replace('\\|', '|')
    t = re.sub(r'\*\*(.*?)\*\*', r'\1', t)
    t = re.sub(r'`([^`]*)`', r'\1', t)
    t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)
    return ' '.join(t.split())

def cells(line):
    # split on | not preceded by a backslash
    parts = re.split(r'(?<!\\)\|', line.strip())
    return [p.strip() for p in parts[1:-1]]

def main():
    src, out = sys.argv[1], sys.argv[2]
    pkg = None
    rows = []
    for line in open(src, encoding='utf-8'):
        m = re.match(r'##\s+(riscos-[a-z0-9-]+)', line)
        if m:
            pkg = m.group(1)
            continue
        if line.startswith('## '):
            pkg = '' if 'Kernels' in line else None
            continue
        if pkg is None or not line.startswith('|') or line.startswith('|---'):
            continue
        c = cells(line)
        if pkg == '':
            if len(c) < 4 or c[0] == 'Package':
                continue
            names = [n.strip() for n in c[0].split(',')]
            ver, date, what = c[1], c[2], c[3]
        else:
            if len(c) < 3 or c[0] == 'Version':
                continue
            names = [pkg]
            ver, date, what = c[0], c[1], c[2]
        for n in names:
            if re.match(r'riscos-[a-z0-9-]+$', n):
                rows.append('%s\t%s\t%s\t%s' % (n, plain(ver), plain(date), plain(what)))
    open(out, 'w', encoding='utf-8').write('\n'.join(rows) + '\n')
    print(len(rows), 'changes')

if __name__ == '__main__':
    main()
