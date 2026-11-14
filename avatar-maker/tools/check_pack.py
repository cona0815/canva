#!/usr/bin/env python3
"""紙娃娃風格包檢查程式 v1.0 2026-11-15
用法：python check_pack.py packs/<id>/pack.json
會檢查格式、顏色代號、安全性，並在同一個資料夾輸出 overview.svg（每個部件套在預設角色上的總覽圖）。
只用 Python 標準函式庫，不用安裝任何東西。
"""
import json, re, sys, os
import xml.etree.ElementTree as ET

ORDER = ['face', 'hair', 'brow', 'eyes', 'mouth', 'nose', 'deco', 'glasses', 'hat', 'top', 'hand']
CAT_NAME = {'face': '臉型', 'hair': '髮型', 'brow': '眉毛', 'eyes': '眼睛', 'mouth': '嘴巴', 'nose': '鼻子',
            'deco': '臉部裝飾', 'glasses': '眼鏡', 'hat': '帽子頭飾', 'top': '上衣', 'hand': '手持物'}
MUST_HAVE_DEFAULT = {'face', 'eyes', 'mouth', 'top'}          # 這幾類不能是空的
FIELDS = {'eyes': ['open', 'blink'], 'mouth': ['closed', 'open'], 'hair': ['front']}  # 其他類用 svg
TOKENS = {'skin', 'skin2', 'hair', 'hair2', 'eye', 'c1', 'c1d', 'c2', 'hat'}
ALLOWED_TAGS = {'g', 'path', 'circle', 'ellipse', 'rect', 'line', 'polyline', 'polygon'}
BAD = [r'<\s*(script|image|text|foreignObject|use|a|style|iframe)', r'\bon\w+\s*=', r'href', r'url\s*\(', r'javascript:']
MIN_OPTS = {'face': 3, 'hair': 6, 'brow': 3, 'eyes': 4, 'mouth': 4, 'nose': 2, 'deco': 3, 'glasses': 2, 'hat': 5, 'top': 6, 'hand': 3}

SAMPLE = {'skin': '#ffdcbf', 'skin2': '#e6c6ac', 'hair': '#3b2a24', 'hair2': '#2a1e1a', 'eye': '#2b2b33',
          'c1': '#23407a', 'c1d': '#1d3464', 'c2': '#e2553b', 'hat': '#e2553b'}

errors, warns = [], []


def frag_ok(where, s):
    if not isinstance(s, str) or not s.strip():
        errors.append(f'{where}：是空的'); return
    for pat in BAD:
        if re.search(pat, s, re.I):
            errors.append(f'{where}：含有不允許的內容（{pat}）')
    for t in set(re.findall(r'\{(\w+)\}', s)):
        if t not in TOKENS:
            errors.append(f'{where}：未知的顏色代號 {{{t}}}')
    try:
        root = ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg">' + s + '</svg>')
        for el in root.iter():
            tag = el.tag.split('}')[-1]
            if el is not root and tag not in ALLOWED_TAGS:
                errors.append(f'{where}：不允許的標籤 <{tag}>')
    except ET.ParseError as e:
        errors.append(f'{where}：SVG 寫錯了（{e}）')


def compose(p, sel, pose=None):
    """和網頁 inner() 一樣的組合順序"""
    pose = pose or {}
    cats = p['cats']
    def opt(c):
        return next((o for o in cats[c]['opts'] if o['id'] == sel.get(c)), None)
    g = lambda c: (opt(c) or {}).get('svg', '')
    hair, eyes, mouth = opt('hair'), opt('eyes'), opt('mouth')
    parts = [(hair or {}).get('back', ''), g('top'), p['base'].get('neck', ''), p['base'].get('ears', ''),
             g('face'), g('deco'),
             (mouth or {}).get('open' if pose.get('mouth') == 'open' else 'closed', ''),
             g('nose'),
             (eyes or {}).get('blink' if pose.get('eyes') == 'blink' else 'open', ''),
             g('brow'), (hair or {}).get('front', ''), g('glasses'), g('hat'), g('hand')]
    return re.sub(r'\{(\w+)\}', lambda m: SAMPLE.get(m.group(1), m.group(0)), ''.join(parts))


def main(path):
    p = json.load(open(path, encoding='utf-8'))
    for k in ['id', 'name', 'version', 'date', 'base', 'defaults', 'cats']:
        if k not in p:
            errors.append(f'缺少欄位 {k}')
    if errors:
        return report(path, p)
    if not re.fullmatch(r'[a-z0-9-]+', str(p['id'])):
        errors.append('id 只能用小寫英文、數字、減號')
    for k in ['neck', 'ears']:
        if k in p['base'] and p['base'][k]:
            frag_ok(f'base.{k}', p['base'][k])
    total = 0
    for c in ORDER:
        C = p['cats'].get(c)
        if not C:
            errors.append(f'缺少分類 {c}（{CAT_NAME[c]}）'); continue
        opts = C.get('opts', [])
        total += len(opts)
        if len(opts) < MIN_OPTS[c]:
            warns.append(f'{CAT_NAME[c]} 只有 {len(opts)} 款，建議至少 {MIN_OPTS[c]} 款')
        ids = [o.get('id') for o in opts]
        if len(ids) != len(set(ids)):
            errors.append(f'{CAT_NAME[c]}：編號重複')
        for o in opts:
            where = f"{CAT_NAME[c]} {o.get('id')}（{o.get('name')}）"
            if not o.get('name'):
                errors.append(f'{where}：沒有中文名稱')
            for f in FIELDS.get(c, ['svg']):
                frag_ok(f'{where}.{f}', o.get(f))
            if c == 'hair' and o.get('back'):
                frag_ok(f'{where}.back', o['back'])
        d = p['defaults'].get(c, '')
        if d == '' and c in MUST_HAVE_DEFAULT:
            errors.append(f'預設角色的{CAT_NAME[c]}不能是空的')
        if d and d not in ids:
            errors.append(f'預設角色的{CAT_NAME[c]} {d} 不存在')
        if d == '' and not C.get('none'):
            errors.append(f'{CAT_NAME[c]} 沒有開放「不要」，預設不能是空的')
    if not errors:
        overview(path, p)
    return report(path, p, total)


def overview(path, p):
    cell, label = 200, 34
    rows = [(c, o) for c in ORDER for o in p['cats'][c]['opts']]
    cols = 8
    out = []
    y = 0
    for c in ORDER:
        opts = p['cats'][c]['opts']
        out.append(f'<text x="10" y="{y + 26}" font-size="22" font-weight="700" fill="#333">{CAT_NAME[c]}（{len(opts)}）</text>')
        y += 36
        for i, o in enumerate(opts):
            x, yy = (i % cols) * cell, y + (i // cols) * (cell + label)
            sel = dict(p['defaults']); sel[c] = o['id']
            out.append(f'<rect x="{x + 4}" y="{yy}" width="{cell - 8}" height="{cell - 8}" rx="14" fill="#f3f0fa"/>'
                       f'<svg x="{x + 4}" y="{yy}" width="{cell - 8}" height="{cell - 8}" viewBox="0 0 1000 1000">{compose(p, sel)}</svg>'
                       f'<text x="{x + cell / 2}" y="{yy + cell + 18}" text-anchor="middle" font-size="18" fill="#444">{o["id"]} {o["name"]}</text>')
            if c in ('eyes', 'mouth'):
                pose = {'eyes': 'blink'} if c == 'eyes' else {'mouth': 'open'}
                out.append(f'<svg x="{x + cell - 74}" y="{yy + 6}" width="66" height="66" viewBox="250 220 500 500">'
                           f'<rect x="250" y="220" width="500" height="500" fill="#fff"/>{compose(p, sel, pose)}</svg>')
        y += ((len(opts) - 1) // cols + 1) * (cell + label) + 10
    W = cols * cell
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{y}" viewBox="0 0 {W} {y}" '
           f'font-family="Noto Sans TC, Microsoft JhengHei, sans-serif"><rect width="{W}" height="{y}" fill="#fff"/>' + ''.join(out) + '</svg>')
    open(os.path.join(os.path.dirname(path), 'overview.svg'), 'w', encoding='utf-8').write(svg)


def report(path, p, total=0):
    print(f'風格包：{p.get("name")}（{p.get("id")}） 部件 {total} 個')
    for w in warns:
        print('  提醒：' + w)
    for e in errors:
        print('  錯誤：' + e)
    print('結果：' + ('通過，已輸出 overview.svg' if not errors else f'沒通過，共 {len(errors)} 個錯誤'))
    return 0 if not errors else 1


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(2)
    sys.exit(main(sys.argv[1]))
