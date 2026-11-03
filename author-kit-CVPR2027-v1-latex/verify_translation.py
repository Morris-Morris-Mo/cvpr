from pathlib import Path
import re

root = Path(__file__).resolve().parent
source = next(root.parents[1].glob('Griffin_*_v1_2026-11-02.md'))
zh = source.read_text(encoding='utf-8').split('## 附录 D.')[0]
en = (root / 'georank_en.md').read_text(encoding='utf-8')

def table_numbers(text):
    rows = [row for row in text.splitlines() if row.startswith('|')]
    return [numbers for row in rows if (numbers := re.findall(r'(?<![A-Za-z_])\d+\.\d+', row))]

assert table_numbers(zh) == table_numbers(en), 'Table decimal values differ'
tex = '\n'.join(path.read_text(encoding='utf-8') for path in root.glob('sec/georank_*.tex'))
assert '\\includegraphics' not in tex
assert not re.search('[\u4e00-\u9fff]', tex)
keys = set(re.findall(r'\\bibitem\{([^}]+)\}', tex))
cites = {key for group in re.findall(r'\\cite\{([^}]+)\}', tex) for key in group.split(',')}
assert cites <= keys and len(keys) == 13
for path in root.glob('sec/georank_*.tex'):
    content = path.read_text(encoding='utf-8')
    environments = re.findall(r'\\(begin|end)\{([^}]+)\}', content)
    stack = []
    for action, name in environments:
        if action == 'begin':
            stack.append(name)
        else:
            assert stack.pop() == name, (path, name)
    assert not stack
print('PASS: all decimal table rows match the Chinese source.')
print('PASS: all citations resolve against 13 bibliography entries.')
print('PASS: LaTeX environments are balanced; no Chinese or image commands in paper content.')
print('English word count:', len(en.split()))
print('Table count:', len(re.findall(r'\\begin\{table\*?\}', tex)))
print('NOTE: source-level checks do not substitute for TeX compilation and visual inspection.')
