#!/usr/bin/env python3
"""紙娃娃風格包檢查程式 v2.0 2026-11-15
用法：python check_pack.py packs/<id>/pack.json
會檢查格式、顏色代號、安全性，並在同一個資料夾輸出 overview.svg（每個部件套在預設角色上的總覽圖）。
支援格式 1（只有半身、11 類）和格式 2（半身＋全身、17 類、表情、動作）。
只用 Python 標準函式庫，不用安裝任何東西。
"""
import json, re, sys, os
import xml.etree.ElementTree as ET

ORDER1 = ['face', 'hair', 'brow', 'eyes', 'mouth', 'nose', 'deco', 'glasses', 'hat', 'top', 'hand']
ORDER2 = ['face', 'hair', 'brow', 'eyes', 'mouth', 'nose', 'deco', 'glasses', 'hat', 'headset',
          'top', 'coat', 'bottom', 'shoes', 'hand', 'back', 'pet']
CAT_NAME = {'face': '臉型', 'hair': '髮型', 'brow': '眉毛', 'eyes': '眼睛', 'mouth': '嘴巴', 'nose': '鼻子',
            'deco': '臉部裝飾', 'glasses': '眼鏡', 'hat': '帽子頭飾', 'headset': '耳機麥克風', 'top': '上衣', 'coat': '外套',
            'bottom': '下身', 'shoes': '鞋子', 'hand': '手持物', 'back': '背後', 'pet': '夥伴'}
MUST_HAVE_DEFAULT = {'face', 'eyes', 'mouth', 'top', 'bottom'}   # 這幾類不能是空的
FIELDS = {'eyes': ['open', 'blink'], 'mouth': ['closed', 'open'], 'hair': ['front']}  # 其他類用 svg
OPTIONAL = {'hair': ['back'], 'back': ['front'], 'pet': ['half']}
TOKENS1 = {'skin', 'skin2', 'hair', 'hair2', 'eye', 'c1', 'c1d', 'c2', 'hat'}
TOKENS2 = TOKENS1 | {'acc', 'coat', 'coatd', 'pants', 'pantsd', 'shoe', 'back', 'backd', 'pet', 'petd'}
ALLOWED_TAGS = {'g', 'path', 'circle', 'ellipse', 'rect', 'line', 'polyline', 'polygon'}
BAD = [r'<\s*(script|image|text|foreignObject|use|a|style|iframe)', r'\bon\w+\s*=', r'href', r'url\s*\(', r'javascript:']
MIN1 = {'face': 3, 'hair': 6, 'brow': 3, 'eyes': 4, 'mouth': 4, 'nose': 2, 'deco': 3, 'glasses': 2, 'hat': 5, 'top': 6, 'hand': 3}
MIN2 = dict(MIN1, headset=2, coat=3, bottom=4, shoes=3, back=2, pet=2)
FULL = {'face': 4, 'hair': 24, 'brow': 6, 'eyes': 10, 'mouth': 7, 'nose': 4, 'deco': 8, 'glasses': 6, 'hat': 14, 'headset': 4,
        'top': 24, 'coat': 8, 'bottom': 12, 'shoes': 8, 'hand': 10, 'back': 6, 'pet': 6}
ARMS = ['L_down', 'L_wave', 'L_hip', 'L_thumb', 'R_down', 'R_hip', 'R_hold']
POSES = ['stand', 'wave', 'hips', 'thumb']
EXPRS = ['normal', 'happy', 'surprised', 'angry', 'cry', 'shy', 'love', 'sleepy', 'wink']

SAMPLE = {'skin': '#ffdcbf', 'skin2': '#e6c6ac', 'hair': '#3b2a24', 'hair2': '#2a1e1a', 'eye': '#2b2b33',
          'c1': '#23407a', 'c1d': '#1d3464', 'c2': '#e2553b', 'hat': '#e2553b', 'acc': '#2b2b33',
          'coat': '#2f9e5b', 'coatd': '#26814a', 'pants': '#3d5a8a', 'pantsd': '#324a71', 'shoe': '#e2553b',
          'back': '#ffc531', 'backd': '#d1a128', 'pet': '#f28c28', 'petd': '#c67321'}

errors, warns = [], []


def frag_ok(where, s, tokens, extra=()):
    if not isinstance(s, str) or not s.strip():
        errors.append(f'{where}：是空的'); return
    for pat in BAD:
        if re.search(pat, s, re.I):
            errors.append(f'{where}：含有不允許的內容（{pat}）')
    for t in set(re.findall(r'\{(\w+)\}', s)):
        if t not in tokens and t not in extra:
            errors.append(f'{where}：未知的顏色代號 {{{t}}}')
    try:
        root = ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg">' + s + '</svg>')
        for el in root.iter():
            tag = el.tag.split('}')[-1]
            if el is not root and tag not in ALLOWED_TAGS:
                errors.append(f'{where}：不允許的標籤 <{tag}>')
    except ET.ParseError as e:
        errors.append(f'{where}：SVG 寫錯了（{e}）')


def compose(p, sel, pose=None, mode='full'):
    """和網頁 inner() 一樣的組合順序"""
    pose = pose or {}
    cats = p['cats']
    fmt = p.get('format', 1)

    def opt(c):
        if c not in cats:
            return None
        return next((o for o in cats[c]['opts'] if o['id'] == sel.get(c)), None)
    g = lambda c, f='svg': (opt(c) or {}).get(f, '')
    hair, eyes, mouth = opt('hair'), opt('eyes'), opt('mouth')
    base = p['base']
    if fmt < 2:
        parts = [(hair or {}).get('back', ''), g('top'), base.get('neck', ''), base.get('ears', ''), g('face'), g('deco'),
                 (mouth or {}).get('open' if pose.get('mouth') == 'open' else 'closed', ''), g('nose'),
                 (eyes or {}).get('blink' if pose.get('eyes') == 'blink' else 'open', ''),
                 g('brow'), (hair or {}).get('front', ''), g('glasses'), g('hat'), g('hand')]
    else:
        E = p.get('expr', {}).get(sel.get('expr', 'normal'), {})
        eyeset = E.get('eyes') or eyes or {}
        mouthset = E.get('mouth') or mouth or {}
        brow = (E['brow'] if 'brow' in E else g('brow')) if sel.get('brow') else ''
        P = p['poses'].get(sel.get('pose', 'stand')) or p['poses']['stand']
        top, coat = opt('top') or {}, opt('coat') or {}
        sleeve = coat.get('sleeve') if coat and coat.get('sleeve', {}).get('type', 'none') != 'none' else top.get('sleeve', {'type': 'none'})
        sleeve = sleeve or {'type': 'none'}
        A = base['arms']
        ids = [P['L'], 'R_hold' if sel.get('hand') else P['R']]

        def arm(i):
            a = A[i]
            t = sleeve.get('type')
            return (a['skin'] + (a.get(t, '') if t in ('long', 'short') else '')).replace('{sleeve}', sleeve.get('fill', '{c1}'))
        pet = opt('pet') or {}
        parts = [g('back'), (hair or {}).get('back', ''), base.get('legs', ''), g('shoes'), g('bottom'), g('top'), g('coat'), g('back', 'front'),
                 arm(ids[0]), arm(ids[1]), base.get('neck', ''), base.get('ears', ''), g('face'), g('deco'),
                 mouthset.get('open' if pose.get('mouth') == 'open' else 'closed', ''), g('nose'),
                 eyeset.get('blink' if pose.get('eyes') == 'blink' else 'open', ''),
                 (hair or {}).get('front', ''), brow, E.get('over', ''), g('glasses'), g('hat'), g('headset'), g('hand'),
                 A[ids[0]]['hand'] + A[ids[1]]['hand'], pet.get('half', '') if mode == 'half' else pet.get('svg', '')]
    return re.sub(r'\{(\w+)\}', lambda m: SAMPLE.get(m.group(1), m.group(0)), ''.join(parts))


def main(path):
    p = json.load(open(path, encoding='utf-8'))
    for k in ['id', 'name', 'version', 'date', 'base', 'defaults', 'cats']:
        if k not in p:
            errors.append(f'缺少欄位 {k}')
    if errors:
        return report(path, p)
    fmt = p.get('format', 1)
    if fmt not in (1, 2):
        errors.append('format 只能是 1 或 2')
        return report(path, p)
    order, tokens, mins = (ORDER2, TOKENS2, MIN2) if fmt == 2 else (ORDER1, TOKENS1, MIN1)
    if not re.fullmatch(r'[a-z0-9-]+', str(p['id'])):
        errors.append('id 只能用小寫英文、數字、減號')
    for k in ['neck', 'ears'] + (['legs'] if fmt == 2 else []):
        if p['base'].get(k):
            frag_ok(f'base.{k}', p['base'][k], tokens)
        elif fmt == 2:
            errors.append(f'缺少 base.{k}')
    if fmt == 2:
        A = p['base'].get('arms', {})
        for a in ARMS:
            if a not in A:
                errors.append(f'缺少手臂 base.arms.{a}'); continue
            for f in ('skin', 'long', 'short', 'hand'):
                frag_ok(f'手臂 {a}.{f}', A[a].get(f), tokens, ('sleeve',))
        for k in POSES:
            P = p.get('poses', {}).get(k)
            if not P or P.get('L') not in A or P.get('R') not in A or not P.get('name'):
                errors.append(f'動作 {k} 缺少或寫錯（要有 name、L、R）')
        for k in EXPRS:
            E = p.get('expr', {}).get(k)
            if not E or not E.get('name'):
                errors.append(f'表情 {k} 缺少或沒有 name'); continue
            if 'eyes' in E:
                for f in ('open', 'blink'):
                    frag_ok(f'表情 {k}.eyes.{f}', E['eyes'].get(f), tokens)
            if 'mouth' in E:
                for f in ('closed', 'open'):
                    frag_ok(f'表情 {k}.mouth.{f}', E['mouth'].get(f), tokens)
            for f in ('brow', 'over'):
                if f in E:
                    frag_ok(f'表情 {k}.{f}', E[f], tokens)
    total = 0
    for c in order:
        C = p['cats'].get(c)
        if not C:
            errors.append(f'缺少分類 {c}（{CAT_NAME[c]}）'); continue
        opts = C.get('opts', [])
        total += len(opts)
        if len(opts) < mins[c]:
            warns.append(f'{CAT_NAME[c]} 只有 {len(opts)} 款，建議至少 {mins[c]} 款')
        elif fmt == 2 and len(opts) < FULL[c]:
            warns.append(f'{CAT_NAME[c]} {len(opts)} 款，完整包是 {FULL[c]} 款')
        ids = [o.get('id') for o in opts]
        if len(ids) != len(set(ids)):
            errors.append(f'{CAT_NAME[c]}：編號重複')
        for o in opts:
            where = f"{CAT_NAME[c]} {o.get('id')}（{o.get('name')}）"
            if not o.get('name'):
                errors.append(f'{where}：沒有中文名稱')
            for f in FIELDS.get(c, ['svg']):
                frag_ok(f'{where}.{f}', o.get(f), tokens)
            for f in OPTIONAL.get(c, []):
                if o.get(f):
                    frag_ok(f'{where}.{f}', o[f], tokens)
            if fmt == 2 and c in ('top', 'coat'):
                sl = o.get('sleeve')
                if not isinstance(sl, dict) or sl.get('type') not in ('long', 'short', 'none') or not isinstance(sl.get('fill', ''), str):
                    errors.append(f'{where}：sleeve 要寫成 {{"type":"long|short|none","fill":"{{c1}}"}}')
        d = p['defaults'].get(c, '')
        if d == '' and c in MUST_HAVE_DEFAULT:
            errors.append(f'預設角色的{CAT_NAME[c]}不能是空的')
        if d and d not in ids:
            errors.append(f'預設角色的{CAT_NAME[c]} {d} 不存在')
        if d == '' and not C.get('none'):
            errors.append(f'{CAT_NAME[c]} 沒有開放「不要」，預設不能是空的')
    if not errors:
        overview(path, p, order)
    return report(path, p, total)


def overview(path, p, order):
    fmt = p.get('format', 1)
    H = 1400 if fmt == 2 else 1000
    cell, label, cols = 200, 34, 8
    out = []
    y = 0

    def head(t):
        nonlocal y
        out.append(f'<text x="10" y="{y + 26}" font-size="22" font-weight="700" fill="#333">{t}</text>')
        y += 36

    def tile(i, sel, name, view='0 0 1000 1000', pose=None, small=None):
        x, yy = (i % cols) * cell, y + (i // cols) * (cell + label)
        out.append(f'<rect x="{x + 4}" y="{yy}" width="{cell - 8}" height="{cell - 8}" rx="14" fill="#f3f0fa"/>'
                   f'<svg x="{x + 4}" y="{yy}" width="{cell - 8}" height="{cell - 8}" viewBox="{view}">{compose(p, sel, pose)}</svg>'
                   f'<text x="{x + cell / 2}" y="{yy + cell + 18}" text-anchor="middle" font-size="18" fill="#444">{name}</text>')
        if small:
            v, ps = small
            out.append(f'<svg x="{x + cell - 74}" y="{yy + 6}" width="66" height="66" viewBox="{v}">'
                       f'<rect x="-500" y="-500" width="3000" height="3000" fill="#fff"/>{compose(p, sel, ps)}</svg>')

    def end(n):
        nonlocal y
        y += ((n - 1) // cols + 1) * (cell + label) + 10

    V = p.get('view', {})
    for c in order:
        opts = p['cats'][c]['opts']
        head(f'{CAT_NAME[c]}（{len(opts)}）')
        for i, o in enumerate(opts):
            sel = dict(p['defaults'], expr='normal', pose='stand'); sel[c] = o['id']
            if fmt == 2:
                v = V.get(c, '0 0 1000 1400')
                v = {'top': '150 560 700 700', 'coat': '150 560 700 700', 'hand': '200 300 760 760', 'back': '0 400 1000 1000',
                     'bottom': '0 400 1000 1000', 'shoes': '200 900 600 600', 'pet': '450 900 550 550', 'hair': '60 0 880 880', 'hat': '60 0 880 880'}.get(c, v)
            else:
                v = '0 0 1000 1000'
            small = None
            if c in ('eyes', 'mouth'):
                small = ('250 220 500 500', {'eyes': 'blink'} if c == 'eyes' else {'mouth': 'open'})
            tile(i, sel, f'{o["id"]} {o["name"]}', v, None, small)
        end(len(opts))
    if fmt == 2:
        head('表情（右上小圖是張嘴）')
        for i, (k, E) in enumerate(p['expr'].items()):
            sel = dict(p['defaults'], expr=k, pose='stand')
            tile(i, sel, f'{k} {E["name"]}', '200 120 600 600', None, ('250 220 500 500', {'mouth': 'open'}))
        end(len(p['expr']))
        head('動作（第二排：拿東西＋穿外套）')
        items = list(p['poses'].items())
        for i, (k, P) in enumerate(items):
            tile(i, dict(p['defaults'], expr='normal', pose=k), f'{k} {P["name"]}', '0 0 1000 1400')
        hand1 = p['cats']['hand']['opts'][0]['id']
        coat1 = p['cats']['coat']['opts'][0]['id']
        for i, (k, P) in enumerate(items):
            tile(i + len(items), dict(p['defaults'], expr='happy', pose=k, hand=hand1, coat=coat1), f'{k}＋{hand1}＋{coat1}', '0 0 1000 1400')
        end(len(items) * 2)
        head('半身（裁上方 1000×1000）')
        tile(0, dict(p['defaults'], expr='normal', pose='stand', pet=p['cats']['pet']['opts'][0]['id']), '半身＋夥伴', '0 0 1000 1000')
        end(1)
    W = cols * cell
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{y}" viewBox="0 0 {W} {y}" '
           f'font-family="Noto Sans TC, Microsoft JhengHei, sans-serif"><rect width="{W}" height="{y}" fill="#fff"/>' + ''.join(out) + '</svg>')
    open(os.path.join(os.path.dirname(path), 'overview.svg'), 'w', encoding='utf-8').write(svg)


def report(path, p, total=0):
    print(f'風格包：{p.get("name")}（{p.get("id")}，格式 {p.get("format", 1)}） 部件 {total} 個')
    for w in warns:
        print('  提醒：' + w)
    for e in errors:
        print('  錯誤：' + e)
    print('結果：' + ('通過，已輸出 overview.svg' if not errors else f'沒通過，共 {len(errors)} 個錯誤'))
    return 0 if not errors else 1


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(2)
    sys.exit(main(sys.argv[1]))
