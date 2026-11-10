"""Genera páginas de CV condensado desde cv.md.
uso: cvgen.py cv.md repo_dir  -> escribe repo_dir/cv-full.md (bloque) e imprime stats"""
import re, sys, json, subprocess, pathlib, tempfile
cv_path, repo = sys.argv[1], pathlib.Path(sys.argv[2])
SKIP_H2 = {'Docencia', 'Prensa'}
SKIP_H3 = {'Residencias'}
cv = re.sub(r'<!--.*?-->', '', open(cv_path).read(), flags=re.S)

def absurl(u):
    if u.startswith('http'): return u
    return 'https://misaa.cc/' + u.lstrip('./')

def esc(t):
    t = t.replace('[', '\\[').replace(']', '\\]')
    if t.count('*') % 2: t = t.replace('*', '\\*')
    return t

LINK_GROUP = re.compile(r'\s*\(\[([^\]]+)\]\(([^)\s]+)\)\)|\s*\[\[([^\]]+)\]\(([^)\s]+)\)\]')
def entry(line):
    urls = []
    def grab(m):
        urls.append(absurl(m.group(2) or m.group(4))); return ''
    t = LINK_GROUP.sub(grab, line).strip()
    t = re.sub(r'\s*\|\s*\(\[.*$', '', t)
    t = re.sub(r'\s+\|\s*$', '', t).strip()
    m = re.match(r'^(\d{4})(?:\d{4})?(\s*-\s*(?:\d{4}|actualidad)?\.?|-\d{4})?\s*\|?\s*(.*)$', t)
    if not m: return None
    y, rng, rest = m.groups()
    rng = (rng or '').strip().rstrip('.')
    year = y + ('–' + rng.lstrip('-').strip() if rng else '')
    if rng and not rng.lstrip('-').strip(): year = y + '–'
    rest = rest.lstrip('|. ').strip()
    rest = re.sub(r'\s{2,}', ' ', rest)
    body = esc(rest)
    if urls: body += f' [↗]({urls[0]}){{.cvf-link}}'
    return f'[{year}]{{.cvf-y}} {body}'

units = []  # (kind, markdown)
h2 = h3 = None
for raw in cv.splitlines():
    line = raw.strip()
    if not line: continue
    if line.startswith('# ') or line.startswith('## '):
        h2 = line.lstrip('# ').strip(); h3 = None
        if h2 in SKIP_H2: continue
        units.append(('h2', f'#### {h2} {{.cvf-h2}}')); continue
    if line.startswith('### '):
        h3 = line[4:].strip()
        if h2 in SKIP_H2 or h3 in SKIP_H3: continue
        units.append(('h3', f'##### {h3} {{.cvf-h3}}')); continue
    if h2 in SKIP_H2 or h3 in SKIP_H3: continue
    e = entry(line)
    if e: units.append(('e', e))
    else: print('SKIP', line[:70], file=sys.stderr)

units.insert(0, ('hdr', '## curriculum vitae {.cvf-title}\n\n[CV completo  en [misaa.cc/cv.html](https://misaa.cc/cv.html)]{.cvf-meta}'))

units.append(('end', '[CV completo, actualizado y con enlaces a registros: [misaa.cc/cv.html](https://misaa.cc/cv.html)]{.cvf-meta .cvf-end}'))

# --- medir alturas con el CSS real
tmp = pathlib.Path(tempfile.mkdtemp())
md = '\n\n'.join(f'::: {{.m data-i="{i}"}}\n{u}\n:::' for i, (_, u) in enumerate(units))
(tmp/'m.md').write_text(md)
frag = subprocess.run(['pandoc', str(tmp/'m.md'), '--from', 'markdown+native_divs', '--to', 'html5'], capture_output=True, text=True, check=True).stdout
css = (repo/'style.css').read_text()
COLW = sys.argv[3] if len(sys.argv) > 3 else '79mm'
html = f'''<!doctype html><meta charset=utf-8><link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet"><style>{css}
body{{padding:0!important}} .wrap{{width:{COLW}}} .m{{display:flow-root}}</style><div class="cvf-col wrap">{frag}</div>'''
(tmp/'m.html').write_text(html)
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.goto((tmp/'m.html').as_uri()); pg.wait_for_timeout(1500)
    hs = pg.evaluate('''() => [...document.querySelectorAll('.m')].map(d => d.getBoundingClientRect().height)''')
    b.close()
json.dump({'units': units, 'h': hs}, open(tmp.parent/'cv_units.json', 'w'))
print(len(units), 'units; total px', round(sum(hs)), file=sys.stderr)
print(tmp.parent/'cv_units.json')
