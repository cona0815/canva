#!/usr/bin/env python3
"""產生示範風格包「Q 版描邊風」v1.0 2026-11-15：大頭小身體＋深色描邊，眼睛和嘴巴重新畫。"""
import json, sys, copy

flat = json.load(open(sys.argv[1], encoding='utf-8'))
out_path = sys.argv[2]

OUT = '#3b2b3f'
HEAD = 'translate(500 410) scale(1.3) translate(-500 440)'.replace('translate(-500 440)', 'translate(-500 -440)')
BODY = 'translate(500 1000) scale(0.74) translate(-500 -1000)'
STROKE = f'stroke="{OUT}" stroke-width="9" stroke-linejoin="round"'
HEAD_CATS = {'face', 'hair', 'brow', 'eyes', 'mouth', 'nose', 'deco', 'glasses', 'hat'}
NO_OUTLINE = {'deco', 'brow', 'mouth', 'eyes'}


def wrap(cat, s):
    if not s:
        return s
    t = HEAD if cat in HEAD_CATS else BODY
    line = '' if cat in NO_OUTLINE else ' ' + STROKE
    return f'<g transform="{t}"{line}>{s}</g>'


EL, ER, EY = 410, 590, 412
both = lambda f: f(EL) + f(ER)
BLINK = both(lambda x: f'<path d="M{x-40} {EY} Q{x} {EY+30} {x+40} {EY}" stroke="{OUT}" stroke-width="13" fill="none" stroke-linecap="round"/>')
EYES = [
    ('e1', '水汪汪大眼', both(lambda x: f'<ellipse cx="{x}" cy="{EY}" rx="42" ry="54" fill="{OUT}"/><ellipse cx="{x}" cy="{EY+14}" rx="30" ry="34" fill="{{eye}}"/>'
                          f'<circle cx="{x+14}" cy="{EY-20}" r="15" fill="#fff"/><circle cx="{x-14}" cy="{EY+24}" r="8" fill="#fff"/>')),
    ('e2', '星星眼', both(lambda x: f'<ellipse cx="{x}" cy="{EY}" rx="42" ry="52" fill="{OUT}"/>'
                       f'<path d="M{x} {EY-30} l9 20 22 3 -16 15 4 22 -19 -11 -19 11 4 -22 -16 -15 22 -3 Z" fill="#ffd84d"/>')),
    ('e3', '瞇瞇笑眼', both(lambda x: f'<path d="M{x-40} {EY+12} Q{x} {EY-34} {x+40} {EY+12}" stroke="{OUT}" stroke-width="14" fill="none" stroke-linecap="round"/>')),
    ('e4', '愛心眼', both(lambda x: f'<path d="M{x} {EY+36} C{x-60} {EY-4} {x-36} {EY-52} {x} {EY-18} C{x+36} {EY-52} {x+60} {EY-4} {x} {EY+36} Z" fill="#ff5c8a" stroke="{OUT}" stroke-width="8"/>')),
    ('e5', '酷酷半眼', both(lambda x: f'<ellipse cx="{x}" cy="{EY+6}" rx="40" ry="36" fill="{OUT}"/><circle cx="{x+6}" cy="{EY+14}" r="18" fill="{{eye}}"/>'
                         f'<rect x="{x-46}" y="{EY-36}" width="92" height="30" fill="{{skin}}"/><path d="M{x-44} {EY-6} L{x+44} {EY-6}" stroke="{OUT}" stroke-width="12" stroke-linecap="round"/>')),
    ('e6', '漩渦眼', both(lambda x: f'<circle cx="{x}" cy="{EY}" r="40" fill="#fff" stroke="{OUT}" stroke-width="9"/>'
                       f'<path d="M{x} {EY} m-4 0 a4 4 0 1 1 8 0 a10 10 0 1 1 -20 0 a16 16 0 1 1 32 0 a22 22 0 1 1 -44 0" stroke="{OUT}" stroke-width="6" fill="none"/>')),
]
MY = 548
MOUTHS = [
    ('m1', '開心笑', f'<path d="M462 {MY} Q500 {MY+34} 538 {MY}" stroke="{OUT}" stroke-width="12" fill="none" stroke-linecap="round"/>',
     f'<path d="M456 {MY-6} Q500 {MY+70} 544 {MY-6} Z" fill="#7a1f2b" stroke="{OUT}" stroke-width="8" stroke-linejoin="round"/><path d="M478 {MY+30} Q500 {MY+46} 522 {MY+30} Q500 {MY+18} 478 {MY+30} Z" fill="#ff8a8a"/>'),
    ('m2', 'ω 嘴', f'<path d="M462 {MY} Q481 {MY+26} 500 {MY} Q519 {MY+26} 538 {MY}" stroke="{OUT}" stroke-width="11" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
     f'<path d="M462 {MY} Q481 {MY+26} 500 {MY} Q519 {MY+26} 538 {MY}" stroke="{OUT}" stroke-width="11" fill="none" stroke-linecap="round"/><ellipse cx="500" cy="{MY+34}" rx="20" ry="18" fill="#7a1f2b" stroke="{OUT}" stroke-width="7"/>'),
    ('m3', '小虎牙', f'<path d="M462 {MY} Q500 {MY+28} 538 {MY}" stroke="{OUT}" stroke-width="12" fill="none" stroke-linecap="round"/><path d="M516 {MY+10} l8 16 8 -18 Z" fill="#fff" stroke="{OUT}" stroke-width="4"/>',
     f'<path d="M456 {MY-6} Q500 {MY+64} 544 {MY-6} Z" fill="#7a1f2b" stroke="{OUT}" stroke-width="8"/><path d="M516 {MY-2} l8 18 8 -20 Z" fill="#fff"/>'),
    ('m4', '吐舌頭', f'<path d="M466 {MY} Q500 {MY+20} 534 {MY}" stroke="{OUT}" stroke-width="12" fill="none" stroke-linecap="round"/><path d="M500 {MY+10} q-18 0 -18 22 q0 18 18 18 q18 0 18 -18 q0 -22 -18 -22" fill="#ff7a9a" stroke="{OUT}" stroke-width="7"/>',
     f'<ellipse cx="500" cy="{MY+16}" rx="36" ry="30" fill="#7a1f2b" stroke="{OUT}" stroke-width="8"/><path d="M500 {MY+18} q-20 0 -20 24 q0 20 20 20 q20 0 20 -20 q0 -24 -20 -24" fill="#ff7a9a" stroke="{OUT}" stroke-width="6"/>'),
    ('m5', '驚訝 O 嘴', f'<ellipse cx="500" cy="{MY+12}" rx="16" ry="20" fill="#7a1f2b" stroke="{OUT}" stroke-width="8"/>',
     f'<ellipse cx="500" cy="{MY+14}" rx="26" ry="32" fill="#7a1f2b" stroke="{OUT}" stroke-width="8"/>'),
]

cats = copy.deepcopy(flat['cats'])
for c, C in cats.items():
    for o in C['opts']:
        for f in ('svg', 'front', 'back'):
            if f in o:
                o[f] = wrap(c, o[f])
cats['eyes']['opts'] = [{'id': i, 'name': n, 'open': wrap('eyes', s), 'blink': wrap('eyes', BLINK)} for i, n, s in EYES]
cats['mouth']['opts'] = [{'id': i, 'name': n, 'closed': wrap('mouth', a), 'open': wrap('mouth', b)} for i, n, a, b in MOUTHS]
# 腮紅改成 Q 版斜線腮紅
for o in cats['deco']['opts']:
    if o['id'] == 'd1':
        o['svg'] = wrap('deco', '<ellipse cx="350" cy="492" rx="40" ry="22" fill="#ff8fa8" opacity=".55"/><ellipse cx="650" cy="492" rx="40" ry="22" fill="#ff8fa8" opacity=".55"/>'
                        f'<path d="M330 492 l12 -14 M350 494 l12 -14 M630 492 l12 -14 M650 494 l12 -14" stroke="{OUT}" stroke-width="5" stroke-linecap="round" opacity=".6"/>')

base = {'neck': wrap('top', flat['base']['neck']), 'ears': wrap('face', flat['base']['ears'])}
VIEW = {k: '120 20 760 760' for k in ['face', 'hair', 'brow', 'eyes', 'mouth', 'nose', 'deco', 'glasses']}
VIEW.update({'eyes': '230 210 540 540', 'mouth': '230 330 540 540', 'brow': '230 170 540 540', 'nose': '230 300 540 540', 'hat': '80 -60 840 840'})
pack = {'id': 'chibi', 'name': 'Q 版描邊風', 'version': '1.0', 'date': '2026-11-15', 'author': 'Claude（示範）',
        'base': base, 'defaults': dict(flat['defaults']), 'view': VIEW, 'cats': cats}
json.dump(pack, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False)
print('ok', sum(len(C['opts']) for C in cats.values()))
