import json, sys, re
data = json.load(open(sys.argv[1])); target = sys.argv[2]
units, hs = data['units'], data['h']
H = 184.6 * 3.7795 - 6   # alto útil de columna en px (margen de seguridad)
cols, cur, ch = [], [], 0
i = 0
while i < len(units):
    kind, md = units[i]; h = hs[i]
    need = h
    if kind in ('h2', 'h3'):   # no dejar títulos huérfanos
        j = i + 1; need = h
        while j < len(units) and units[j][0] in ('h2', 'h3'): need += hs[j]; j += 1
        if j < len(units): need += hs[j]
    if cur and ch + need > H:
        cols.append(cur); cur, ch = [], 0
    cur.append(md); ch += h; i += 1
cols.append(cur)
pages = [cols[k:k+3] for k in range(0, len(cols), 3)]
out = ['<!-- ============================================================',
       '     ANID 2027 · CV CONDENSADO — generado desde misaa.cc/cv.md',
       '     (sin docencia, residencias ni prensa). Versión completa: https://misaa.cc/cv.html',
       '     ============================================================ -->']
for pcols in pages:
    out.append('::: {.cvfull}')
    for c in pcols:
        out.append('::: {.cvf-col}'); out.append('\n\n'.join(c)); out.append(':::\n')
    out.append(':::\n')
block = '\n'.join(out) + '\n<!-- FIN CV CONDENSADO -->\n\n'
s = open(target).read()
s = re.sub(r'<!-- =+\n     ANID 2027 · CV CONDENSADO.*?<!-- FIN CV CONDENSADO -->\n\n', '', s, flags=re.S)
anchor = '<!-- ============================================================\n     PÁGINA DE CIERRE'
assert anchor in s
s = s.replace(anchor, block + anchor, 1)
open(target, 'w').write(s)
print(len(cols), 'columns,', len(pages), 'pages')
