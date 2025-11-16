import os

paths = [
    'src/__init__.py',
    'src/pages/__init__.py',
    'src/components/__init__.py',
    'src/utils/__init__.py',
    'tests/__init__.py'
]

for path in paths:
    with open(path, 'w', encoding='utf-8') as f:
        f.write('# Package module\n')
    print(f"Fixed: {path}")