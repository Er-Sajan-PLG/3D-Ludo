#!/usr/bin/env python3
"""Simple script to check the scaffolded Flutter structure."""
import os

root = os.path.abspath(os.path.dirname(__file__))
paths = [
    'Flutter',
    os.path.join('Flutter', 'UI'),
    os.path.join('Flutter', 'Authentication'),
    os.path.join('Flutter', 'Store'),
    os.path.join('Flutter', 'Lobby'),
    os.path.join('Flutter', 'Friends'),
    os.path.join('Flutter', 'Inventory'),
    os.path.join('Flutter', 'Settings'),
    os.path.join('Flutter', '3D Game Engine', 'Unity'),
]

print('Checking scaffolded directories under:', root)
all_ok = True
for p in paths:
    full = os.path.join(root, p)
    exists = os.path.exists(full)
    print(f"- {p}: {'FOUND' if exists else 'MISSING'}")
    if exists:
        try:
            print('  contains:', os.listdir(full))
        except Exception as e:
            print('  (could not list contents)', e)
    else:
        all_ok = False

if all_ok:
    print('\nStructure check: OK')
else:
    print('\nStructure check: INCOMPLETE')

# exit code 0 for OK, 1 otherwise
import sys
sys.exit(0 if all_ok else 1)
