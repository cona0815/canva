#!/usr/bin/env python3
"""產生風格包「Q 版描邊風」（格式 2）v2.0 2026-11-15
用法：python tools/make_chibi.py packs/chibi/pack.json
做法：拿扁平圓潤風（make_flat.py）的全部部件，頭放大 1.12 倍、身體縮成 0.85 倍並往上提，加深色描邊；眼睛和嘴巴換成 Q 版專用的。
v1.0 的眼睛 e1～e6、嘴巴 m1～m5 編號不變，舊的角色代碼還能還原。
"""
import json, sys, copy, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_flat as F

OUT = '#3b2b3f'
HEAD = 'translate(500 685) scale(1.12) translate(-500 -650)'
BODY = 'translate(500 1336) scale(.85) translate(-500 -1396)'   # 身體縮小並往上提，半身時肩膀和上衣都看得到
STROKE = f' stroke="{OUT}" stroke-width="9" stroke-linejoin="round"'
HEAD_CATS = {'face', 'hair', 'brow', 'eyes', 'mouth', 'nose', 'deco', 'glasses', 'hat', 'headset'}
NO_OUTLINE = {'deco', 'brow', 'mouth', 'eyes'}


def wrap(s, head, line=True):
    if not s:
        return s
    return f'<g transform="{HEAD if head else BODY}"{STROKE if line else ""}>{s}</g>'


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
    ('e7', '圓滾滾眼', both(lambda x: f'<circle cx="{x}" cy="{EY}" r="34" fill="{OUT}"/><circle cx="{x}" cy="{EY+4}" r="24" fill="{{eye}}"/><circle cx="{x+12}" cy="{EY-12}" r="11" fill="#fff"/>')),
    ('e8', '亮晶晶眼', both(lambda x: f'<ellipse cx="{x}" cy="{EY}" rx="40" ry="50" fill="{OUT}"/><ellipse cx="{x}" cy="{EY+10}" rx="30" ry="34" fill="{{eye}}"/>'
                         f'<ellipse cx="{x}" cy="{EY+26}" rx="24" ry="12" fill="#fff" opacity=".35"/><circle cx="{x-12}" cy="{EY-16}" r="13" fill="#fff"/><circle cx="{x+16}" cy="{EY-6}" r="7" fill="#fff"/>')),
    ('e9', '貓咪眼', both(lambda x: f'<path d="M{x-44} {EY+6} Q{x-6} {EY-44} {x+44} {EY-10} Q{x+6} {EY+40} {x-44} {EY+6} Z" fill="#fff" stroke="{OUT}" stroke-width="9"/>'
                       f'<circle cx="{x}" cy="{EY-2}" r="22" fill="{{eye}}"/><ellipse cx="{x}" cy="{EY-2}" rx="6" ry="17" fill="{OUT}"/><circle cx="{x+8}" cy="{EY-12}" r="6" fill="#fff"/>')),
    ('e10', '豆豆眼', both(lambda x: f'<ellipse cx="{x}" cy="{EY}" rx="16" ry="22" fill="{OUT}"/><circle cx="{x+5}" cy="{EY-7}" r="5" fill="#fff"/>')),
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
    ('m6', '大大笑', f'<path d="M448 {MY-8} Q500 {MY+56} 552 {MY-8} Z" fill="#7a1f2b" stroke="{OUT}" stroke-width="8" stroke-linejoin="round"/><path d="M460 {MY-6} L540 {MY-6} L534 {MY+8} L466 {MY+8} Z" fill="#fff"/>',
     f'<path d="M444 {MY-12} Q500 {MY+90} 556 {MY-12} Z" fill="#7a1f2b" stroke="{OUT}" stroke-width="8" stroke-linejoin="round"/><path d="M458 {MY-10} L542 {MY-10} L536 {MY+6} L464 {MY+6} Z" fill="#fff"/><path d="M474 {MY+44} Q500 {MY+64} 526 {MY+44} Q500 {MY+30} 474 {MY+44} Z" fill="#ff8a8a"/>'),
    ('m7', '小小嘴', f'<path d="M488 {MY+4} L512 {MY+4}" stroke="{OUT}" stroke-width="10" stroke-linecap="round"/>',
     f'<ellipse cx="500" cy="{MY+10}" rx="14" ry="18" fill="#7a1f2b" stroke="{OUT}" stroke-width="7"/>'),
]


def main(out_path):
    flat = F.build()
    cats = copy.deepcopy(flat['cats'])
    for c, C in cats.items():
        head = c in HEAD_CATS
        for o in C['opts']:
            for f in ('svg', 'front', 'back'):
                if f in o and not (c == 'pet' and f == 'svg' and False):
                    o[f] = wrap(o[f], head, c not in NO_OUTLINE)
            if c == 'pet' and 'half' in o:
                o['half'] = f'<g{STROKE}>{o["half"]}</g>'
    cats['eyes']['opts'] = [{'id': i, 'name': n, 'open': wrap(s, True, False), 'blink': wrap(BLINK, True, False)} for i, n, s in EYES]
    cats['mouth']['opts'] = [{'id': i, 'name': n, 'closed': wrap(a, True, False), 'open': wrap(b, True, False)} for i, n, a, b in MOUTHS]
    for o in cats['deco']['opts']:
        if o['id'] == 'd1':
            o['svg'] = wrap('<ellipse cx="350" cy="492" rx="40" ry="22" fill="#ff8fa8" opacity=".55"/><ellipse cx="650" cy="492" rx="40" ry="22" fill="#ff8fa8" opacity=".55"/>'
                            f'<path d="M330 492 l12 -14 M350 494 l12 -14 M630 492 l12 -14 M650 494 l12 -14" stroke="{OUT}" stroke-width="5" stroke-linecap="round" opacity=".6"/>', True, False)
    expr = copy.deepcopy(flat['expr'])
    for k, E in expr.items():
        for f in ('eyes', 'mouth'):
            if f in E:
                E[f] = {s: wrap(v, True, False) for s, v in E[f].items()}
        for f in ('brow', 'over'):
            if f in E:
                E[f] = wrap(E[f], True, False)
    arms = {k: {f: (wrap(v, False, f == 'hand') if f != 'hand' else f'<g transform="{BODY}">{v}</g>') for f, v in a.items()} for k, a in F.arms(OUT).items()}
    base = {'neck': wrap(flat['base']['neck'], False), 'ears': wrap(flat['base']['ears'], True), 'legs': wrap(flat['base']['legs'], False), 'arms': arms}
    view = dict(flat['view'])
    view.update({'face': '200 140 600 600', 'hair': '80 -10 840 840', 'hat': '60 -40 880 880', 'headset': '120 20 760 760', 'brow': '260 200 480 480',
                 'eyes': '270 188 460 460', 'mouth': '320 401 340 340', 'nose': '340 323 320 320', 'deco': '230 250 540 540', 'glasses': '230 140 540 540',
                 'expr': '220 140 560 560', 'top': '230 700 540 540', 'coat': '230 700 540 540', 'bottom': '250 930 480 480', 'shoes': '330 1130 340 340',
                 'hand': '300 520 620 620', 'back': '80 540 840 840', 'pet': '660 1080 260 260'})
    pack = {'format': 2, 'id': 'chibi', 'name': 'Q 版描邊風', 'version': '2.0', 'date': '2026-11-15', 'author': 'Claude',
            'base': base, 'poses': flat['poses'], 'expr': expr, 'defaults': dict(flat['defaults']), 'view': view, 'cats': cats}
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    json.dump(pack, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('ok', out_path, sum(len(C['opts']) for C in cats.values()), '個部件')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'packs/chibi/pack.json')
