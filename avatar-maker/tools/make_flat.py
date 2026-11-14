#!/usr/bin/env python3
"""產生「扁平圓潤風」風格包（格式 2）v2.0 2026-11-15
用法：python tools/make_flat.py packs/flat/pack.json
全身畫布 1000×1400，半身＝裁上方 1000×1000。所有部件都在這裡用程式畫，make_chibi.py 會拿這份再加工。
"""
import json, sys, math

# ---------- 顏色代號（網頁會換成學生選的顏色） ----------
SK, SK2 = '{skin}', '{skin2}'
H, H2 = '{hair}', '{hair2}'
EY = '{eye}'
C1, C1D, C2 = '{c1}', '{c1d}', '{c2}'
HAT, ACC = '{hat}', '{acc}'
COAT, COATD = '{coat}', '{coatd}'
PA, PAD = '{pants}', '{pantsd}'
SH = '{shoe}'
BK, BKD = '{back}', '{backd}'
PET, PETD = '{pet}', '{petd}'
SL = '{sleeve}'
INK = '#2b2b33'
MOUTH_IN, TONGUE, LIP = '#7a1f2b', '#ff8a8a', '#8a3b2e'

EYE_L, EYE_R, EYE_Y = 410, 590, 400
both = lambda f: f(EYE_L) + f(EYE_R)
MIR = lambda s: f'<g transform="matrix(-1 0 0 1 1000 0)">{s}</g>'   # 左右鏡像
sym = lambda s: s + MIR(s)
shade = lambda o=.18: f'fill="#000" opacity="{o}"'


def stroke(d, col, w, extra=''):
    return f'<path d="{d}" stroke="{col}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round"{extra}/>'


def star(cx, cy, r, fill, rot=0, extra=''):
    pts = []
    for i in range(10):
        a = math.radians(rot - 90 + i * 36)
        rr = r if i % 2 == 0 else r * .45
        pts.append(f'{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}')
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"{extra}/>'


def heart(cx, cy, s, fill, extra=''):
    return (f'<path d="M{cx} {cy + 22 * s} C{cx - 40 * s} {cy - 4 * s} {cx - 26 * s} {cy - 38 * s} {cx} {cy - 14 * s} '
            f'C{cx + 26 * s} {cy - 38 * s} {cx + 40 * s} {cy - 4 * s} {cx} {cy + 22 * s} Z" fill="{fill}"{extra}/>')


# ---------- 身體幾何 ----------
TORSO_D = 'M380 714 Q500 700 620 714 Q668 724 672 780 L662 1036 Q500 1052 338 1036 L328 780 Q332 724 380 714 Z'
torso = lambda fill: f'<path d="{TORSO_D}" fill="{fill}"/>'


def xl(y):  # 身體左緣 x
    return 328 + (y - 780) * 10 / 256 if y >= 780 else 328 + (780 - y) ** 2 / 1600


def band(y0, y1, fill, inset=2, extra=''):
    a, b = xl(y0) + inset, xl(y1) + inset
    return f'<polygon points="{a:.1f},{y0} {1000 - a:.1f},{y0} {1000 - b:.1f},{y1} {b:.1f},{y1}" fill="{fill}"{extra}/>'


NECK = '<rect x="456" y="600" width="88" height="130" rx="30" fill="{skin2}"/>'
EARS = '<circle cx="282" cy="450" r="36" fill="{skin2}"/><circle cx="718" cy="450" r="36" fill="{skin2}"/>'
LEGS = ('<rect x="400" y="980" width="82" height="390" rx="36" fill="{skin}"/>'
        '<rect x="518" y="980" width="82" height="390" rx="36" fill="{skin}"/>')

# ---------- 手臂（依動作） ----------
ARMS_GEO = {   # 肩、肘、腕、手的樣子
    'L_down': ((352, 752), (318, 868), (314, 966), 'fist'),
    'L_wave': ((352, 752), (248, 716), (214, 604), 'open'),
    'L_hip': ((352, 752), (260, 872), (346, 968), 'fist'),
    'L_thumb': ((352, 752), (300, 892), (398, 872), 'thumb'),
    'R_down': ((648, 752), (682, 868), (686, 966), 'fist'),
    'R_hip': ((648, 752), (740, 872), (654, 968), 'fist'),
    'R_hold': ((648, 752), (712, 878), (622, 892), 'fist'),
}
HOLD = (604, 886)   # 手持物的握點


def arm_parts(name, outline=None, ow=14):
    (sx, sy), (ex, ey), (wx, wy), kind = ARMS_GEO[name]
    full = f'M{sx} {sy} L{ex} {ey} L{wx} {wy}'
    k = .62
    short = f'M{sx} {sy} L{sx + (ex - sx) * k:.0f} {sy + (ey - sy) * k:.0f}'
    ln = lambda d, col, w: stroke(d, col, w)
    out = (lambda d, w: ln(d, outline, w + ow)) if outline else (lambda d, w: '')
    skin = out(full, 54) + ln(full, SK, 54)
    longs = out(full, 62) + ln(full, SL, 62)
    shorts = out(short, 66) + ln(short, SL, 66)
    # 手
    dx, dy = wx - ex, wy - ey
    L = math.hypot(dx, dy)
    hx, hy = wx + dx / L * 14, wy + dy / L * 14
    oc = f' stroke="{outline}" stroke-width="{ow * .6:.0f}"' if outline else ''
    if kind == 'open':
        hand = (f'<ellipse cx="{hx:.0f}" cy="{hy - 6:.0f}" rx="34" ry="40" fill="{SK}"{oc}/>'
                f'<ellipse cx="{hx + 34:.0f}" cy="{hy + 10:.0f}" rx="13" ry="22" transform="rotate(35 {hx + 34:.0f} {hy + 10:.0f})" fill="{SK}"{oc}/>'
                + stroke(f'M{hx - 16:.0f} {hy - 30:.0f} L{hx - 16:.0f} {hy - 8:.0f} M{hx:.0f} {hy - 36:.0f} L{hx:.0f} {hy - 10:.0f} M{hx + 16:.0f} {hy - 30:.0f} L{hx + 16:.0f} {hy - 8:.0f}', SK2, 6))
    elif kind == 'thumb':
        hand = (f'<rect x="{hx - 12:.0f}" y="{hy - 70:.0f}" width="26" height="56" rx="13" fill="{SK}"{oc}/>'
                f'<circle cx="{hx:.0f}" cy="{hy:.0f}" r="34" fill="{SK}"{oc}/>'
                + stroke(f'M{hx - 20:.0f} {hy - 6:.0f} L{hx + 14:.0f} {hy - 6:.0f} M{hx - 20:.0f} {hy + 10:.0f} L{hx + 14:.0f} {hy + 10:.0f}', SK2, 6))
    else:
        hand = f'<circle cx="{hx:.0f}" cy="{hy:.0f}" r="32" fill="{SK}"{oc}/>'
    return {'skin': skin, 'long': longs, 'short': shorts, 'hand': hand}


def arms(outline=None):
    return {k: arm_parts(k, outline) for k in ARMS_GEO}


POSES = {'stand': {'name': '站立', 'L': 'L_down', 'R': 'R_down'},
         'wave': {'name': '揮手', 'L': 'L_wave', 'R': 'R_down'},
         'hips': {'name': '叉腰', 'L': 'L_hip', 'R': 'R_hip'},
         'thumb': {'name': '比讚', 'L': 'L_thumb', 'R': 'R_down'}}

# ---------- 臉型 ----------
FACE = [
    ('f1', '圓臉', '<circle cx="500" cy="430" r="220" fill="{skin}"/>'),
    ('f2', '鵝蛋臉', '<ellipse cx="500" cy="438" rx="204" ry="234" fill="{skin}"/>'),
    ('f3', '方臉', '<rect x="284" y="212" width="432" height="448" rx="150" fill="{skin}"/>'),
    ('f4', '包子臉', '<ellipse cx="500" cy="445" rx="236" ry="212" fill="{skin}"/>'),
]


# ---------- 髮型 ----------
def braid(x0, y0, x1, y1, n, tie=True):
    s = ''
    for i in range(n):
        t = i / max(1, n - 1)
        x, y = x0 + (x1 - x0) * t + (8 if i % 2 else -8), y0 + (y1 - y0) * t
        s += f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{34 - 8 * t:.0f}" ry="30" fill="{H}"/>' + stroke(f'M{x - 22:.0f} {y - 4:.0f} Q{x:.0f} {y + 16:.0f} {x + 22:.0f} {y - 4:.0f}', H2, 5)
    if tie:
        s += f'<rect x="{x1 - 24}" y="{y1 + 22}" width="48" height="20" rx="10" fill="{C2}"/>'
        s += f'<path d="M{x1 - 20} {y1 + 40} Q{x1} {y1 + 100} {x1 + 20} {y1 + 40} Z" fill="{H}"/>'
    return s


def curls(points, r, fill=H):
    return ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>' for x, y in points)


AFRO_BACK = ''.join(f'<circle cx="{500 + 250 * math.cos(math.radians(a)):.0f}" cy="{350 + 215 * math.sin(math.radians(a)):.0f}" r="96" fill="{H}"/>'
                    for a in range(0, 360, 30)) + f'<ellipse cx="500" cy="350" rx="260" ry="220" fill="{H}"/>'
CURLY_BACK = (f'<path d="M250 430 Q240 168 500 164 Q760 168 750 430 L760 760 Q500 800 240 760 Z" fill="{H}"/>'
              + curls([(250, 500), (236, 580), (244, 660), (262, 740), (330, 790), (750, 500), (764, 580), (756, 660), (738, 740), (670, 790)], 52))

HAIR = [
    ('h1', '短髮', None, f'<path d="M280 430 Q280 190 500 184 Q724 190 720 430 Q700 300 600 280 Q520 350 350 320 Q300 350 280 430 Z" fill="{H}"/>'),
    ('h2', '長直髮', f'<path d="M250 430 Q240 168 500 164 Q760 168 750 430 L772 830 Q650 860 610 700 L390 700 Q350 860 228 830 Z" fill="{H}"/>',
     f'<path d="M278 440 Q270 185 500 180 Q730 185 722 440 Q700 330 640 312 L600 348 L550 308 L500 348 L450 308 L400 348 L360 312 Q300 330 278 440 Z" fill="{H}"/>'),
    ('h3', '馬尾', f'<path d="M680 250 Q880 230 860 480 Q850 640 770 690 Q810 530 740 420 Z" fill="{H}"/><circle cx="716" cy="270" r="26" fill="{C2}"/>',
     f'<path d="M280 430 Q280 190 500 184 Q724 190 720 430 Q690 290 540 270 Q420 330 330 320 Q296 350 280 430 Z" fill="{H}"/>'),
    ('h4', '刺蝟頭', None, f'<path d="M280 430 L262 300 L326 328 L336 196 L420 268 L470 146 L540 258 L622 156 L652 278 L744 236 L720 430 Q690 320 500 310 Q310 320 280 430 Z" fill="{H}"/>'),
    ('h5', '包包頭', f'<circle cx="300" cy="215" r="82" fill="{H}"/><circle cx="700" cy="215" r="82" fill="{H}"/>',
     f'<path d="M280 430 Q280 190 500 184 Q724 190 720 430 Q700 310 500 268 Q300 310 280 430 Z" fill="{H}"/>'),
    ('h6', '捲捲頭', f'<circle cx="262" cy="500" r="72" fill="{H}"/><circle cx="738" cy="500" r="72" fill="{H}"/>',
     f'<g fill="{H}"><circle cx="290" cy="392" r="62"/><circle cx="330" cy="300" r="80"/><circle cx="420" cy="232" r="86"/><circle cx="520" cy="208" r="90"/><circle cx="620" cy="236" r="86"/><circle cx="688" cy="308" r="78"/><circle cx="712" cy="396" r="60"/></g>'),
    ('h7', '雙馬尾', f'<path d="M300 300 Q130 330 150 560 Q160 700 240 760 Q210 600 300 470 Z" fill="{H}"/><path d="M700 300 Q870 330 850 560 Q840 700 760 760 Q790 600 700 470 Z" fill="{H}"/>',
     f'<path d="M278 440 Q270 185 500 180 Q730 185 722 440 Q700 320 620 300 Q500 345 380 300 Q300 320 278 440 Z" fill="{H}"/><circle cx="292" cy="318" r="24" fill="{C2}"/><circle cx="708" cy="318" r="24" fill="{C2}"/>'),
    ('h8', '平頭', None, f'<path d="M286 400 Q290 200 500 196 Q710 200 714 400 Q690 286 500 282 Q310 286 286 400 Z" fill="{H}"/>'),
    ('h9', '妹妹頭', f'<path d="M258 430 Q248 172 500 168 Q752 172 742 430 L748 606 Q712 640 672 606 L328 606 Q288 640 252 606 Z" fill="{H}"/>',
     f'<path d="M270 470 Q260 178 500 174 Q740 178 730 470 L712 470 L702 330 L298 330 L288 470 Z" fill="{H}"/>'),
    ('h10', '西瓜頭', None,
     f'<path d="M268 450 Q258 174 500 170 Q742 174 732 450 L716 450 Q712 366 696 352 L304 352 Q288 366 284 450 Z" fill="{H}"/>' + stroke('M330 346 L670 346', H2, 6, ' opacity=".5"')),
    ('h11', '中分', f'<path d="M262 430 Q252 178 500 174 Q748 178 738 430 L744 660 Q640 690 610 640 L390 640 Q360 690 256 660 Z" fill="{H}"/>',
     f'<path d="M274 480 Q260 184 500 178 Q740 184 726 480 Q704 330 624 282 Q556 248 500 234 Q444 248 376 282 Q296 330 274 480 Z" fill="{H}"/>' + stroke('M500 184 L500 232', H2, 7)),
    ('h12', '旁分', None,
     f'<path d="M276 466 Q262 184 500 178 Q738 184 724 420 Q702 300 570 288 Q430 296 350 356 Q300 400 276 466 Z" fill="{H}"/>' + stroke('M430 186 Q410 236 430 290', H2, 7)),
    ('h13', '波浪長髮', f'<path d="M250 430 Q236 170 500 166 Q764 170 750 430 Q780 520 752 600 Q790 690 756 770 Q780 840 720 870 Q650 860 640 760 L360 760 Q350 860 280 870 Q220 840 244 770 Q210 690 248 600 Q220 520 250 430 Z" fill="{H}"/>',
     f'<path d="M274 470 Q260 182 500 176 Q740 182 726 470 Q714 340 652 300 Q600 344 540 302 Q480 344 420 302 Q350 330 274 470 Z" fill="{H}"/>'),
    ('h14', '公主頭', f'<path d="M250 430 Q240 168 500 164 Q760 168 750 430 L766 800 Q640 830 610 700 L390 700 Q360 830 234 800 Z" fill="{H}"/>',
     f'<path d="M278 452 Q268 184 500 178 Q732 184 722 452 Q706 320 600 290 Q500 332 400 290 Q294 320 278 452 Z" fill="{H}"/>'
     f'<path d="M676 236 L620 196 L622 276 Z" fill="{C2}"/><path d="M676 236 L732 196 L730 276 Z" fill="{C2}"/><circle cx="676" cy="236" r="20" fill="{C2}"/><circle cx="676" cy="236" r="20" {shade(.15)}/>'),
    ('h15', '單辮子', None,
     f'<path d="M276 470 Q262 184 500 178 Q738 184 724 430 Q700 300 560 290 Q420 300 340 360 Q300 410 276 470 Z" fill="{H}"/>' + braid(292, 480, 300, 770, 7)),
    ('h16', '雙辮子', None,
     f'<path d="M276 470 Q262 184 500 178 Q738 184 724 470 Q700 320 620 300 Q500 344 380 300 Q300 320 276 470 Z" fill="{H}"/>' + stroke('M500 182 L500 236', H2, 7)
     + braid(286, 480, 292, 740, 6) + braid(714, 480, 708, 740, 6)),
    ('h17', '爆炸頭', AFRO_BACK,
     f'<path d="M282 420 Q282 220 500 214 Q718 220 718 420 Q700 300 500 290 Q300 300 282 420 Z" fill="{H}"/>'
     + curls([(330, 300), (400, 268), (470, 254), (540, 254), (610, 268), (672, 300)], 38)),
    ('h18', '飛機頭', None,
     f'<path d="M284 430 Q276 250 330 200 Q380 128 520 124 Q660 122 712 200 Q736 250 716 430 Q700 330 640 300 Q560 280 470 300 Q400 290 350 320 Q300 350 284 430 Z" fill="{H}"/>'
     + stroke('M380 210 Q480 150 640 190', H2, 8, ' opacity=".55"')),
    ('h19', '呆毛頭', None,
     f'<path d="M280 430 Q280 190 500 184 Q724 190 720 430 Q700 300 600 280 Q520 350 350 320 Q300 350 280 430 Z" fill="{H}"/>' + stroke('M492 190 Q456 120 512 98 Q566 84 546 136', H, 16)),
    ('h20', '層次短髮', f'<path d="M262 440 Q250 180 500 176 Q750 180 738 440 L742 566 L704 528 L666 606 L334 606 L296 528 L258 566 Z" fill="{H}"/>',
     f'<path d="M276 470 Q262 186 500 180 Q738 186 724 470 L702 404 L690 330 L642 362 L610 300 L562 352 L520 302 L480 352 L438 302 L398 352 L358 312 L318 382 L300 424 Z" fill="{H}"/>'),
    ('h21', '丸子頭', f'<circle cx="500" cy="140" r="66" fill="{H}"/>' + stroke('M470 110 Q500 92 530 110', H2, 6, ' opacity=".6"'),
     f'<path d="M282 432 Q280 192 500 186 Q720 192 718 432 Q700 300 560 286 Q500 320 440 286 Q300 300 282 432 Z" fill="{H}"/><ellipse cx="500" cy="190" rx="46" ry="14" fill="{C2}"/>'),
    ('h22', '長捲髮', CURLY_BACK,
     f'<path d="M276 460 Q262 184 500 178 Q738 184 724 460 Q712 340 660 300 L340 300 Q288 340 276 460 Z" fill="{H}"/>'
     + curls([(332, 312), (394, 296), (456, 288), (518, 288), (580, 294), (640, 308)], 36)),
    ('h23', '側馬尾', f'<path d="M690 280 Q820 250 832 400 Q852 560 790 690 Q772 560 742 470 Q722 400 690 380 Z" fill="{H}"/><circle cx="712" cy="300" r="28" fill="{C2}"/>',
     f'<path d="M276 466 Q262 184 500 178 Q738 184 724 430 Q702 300 570 288 Q430 296 350 356 Q300 400 276 466 Z" fill="{H}"/>'),
    ('h24', '龐克頭', None,
     f'<path d="M284 410 Q288 214 500 208 Q712 214 716 410 Q692 300 500 294 Q308 300 284 410 Z" fill="{H}" opacity=".45"/>'
     f'<path d="M432 300 L404 168 L456 206 L462 112 L508 184 L540 100 L562 190 L606 150 L590 300 Q510 284 432 300 Z" fill="{H}"/>'),
]

# ---------- 眉毛 ----------
BROW = [
    ('b1', '彎彎眉', both(lambda x: stroke(f'M{x - 34} 352 Q{x} 334 {x + 34} 352', H2, 12))),
    ('b2', '一字眉', both(lambda x: stroke(f'M{x - 34} 346 L{x + 34} 346', H2, 14))),
    ('b3', '生氣眉', stroke('M376 334 L444 356', H2, 14) + stroke('M624 334 L556 356', H2, 14)),
    ('b4', '八字眉', stroke('M376 356 L444 336', H2, 14) + stroke('M624 356 L556 336', H2, 14)),
    ('b5', '粗眉', both(lambda x: f'<rect x="{x - 38}" y="332" width="76" height="26" rx="13" fill="{H2}"/>')),
    ('b6', '短短眉', both(lambda x: f'<ellipse cx="{x}" cy="342" rx="18" ry="12" fill="{H2}"/>')),
]

# ---------- 眼睛 ----------
BLINK = both(lambda x: stroke(f'M{x - 30} {EYE_Y + 4} Q{x} {EYE_Y + 22} {x + 30} {EYE_Y + 4}', INK, 12))
EYES = [
    ('e1', '圓圓眼', both(lambda x: f'<circle cx="{x}" cy="{EYE_Y}" r="28" fill="{EY}"/><circle cx="{x + 10}" cy="{EYE_Y - 10}" r="10" fill="#fff"/>')),
    ('e2', '閃亮大眼', both(lambda x: f'<ellipse cx="{x}" cy="{EYE_Y}" rx="36" ry="44" fill="#fff"/><ellipse cx="{x}" cy="{EYE_Y + 4}" rx="28" ry="36" fill="{EY}"/><circle cx="{x}" cy="{EYE_Y + 8}" r="14" fill="#1c1c24"/><circle cx="{x + 12}" cy="{EYE_Y - 14}" r="11" fill="#fff"/><circle cx="{x - 12}" cy="{EYE_Y + 18}" r="6" fill="#fff"/>')),
    ('e3', '笑笑眼', both(lambda x: stroke(f'M{x - 30} {EYE_Y + 10} Q{x} {EYE_Y - 26} {x + 30} {EYE_Y + 10}', EY, 13))),
    ('e4', '睫毛眼', both(lambda x: f'<circle cx="{x}" cy="{EYE_Y}" r="26" fill="{EY}"/><circle cx="{x + 9}" cy="{EYE_Y - 9}" r="9" fill="#fff"/>'
                        + stroke(f'M{x - 30} {EYE_Y - 22} l-14 -14 M{x - 8} {EYE_Y - 32} l-4 -18 M{x + 16} {EYE_Y - 30} l6 -18', INK, 7))),
    ('e5', '豆豆眼', both(lambda x: f'<circle cx="{x}" cy="{EYE_Y}" r="15" fill="{EY}"/>')),
    ('e6', '瞇瞇眼', both(lambda x: stroke(f'M{x - 30} {EYE_Y} Q{x} {EYE_Y + 12} {x + 30} {EYE_Y}', INK, 11))),
    ('e7', '星星眼', both(lambda x: f'<ellipse cx="{x}" cy="{EYE_Y}" rx="34" ry="40" fill="#fff"/><ellipse cx="{x}" cy="{EYE_Y + 3}" rx="27" ry="33" fill="{EY}"/>'
                        + star(x, EYE_Y + 2, 20, '#fff6b0'))),
    ('e8', '貓眼', both(lambda x: f'<path d="M{x - 42} {EYE_Y + 4} Q{x - 6} {EYE_Y - 40} {x + 42} {EYE_Y - 8} Q{x + 6} {EYE_Y + 36} {x - 42} {EYE_Y + 4} Z" fill="#fff" stroke="{INK}" stroke-width="7"/>'
                     f'<circle cx="{x}" cy="{EYE_Y - 2}" r="21" fill="{EY}"/><ellipse cx="{x}" cy="{EYE_Y - 2}" rx="6" ry="16" fill="#1c1c24"/><circle cx="{x + 8}" cy="{EYE_Y - 12}" r="6" fill="#fff"/>')),
    ('e9', '垂垂眼', both(lambda x: f'<circle cx="{x}" cy="{EYE_Y + 4}" r="24" fill="{EY}"/><circle cx="{x + 8}" cy="{EYE_Y - 4}" r="8" fill="#fff"/>'
                        + stroke(f'M{x - 34} {EYE_Y - 26} Q{x} {EYE_Y - 34} {x + 36} {EYE_Y - 14}' if x > 500 else f'M{x - 36} {EYE_Y - 14} Q{x} {EYE_Y - 34} {x + 34} {EYE_Y - 26}', INK, 9))),
    ('e10', '酷酷眼', both(lambda x: f'<path d="M{x - 30} {EYE_Y - 4} L{x + 30} {EYE_Y - 4} A30 30 0 0 1 {x - 30} {EYE_Y - 4} Z" fill="{EY}"/><circle cx="{x + 10}" cy="{EYE_Y + 8}" r="7" fill="#fff"/>'
                         + stroke(f'M{x - 36} {EYE_Y - 6} L{x + 36} {EYE_Y - 6}', INK, 11))),
]

# ---------- 嘴巴 ----------
MOUTH = [
    ('m1', '微笑', stroke('M450 524 Q500 564 550 524', LIP, 14),
     f'<ellipse cx="500" cy="536" rx="48" ry="38" fill="{MOUTH_IN}"/><ellipse cx="500" cy="558" rx="28" ry="16" fill="{TONGUE}"/><rect x="464" y="502" width="72" height="14" rx="6" fill="#fff"/>'),
    ('m2', '大笑', stroke('M432 512 Q500 590 568 512', LIP, 14),
     f'<path d="M432 508 Q500 632 568 508 Z" fill="{MOUTH_IN}"/><path d="M462 574 Q500 600 538 574 Q500 556 462 574 Z" fill="{TONGUE}"/><path d="M448 512 L552 512 L546 528 L454 528 Z" fill="#fff"/>'),
    ('m3', '小嘴', stroke('M478 536 L522 536', LIP, 13), f'<ellipse cx="500" cy="540" rx="22" ry="26" fill="{MOUTH_IN}"/>'),
    ('m4', '貓咪嘴', stroke('M456 522 Q478 552 500 524 Q522 552 544 522', LIP, 12),
     stroke('M456 522 Q478 552 500 524 Q522 552 544 522', LIP, 12) + f'<ellipse cx="500" cy="562" rx="24" ry="22" fill="{MOUTH_IN}"/>'),
    ('m5', '嘟嘟嘴', '<circle cx="500" cy="538" r="14" fill="#c9675a"/>',
     f'<ellipse cx="500" cy="540" rx="30" ry="34" fill="{MOUTH_IN}"/><ellipse cx="500" cy="558" rx="16" ry="10" fill="{TONGUE}"/>'),
    ('m6', '虎牙笑', stroke('M448 522 Q500 560 552 522', LIP, 13) + '<path d="M518 536 L526 556 L534 532 Z" fill="#fff"/>',
     f'<path d="M444 514 Q500 600 556 514 Z" fill="{MOUTH_IN}"/><path d="M470 566 Q500 584 530 566 Q500 552 470 566 Z" fill="{TONGUE}"/><path d="M516 514 L526 540 L536 514 Z" fill="#fff"/>'),
    ('m7', '吐舌頭', stroke('M452 526 Q500 552 548 526', LIP, 13) + f'<path d="M482 540 L482 566 Q500 590 518 566 L518 540 Z" fill="{TONGUE}"/>' + stroke('M500 548 L500 568', '#e06a6a', 4),
     f'<ellipse cx="500" cy="536" rx="44" ry="34" fill="{MOUTH_IN}"/><path d="M476 540 L476 576 Q500 604 524 576 L524 540 Z" fill="{TONGUE}"/>'),
]

# ---------- 鼻子 ----------
NOSE = [
    ('n1', '小圓鼻', '<circle cx="500" cy="470" r="9" fill="{skin2}"/>'),
    ('n2', '小勾鼻', stroke('M490 462 Q500 482 512 464', SK2, 9)),
    ('n3', '三角鼻', '<path d="M500 452 L514 480 L486 480 Z" fill="{skin2}"/>'),
    ('n4', '兩點鼻', '<ellipse cx="490" cy="474" rx="6" ry="5" fill="{skin2}"/><ellipse cx="510" cy="474" rx="6" ry="5" fill="{skin2}"/>'),
]

# ---------- 臉部裝飾 ----------
DECO = [
    ('d1', '腮紅', '<ellipse cx="360" cy="490" rx="36" ry="20" fill="#ff9e9e" opacity=".6"/><ellipse cx="640" cy="490" rx="36" ry="20" fill="#ff9e9e" opacity=".6"/>'),
    ('d2', '雀斑', '<g fill="{skin2}"><circle cx="345" cy="478" r="6"/><circle cx="370" cy="492" r="6"/><circle cx="392" cy="476" r="6"/><circle cx="608" cy="476" r="6"/><circle cx="630" cy="492" r="6"/><circle cx="655" cy="478" r="6"/></g>'),
    ('d3', 'OK 繃', '<g transform="rotate(-18 650 490)"><rect x="606" y="474" width="88" height="32" rx="12" fill="#f3c9a0"/><rect x="636" y="474" width="28" height="32" fill="#e6b488"/></g>'),
    ('d4', '星星貼紙', star(352, 486, 30, '#ffc531')),
    ('d5', '愛心貼紙', heart(648, 486, 1, '#ff6f9c')),
    ('d6', '小鬍子', f'<path d="M500 498 Q470 486 446 498 Q424 512 412 500 Q420 526 452 522 Q482 518 500 506 Q518 518 548 522 Q580 526 588 500 Q576 512 554 498 Q530 486 500 498 Z" fill="{H2}"/>'),
    ('d7', '加油臉彩', f'<g transform="rotate(-12 360 490)"><rect x="318" y="470" width="84" height="14" rx="7" fill="{C1}"/><rect x="318" y="490" width="84" height="14" rx="7" fill="{C2}"/></g>'
                     f'<g transform="rotate(12 640 490)"><rect x="598" y="470" width="84" height="14" rx="7" fill="{C1}"/><rect x="598" y="490" width="84" height="14" rx="7" fill="{C2}"/></g>'),
    ('d8', '貓鬍鬚', stroke('M300 470 L380 486 M296 504 L380 500 M306 536 L382 514 M700 470 L620 486 M704 504 L620 500 M694 536 L618 514', INK, 6, ' opacity=".75"')),
]

# ---------- 眼鏡 ----------
GLASS = [
    ('g1', '圓框眼鏡', both(lambda x: f'<circle cx="{x}" cy="{EYE_Y}" r="56" fill="#ffffff" fill-opacity=".18" stroke="{INK}" stroke-width="10"/>') + stroke('M466 400 L534 400', INK, 10)),
    ('g2', '方框眼鏡', both(lambda x: f'<rect x="{x - 60}" y="{EYE_Y - 44}" width="120" height="88" rx="18" fill="#ffffff" fill-opacity=".18" stroke="{C2}" stroke-width="10"/>') + stroke('M470 400 L530 400', C2, 10)),
    ('g3', '太陽眼鏡', both(lambda x: f'<rect x="{x - 64}" y="{EYE_Y - 40}" width="128" height="84" rx="34" fill="#1c1c24"/>') + stroke('M466 392 L534 392', '#1c1c24', 12)
     + stroke('M366 380 l40 -14 M546 380 l40 -14', '#fff', 8, ' opacity=".5"')),
    ('g4', '星星眼鏡', both(lambda x: star(x, EYE_Y + 2, 74, '#ffffff', 0, f' fill-opacity=".2" stroke="{C2}" stroke-width="12" stroke-linejoin="round"')) + stroke('M470 396 L530 396', C2, 10)),
    ('g5', '愛心眼鏡', both(lambda x: heart(x, EYE_Y + 2, 1.9, '#ff6f9c', f' fill-opacity=".35" stroke="#e23c76" stroke-width="10"')) + stroke('M470 392 L530 392', '#e23c76', 10)),
    ('g6', '護目鏡', stroke('M270 404 Q500 380 730 404', C2, 30) + both(lambda x: f'<circle cx="{x}" cy="{EYE_Y + 2}" r="62" fill="#9fdcff" fill-opacity=".45" stroke="#6c7383" stroke-width="16"/>')
     + both(lambda x: stroke(f'M{x - 30} {EYE_Y - 26} Q{x - 10} {EYE_Y - 40} {x + 14} {EYE_Y - 36}', '#fff', 8, ' opacity=".7"'))),
]

# ---------- 帽子頭飾 ----------
FLOWERS = ''
for i, (x, y) in enumerate([(296, 300), (330, 248), (382, 210), (440, 190), (500, 184), (560, 190), (618, 210), (670, 248), (704, 300)]):
    col = ['#ff8fb3', '#ffc531', '#ffffff', '#8ad0ff', '#ff9e6b'][i % 5]
    if i % 2 == 0:
        FLOWERS += f'<ellipse cx="{x + 24}" cy="{y + 10}" rx="20" ry="10" fill="#5bb36a" transform="rotate(30 {x + 24} {y + 10})"/>'
    FLOWERS += ''.join(f'<circle cx="{x + 18 * math.cos(math.radians(a)):.0f}" cy="{y + 18 * math.sin(math.radians(a)):.0f}" r="15" fill="{col}"/>' for a in range(0, 360, 72))
    FLOWERS += f'<circle cx="{x}" cy="{y}" r="10" fill="#ffb300"/>'

HATS = [
    ('a1', '棒球帽', f'<path d="M282 332 Q286 150 500 145 Q714 150 718 332 Z" fill="{HAT}"/><path d="M262 330 Q500 286 800 342 Q812 376 768 376 Q500 330 262 364 Z" fill="{HAT}"/><path d="M262 330 Q500 286 800 342 Q812 376 768 376 Q500 330 262 364 Z" {shade()}/><circle cx="500" cy="150" r="14" fill="#fff"/>'),
    ('a2', '蝴蝶結', f'<path d="M640 214 L560 160 L560 268 Z" fill="{HAT}"/><path d="M640 214 L720 160 L720 268 Z" fill="{HAT}"/><circle cx="640" cy="214" r="24" fill="{HAT}"/><circle cx="640" cy="214" r="24" {shade(.15)}/>'),
    ('a3', '皇冠', '<path d="M378 208 L396 110 L450 170 L500 88 L550 170 L604 110 L622 208 Z" fill="#ffc531"/><rect x="378" y="196" width="244" height="26" rx="8" fill="#e6a700"/><circle cx="500" cy="150" r="12" fill="#e2553b"/><circle cx="420" cy="170" r="9" fill="#4dc3c9"/><circle cx="580" cy="170" r="9" fill="#4dc3c9"/>'),
    ('a4', '貓耳', f'<path d="M296 262 L312 100 L426 190 Z" fill="{H}"/><path d="M704 262 L688 100 L574 190 Z" fill="{H}"/><path d="M322 226 L330 142 L392 192 Z" fill="#ffb3c7"/><path d="M678 226 L670 142 L608 192 Z" fill="#ffb3c7"/>'),
    ('a6', '魔法帽', f'<path d="M330 250 Q470 70 560 62 Q600 160 672 250 Z" fill="{HAT}"/><ellipse cx="500" cy="252" rx="280" ry="46" fill="{HAT}"/><ellipse cx="500" cy="252" rx="280" ry="46" {shade(.15)}/><path d="M356 224 Q500 262 646 224 L660 244 Q500 286 342 244 Z" fill="#ffc531"/>' + star(520, 160, 26, '#ffc531')),
    ('a7', '毛帽', f'<path d="M276 344 Q280 150 500 146 Q720 150 724 344 Z" fill="{HAT}"/><rect x="262" y="296" width="476" height="70" rx="34" fill="#fff"/><circle cx="500" cy="128" r="46" fill="#fff"/>'
     + ''.join(stroke(f'M{x} 196 L{x} 290', '#000', 8, ' opacity=".12"') for x in range(330, 680, 40))),
    ('a8', '兔耳', ''.join(f'<g transform="rotate({r} {x} 230)"><ellipse cx="{x}" cy="140" rx="36" ry="82" fill="{HAT}"/><ellipse cx="{x}" cy="150" rx="17" ry="58" fill="#ffb3c7"/></g>' for x, r in [(420, -12), (580, 12)])
     + stroke('M296 320 Q296 196 500 190 Q704 196 704 320', HAT, 22)),
    ('a9', '廚師帽', '<g fill="#fff" stroke="#d9d6e3" stroke-width="5"><circle cx="384" cy="176" r="72"/><circle cx="616" cy="176" r="72"/><circle cx="500" cy="140" r="76"/><rect x="326" y="200" width="348" height="104" rx="18"/></g>'
     + stroke('M420 220 L420 290 M500 220 L500 290 M580 220 L580 290', '#d9d6e3', 5)),
    ('a10', '消防帽', f'<path d="M300 300 Q300 120 500 116 Q700 120 700 300 Z" fill="{HAT}"/>' + stroke('M500 122 L500 296', '#fff', 16, ' opacity=".35"')
     + f'<path d="M244 300 Q500 262 756 300 Q776 338 744 344 Q500 304 256 344 Q224 338 244 300 Z" fill="{HAT}"/><path d="M244 300 Q500 262 756 300 Q776 338 744 344 Q500 304 256 344 Q224 338 244 300 Z" {shade(.2)}/>'
     + '<path d="M500 160 L556 182 L548 250 L500 278 L452 250 L444 182 Z" fill="#ffc531"/>' + star(500, 222, 26, '#e6a700')),
    ('a11', '貝雷帽', f'<g transform="rotate(-10 480 230)"><ellipse cx="480" cy="230" rx="236" ry="86" fill="{HAT}"/><path d="M262 250 Q480 300 698 250" stroke="#000" stroke-width="14" opacity=".15" fill="none"/><rect x="468" y="132" width="24" height="26" rx="8" fill="{HAT}"/></g>'),
    ('a12', '花圈', FLOWERS),
    ('a13', '熊耳', f'<circle cx="318" cy="222" r="64" fill="{H}"/><circle cx="682" cy="222" r="64" fill="{H}"/><circle cx="318" cy="228" r="34" fill="#fff" opacity=".35"/><circle cx="682" cy="228" r="34" fill="#fff" opacity=".35"/>'),
    ('a14', '學士帽', f'<path d="M340 214 L340 298 Q500 330 660 298 L660 214 Z" fill="{HAT}"/><path d="M340 214 L340 298 Q500 330 660 298 L660 214 Z" {shade(.2)}/><path d="M250 196 L500 124 L750 196 L500 268 Z" fill="{HAT}"/>'
     + '<circle cx="500" cy="196" r="12" fill="#ffc531"/>' + stroke('M500 196 L706 214 L708 300', '#ffc531', 8) + '<path d="M694 296 L722 296 L728 352 L688 352 Z" fill="#ffc531"/>'),
    ('a15', '外星天線', stroke('M290 320 Q290 192 500 186 Q710 192 710 320', HAT, 22) + stroke('M420 200 Q400 140 372 104 M580 200 Q600 140 628 104', INK, 8)
     + f'<circle cx="370" cy="96" r="26" fill="{HAT}"/><circle cx="630" cy="96" r="26" fill="{HAT}"/><circle cx="362" cy="88" r="8" fill="#fff" opacity=".6"/><circle cx="622" cy="88" r="8" fill="#fff" opacity=".6"/>'),
    ('a16', '髮箍', stroke('M290 320 Q290 192 500 186 Q710 192 710 320', HAT, 28) + f'<path d="M372 226 L320 196 L324 262 Z" fill="{HAT}"/><path d="M372 226 L420 186 L424 252 Z" fill="{HAT}"/><circle cx="372" cy="226" r="16" fill="{HAT}"/><circle cx="372" cy="226" r="16" {shade(.15)}/>'),
]

# ---------- 耳機麥克風 ----------
HEADSET = [
    ('s1', '主播耳麥', stroke('M270 440 Q262 160 500 156 Q738 160 730 440', INK, 24) + f'<rect x="236" y="392" width="62" height="124" rx="26" fill="{ACC}"/><rect x="702" y="392" width="62" height="124" rx="26" fill="{ACC}"/>'
     + stroke('M266 510 Q280 610 410 604', INK, 12) + f'<circle cx="420" cy="604" r="20" fill="{INK}"/>'),
    ('s2', '頭戴耳機', stroke('M262 450 Q254 140 500 136 Q746 140 738 450', ACC, 30) + f'<rect x="222" y="376" width="84" height="156" rx="38" fill="{ACC}"/><rect x="694" y="376" width="84" height="156" rx="38" fill="{ACC}"/>'
     + f'<rect x="222" y="376" width="84" height="156" rx="38" {shade(.18)}/><rect x="694" y="376" width="84" height="156" rx="38" {shade(.18)}/><rect x="236" y="390" width="56" height="128" rx="28" fill="{ACC}"/><rect x="708" y="390" width="56" height="128" rx="28" fill="{ACC}"/>'),
    ('s3', '耳掛麥克風', stroke('M260 420 Q250 470 290 490', ACC, 10) + stroke('M288 490 Q340 560 420 552', ACC, 8) + f'<circle cx="426" cy="550" r="14" fill="{INK}"/>'),
    ('s4', '貓耳耳機', stroke('M262 450 Q254 140 500 136 Q746 140 738 450', ACC, 30)
     + f'<path d="M346 196 L356 104 L428 160 Z" fill="{ACC}"/><path d="M654 196 L644 104 L572 160 Z" fill="{ACC}"/><path d="M364 176 L368 132 L404 160 Z" fill="#ffb3c7"/><path d="M636 176 L632 132 L596 160 Z" fill="#ffb3c7"/>'
     + f'<rect x="222" y="376" width="84" height="156" rx="38" fill="{ACC}"/><rect x="694" y="376" width="84" height="156" rx="38" fill="{ACC}"/>' + heart(264, 456, .9, '#fff', ' opacity=".8"') + heart(736, 456, .9, '#fff', ' opacity=".8"')),
]


# ---------- 上衣 ----------
def top(id_, name, svg, sleeve='long', fill=C1):
    return {'id': id_, 'name': name, 'svg': svg, 'sleeve': {'type': sleeve, 'fill': fill}}


def stripes(fill, ys, h):
    return ''.join(band(y, y + h, fill) for y in ys)


ROBE = f'<path d="M380 714 Q500 700 620 714 Q668 724 672 780 L708 1300 Q500 1330 292 1300 L328 780 Q332 724 380 714 Z" fill="{C1}"/>'
DRESS_SKIRT = f'<path d="M346 980 L654 980 Q700 1100 730 1236 Q500 1270 270 1236 Q300 1100 346 980 Z" fill="{C1}"/>'
TOPS = [
    top('t1', '主播西裝', torso(C1) + '<path d="M440 712 L500 834 L560 712 Z" fill="#fff"/>'
        + f'<path d="M488 742 L512 742 L520 762 L512 872 L500 886 L488 872 L480 762 Z" fill="{C2}"/>'
        + sym(f'<path d="M436 712 L398 732 L468 866 L500 834 Z" fill="{C1D}"/>') + '<circle cx="500" cy="930" r="9" fill="#2b2b33" opacity=".5"/><circle cx="500" cy="980" r="9" fill="#2b2b33" opacity=".5"/>'
        + f'<path d="M590 800 L640 800 L636 816 L594 816 Z" fill="{C2}"/>'),
    top('t2', 'T 恤', torso(C1) + stroke('M432 716 Q500 768 568 716', C2, 18) + star(500, 880, 46, C2), 'short'),
    top('t3', '帽 T', torso(C1) + f'<path d="M392 728 Q500 650 608 728 Q568 780 500 780 Q432 780 392 728 Z" fill="{C1D}"/>'
        + stroke('M470 778 L466 860 M530 778 L534 860', '#fff', 9) + f'<rect x="396" y="914" width="208" height="90" rx="30" fill="{C1D}"/>' + stroke('M420 914 L420 1004 M580 914 L580 1004', '#000', 4, ' opacity=".1"')),
    top('t4', '水手服', torso(C1) + sym(f'<path d="M420 708 L500 820 L464 852 L360 760 Q376 724 420 708 Z" fill="#fff"/>') + sym(stroke('M408 730 L478 826', C2, 6))
        + f'<path d="M500 826 L444 800 L452 872 Z" fill="{C2}"/><path d="M500 826 L556 800 L548 872 Z" fill="{C2}"/><circle cx="500" cy="830" r="17" fill="{C2}"/>'),
    top('t5', '球衣', torso(C1) + stroke('M424 712 L500 806 L576 712', C2, 22) + band(860, 900, C2) + sym(f'<path d="M330 790 L366 790 L356 1040 L340 1036 Z" fill="{C2}"/>'), 'short'),
    top('t6', '吊帶裝', torso('#fff') + f'<path d="M392 880 L608 880 L612 1040 Q500 1052 388 1040 Z" fill="{C1}"/>' + stroke('M404 884 L410 720 M596 884 L590 720', C1, 34)
        + f'<circle cx="404" cy="886" r="13" fill="{C2}"/><circle cx="596" cy="886" r="13" fill="{C2}"/><rect x="452" y="918" width="96" height="64" rx="14" fill="{C2}"/>', 'short', '#ffffff'),
    top('t7', '魔法袍', ROBE + f'<path d="M424 712 L500 1310 L576 712 Z" fill="{C1D}"/>' + stroke('M404 716 Q500 790 596 716', C2, 20) + stroke('M380 1290 Q500 1316 620 1290', C2, 14) + star(560, 860, 34, C2)),
    top('t8', '襯衫領帶', torso(C1) + sym(f'<path d="M444 710 L500 760 L470 800 L418 724 Z" fill="#fff"/>') + f'<path d="M490 760 L510 760 L520 900 L500 924 L480 900 Z" fill="{C2}"/>'
        + f'<rect x="572" y="808" width="56" height="60" rx="8" fill="{C1D}"/>', 'short'),
    top('t9', 'POLO 衫', torso(C1) + sym(f'<path d="M446 712 L500 744 L476 792 L416 732 Z" fill="{C2}"/>') + f'<rect x="488" y="744" width="24" height="100" rx="8" fill="{C1D}"/>'
        + '<circle cx="500" cy="770" r="6" fill="#fff"/><circle cx="500" cy="812" r="6" fill="#fff"/>', 'short'),
    top('t10', '條紋衫', torso(C1) + stripes(C2, [790, 850, 910, 970], 28) + stroke('M440 716 Q500 750 560 716', C1D, 12)),
    top('t11', '毛衣', torso(C1) + stroke('M436 716 Q500 760 564 716', C1D, 24) + band(1006, 1040, C1D, 6)
        + stroke('M352 860 L392 830 L432 860 L472 830 L512 860 L552 830 L592 860 L632 830 L652 846', C2, 14) + stroke('M352 900 L392 870 L432 900 L472 870 L512 900 L552 870 L592 900 L632 870 L652 886', '#fff', 10, ' opacity=".8"')),
    top('t12', '偶像舞台裝', torso(C1) + stroke('M420 716 Q440 740 460 716 Q480 740 500 716 Q520 740 540 716 Q560 740 580 716', '#fff', 12)
        + f'<path d="M500 800 L430 760 L436 846 Z" fill="{C2}"/><path d="M500 800 L570 760 L564 846 Z" fill="{C2}"/><circle cx="500" cy="802" r="20" fill="{C2}"/>'
        + ''.join(f'<circle cx="{x}" cy="1030" r="22" fill="{C2}"/>' for x in range(356, 660, 36)) + star(400, 920, 14, '#fff') + star(610, 900, 12, '#fff') + star(560, 970, 10, '#fff'), 'short'),
    top('t13', '醫師袍', torso('#ffffff') + f'<path d="M440 712 L500 830 L560 712 Z" fill="{C1}"/>' + sym('<path d="M436 712 L404 730 L466 1040 L494 1040 L494 836 Z" fill="#eef0f5"/>')
        + stroke('M430 760 Q400 900 470 920 Q540 900 560 800', '#6c7383', 8) + '<circle cx="470" cy="926" r="16" fill="#9aa3b5"/>'
        + '<rect x="574" y="840" width="66" height="70" rx="8" fill="#eef0f5"/>' + stroke('M590 832 L590 868', C2, 8), 'long', '#ffffff'),
    top('t14', '廚師服', torso('#ffffff') + f'<path d="M430 712 Q500 760 570 712 L556 744 Q500 784 444 744 Z" fill="{C2}"/>'
        + ''.join(f'<circle cx="{x}" cy="{y}" r="9" fill="#c9ccd6"/>' for x in (450, 550) for y in (810, 880, 950)) + stroke('M500 760 L500 1040', '#e3e3ea', 6), 'long', '#ffffff'),
    top('t15', '消防衣', torso(C1) + band(870, 900, '#ffd84d') + band(900, 920, '#e8e8ee') + band(980, 1010, '#ffd84d') + stroke('M500 720 L500 1040', '#2b2b33', 10, ' opacity=".35"')
        + stroke('M412 730 L412 860 M588 730 L588 860', '#ffd84d', 22)),
    top('t16', '太空衣', torso('#f4f4f8') + stroke('M420 718 Q500 748 580 718', '#9aa3b5', 26) + '<rect x="420" y="830" width="160" height="110" rx="18" fill="#c9ccd6"/>'
        + f'<circle cx="460" cy="866" r="14" fill="{C2}"/><circle cx="500" cy="866" r="14" fill="#4dc3c9"/><circle cx="540" cy="866" r="14" fill="#ffc531"/><rect x="448" y="896" width="104" height="22" rx="8" fill="#2b2b33"/>'
        + f'<circle cx="380" cy="790" r="26" fill="{C2}"/>' + star(380, 790, 16, '#fff'), 'long', '#f4f4f8'),
    top('t17', '騎士盔甲', torso('#b9c1d0') + '<path d="M400 730 Q500 700 600 730 L590 960 Q500 1010 410 960 Z" fill="#d6dbe5"/>' + stroke('M500 730 L500 990', '#9aa3b5', 8)
        + f'<path d="M500 800 L556 820 L548 880 L500 910 L452 880 L444 820 Z" fill="{C2}"/>' + band(990, 1040, '#8b93a5') + sym('<ellipse cx="362" cy="742" rx="56" ry="36" fill="#9aa3b5"/>'), 'long', '#b9c1d0'),
    top('t18', '恐龍裝', torso(C1) + '<ellipse cx="500" cy="900" rx="110" ry="130" fill="#fff4cc"/>' + stroke('M420 860 L580 860 M410 910 L590 910 M420 960 L580 960', '#e8d79a', 8)
        + f'<path d="M660 990 Q760 1000 790 940 Q770 1040 662 1040 Z" fill="{C1}"/>' + ''.join(f'<path d="M{x} 714 l14 -26 l14 26 Z" fill="{C1D}"/>' for x in (402, 444, 528, 570))),
    top('t19', '熊熊裝', torso(C1) + '<ellipse cx="500" cy="910" rx="104" ry="118" fill="#fff" opacity=".45"/>' + heart(500, 880, 1, '#ff8fb3') + stroke('M440 716 Q500 750 560 716', C1D, 12)),
    top('t20', '新年唐裝', torso(C1) + f'<rect x="440" y="706" width="120" height="34" rx="12" fill="{C2}"/>' + stroke('M500 740 L500 1040', C2, 8)
        + ''.join(stroke(f'M470 {y} Q486 {y - 14} 500 {y} Q514 {y - 14} 530 {y}', '#ffc531', 7) for y in (790, 850, 910, 970)) + band(1012, 1040, C2, 4)),
    top('t21', '聖誕毛衣', torso(C1) + band(760, 790, '#fff') + band(980, 1010, '#fff')
        + f'<path d="M500 816 L556 920 L444 920 Z" fill="{C2}"/><path d="M500 856 L572 960 L428 960 Z" fill="{C2}"/><rect x="488" y="960" width="24" height="20" fill="#8d6e63"/>' + star(500, 812, 16, '#ffc531')
        + ''.join(f'<circle cx="{x}" cy="{y}" r="7" fill="#fff"/>' for x, y in [(380, 840), (620, 860), (400, 940), (610, 950), (360, 900), (640, 910)])),
    top('t22', '南瓜裝', torso(C1) + stroke('M430 730 Q400 880 432 1036 M570 730 Q600 880 568 1036 M500 720 L500 1044', C1D, 10)
        + '<path d="M440 840 L470 840 L455 816 Z" fill="#3b2a24"/><path d="M530 840 L560 840 L545 816 Z" fill="#3b2a24"/><path d="M440 900 Q500 950 560 900 Q500 920 440 900 Z" fill="#3b2a24"/>'
        + '<path d="M460 712 Q480 690 500 712 Q520 690 540 712 L520 734 L480 734 Z" fill="#5bb36a"/>'),
    top('t23', '洋裝', DRESS_SKIRT + torso(C1) + f'<path d="M346 980 L654 980 Q700 1100 730 1236 Q500 1270 270 1236 Q300 1100 346 980 Z" fill="{C1}"/>'
        + stroke('M400 1000 Q380 1120 360 1240 M500 1000 L500 1250 M600 1000 Q620 1120 640 1240', C1D, 6, ' opacity=".7"')
        + band(960, 996, C2) + sym('<path d="M500 716 Q460 760 420 720 Q450 700 500 708 Z" fill="#fff"/>'), 'short'),
    top('t24', '畫家罩衫', torso(C1) + stroke('M432 716 Q500 760 568 716', C1D, 14) + '<rect x="420" y="890" width="160" height="96" rx="20" fill="#fff" opacity=".55"/>'
        + '<circle cx="390" cy="820" r="20" fill="#ff6f6f"/><circle cx="600" cy="790" r="14" fill="#4dc3c9"/><circle cx="620" cy="980" r="18" fill="#ffc531"/><circle cx="372" cy="1000" r="12" fill="#7bd389"/><circle cx="540" cy="840" r="10" fill="#8a5fd3"/>'),
]

# ---------- 外套（前面打開，看得到裡面的上衣） ----------
PANEL = 'M436 712 L380 714 Q332 724 328 780 L338 1040 Q392 1048 456 1048 L462 862 Z'
panel = lambda fill, d=PANEL: sym(f'<path d="{d}" fill="{fill}"/>')
COATS = [
    {'id': 'o1', 'name': '運動外套', 'svg': panel(COAT) + sym(stroke('M452 740 L458 1040', '#fff', 10)) + sym(stroke('M346 800 L356 1030', '#fff', 8, ' opacity=".8"')) + band(1012, 1044, COATD, 4)},
    {'id': 'o2', 'name': '西裝外套', 'svg': panel(COAT) + sym(f'<path d="M436 712 L404 730 L456 880 L462 862 Z" fill="{COATD}"/>') + '<circle cx="452" cy="940" r="9" fill="#2b2b33" opacity=".5"/><circle cx="548" cy="940" r="9" fill="#2b2b33" opacity=".5"/>'
     + f'<rect x="580" y="800" width="60" height="12" rx="4" fill="{COATD}"/>'},
    {'id': 'o3', 'name': '背心', 'svg': f'<path d="M420 710 L380 714 Q340 724 336 780 L344 1020 Q500 1040 656 1020 L664 780 Q660 724 620 714 L580 710 L500 840 Z" fill="{COAT}"/>'
     + stroke('M420 712 L500 842 L580 712', COATD, 12) + band(996, 1030, COATD, 12), 'sleeve': {'type': 'none', 'fill': COAT}},
    {'id': 'o4', 'name': '連帽外套', 'svg': f'<path d="M386 726 Q500 646 614 726 Q560 760 500 760 Q440 760 386 726 Z" fill="{COATD}"/>' + panel(COAT) + stroke('M466 770 L462 860 M534 770 L538 860', '#fff', 8)
     + sym(f'<rect x="352" y="930" width="90" height="70" rx="18" fill="{COATD}"/>')},
    {'id': 'o5', 'name': '牛仔外套', 'svg': panel(COAT) + sym(f'<rect x="364" y="790" width="76" height="62" rx="8" fill="{COATD}"/>') + sym(stroke('M368 822 L436 822', '#f3c26b', 4, ' stroke-dasharray="8 8"'))
     + sym(stroke('M452 730 L458 1040', '#f3c26b', 4, ' stroke-dasharray="8 8"')) + band(1010, 1044, COATD, 4)},
    {'id': 'o6', 'name': '羽絨外套', 'svg': panel(COAT, 'M450 700 L380 712 Q326 724 322 780 L332 1046 Q392 1056 462 1056 L466 700 Z') + f'<path d="M420 696 Q500 676 580 696 L582 744 Q500 726 418 744 Z" fill="{COATD}"/>'
     + ''.join(sym(stroke(f'M{xl(y) - 2:.0f} {y} Q400 {y + 12} 462 {y}', COATD, 6)) for y in (800, 870, 940, 1010))},
    {'id': 'o7', 'name': '風衣', 'svg': panel(COAT, 'M436 712 L380 714 Q332 724 328 780 L320 1240 Q400 1256 470 1250 L462 862 Z') + sym(f'<path d="M436 712 L398 734 L456 880 L462 862 Z" fill="{COATD}"/>')
     + band(980, 1012, COATD, -6) + f'<rect x="478" y="976" width="44" height="40" rx="6" fill="none" stroke="#ffc531" stroke-width="7"/>'
     + ''.join(f'<circle cx="{x}" cy="{y}" r="9" fill="{COATD}"/>' for x in (420, 580) for y in (900, 950))},
    {'id': 'o8', 'name': '開襟毛衣', 'svg': panel(COAT, 'M440 712 L380 714 Q332 724 328 780 L338 1040 Q392 1048 460 1048 L470 880 Z') + sym(stroke('M444 720 L466 1040', COATD, 10))
     + ''.join(f'<circle cx="{x}" cy="{y}" r="8" fill="#fff"/>' for x, y in [(458, 900), (462, 960), (464, 1016)]) + band(1012, 1044, COATD, 4)},
]
for c in COATS:
    c.setdefault('sleeve', {'type': 'long', 'fill': COAT})

# ---------- 下身（只有全身看得到） ----------
LONG = 'M340 990 L660 990 L664 1080 L612 1332 L512 1332 L500 1100 L488 1332 L388 1332 L336 1080 Z'
SHORT = 'M340 990 L660 990 L668 1150 L516 1150 L500 1090 L484 1150 L332 1150 Z'
SKIRT = 'M342 990 L658 990 L706 1180 Q500 1200 294 1180 Z'
pants = lambda d=LONG, fill=PA: f'<path d="{d}" fill="{fill}"/>'
waist = band(990, 1020, PAD, -8)
OP8 = ' opacity=".8"'
BOTTOMS = [
    ('p1', '長褲', pants() + waist + stroke('M440 1060 L440 1320 M560 1060 L560 1320', PAD, 5, ' opacity=".6"')),
    ('p2', '短褲', pants(SHORT) + waist + stroke('M336 1132 L484 1132 M516 1132 L664 1132', PAD, 10)),
    ('p3', '牛仔褲', pants() + waist + stroke('M370 1040 Q400 1080 450 1040 M630 1040 Q600 1080 550 1040', '#f3c26b', 5, ' stroke-dasharray="9 7"')
     + stroke('M500 1000 L500 1100', '#f3c26b', 5, ' stroke-dasharray="9 7"') + stroke('M394 1300 L486 1300 M514 1300 L606 1300', PAD, 12)),
    ('p4', '運動褲', pants() + waist + stroke('M342 1060 L392 1320 M658 1060 L608 1320', '#fff', 12) + stroke('M392 1316 L486 1316 M514 1316 L608 1316', PAD, 22)),
    ('p5', '百褶裙', pants(SKIRT) + waist + stroke('M380 1020 L356 1184 M430 1020 L420 1190 M500 1020 L500 1192 M570 1020 L580 1190 M620 1020 L644 1184', PAD, 6)),
    ('p6', 'A 字裙', pants('M346 990 L654 990 Q690 1090 712 1170 Q500 1196 288 1170 Q310 1090 346 990 Z') + waist + '<circle cx="470" cy="1060" r="9" fill="#fff"/><circle cx="530" cy="1060" r="9" fill="#fff"/>'
     + stroke('M300 1160 Q500 1186 700 1160', PAD, 10)),
    ('p7', '寬褲', pants('M340 990 L660 990 L690 1300 L512 1300 L500 1100 L488 1300 L310 1300 Z') + waist + stroke('M420 1080 L410 1290 M580 1080 L590 1290', PAD, 5, ' opacity=".5"')),
    ('p8', '工作褲', pants() + waist + sym(f'<rect x="342" y="1130" width="56" height="74" rx="10" fill="{PAD}"/>') + sym(stroke('M346 1150 L394 1150', '#000', 4, ' opacity=".2"'))),
    ('p9', '燈籠褲', pants('M336 990 L664 990 Q712 1090 670 1180 L514 1180 Q500 1120 486 1180 L330 1180 Q288 1090 336 990 Z') + waist
     + stroke('M340 1176 L484 1176 M516 1176 L660 1176', PAD, 16) + stroke('M420 1010 Q400 1100 420 1170 M580 1010 Q600 1100 580 1170', PAD, 5, ' opacity=".5"')),
    ('p10', '蓬蓬裙', ''.join(f'<path d="M{350 - i * 30} {1000 + i * 50} Q500 {980 + i * 50} {650 + i * 30} {1000 + i * 50} L{690 + i * 20} {1110 + i * 40} Q500 {1140 + i * 40} {310 - i * 20} {1110 + i * 40} Z" fill="{PA}"{OP8 if i == 0 else ""}/>' for i in (1, 0))
     + waist + ''.join(f'<circle cx="{x}" cy="1150" r="6" fill="#fff"/>' for x in range(330, 680, 50))),
    ('p11', '格子裙', pants(SKIRT) + waist + stroke('M330 1060 L670 1060 M314 1120 L686 1120', PAD, 10)
     + stroke('M400 1000 L380 1186 M500 1000 L500 1194 M600 1000 L620 1186', PAD, 10) + stroke('M322 1090 L678 1090 M450 1000 L440 1192 M550 1000 L560 1192', '#fff', 4, ' opacity=".6"')),
    ('p12', '盔甲護腿', pants('M340 990 L660 990 L676 1130 L324 1130 Z') + waist + sym('<rect x="394" y="1180" width="96" height="140" rx="20" fill="#b9c1d0"/>') + sym('<ellipse cx="442" cy="1180" rx="52" ry="30" fill="#d6dbe5"/>')),
]

# ---------- 鞋子 ----------
def shoes(one):
    """one(cx) 畫左腳，右腳自動鏡像"""
    return one(440) + MIR(one(440))


SHOES = [
    ('z1', '球鞋', shoes(lambda x: f'<path d="M{x - 50} 1392 Q{x - 58} 1334 {x - 24} 1322 L{x + 30} 1322 Q{x + 54} 1334 {x + 48} 1392 Z" fill="{SH}"/>'
                      f'<rect x="{x - 56}" y="1376" width="110" height="20" rx="10" fill="#fff"/>' + stroke(f'M{x - 18} 1340 L{x + 18} 1340 M{x - 18} 1356 L{x + 18} 1356', '#fff', 6))),
    ('z2', '皮鞋', shoes(lambda x: f'<path d="M{x - 52} 1392 Q{x - 56} 1336 {x - 20} 1330 L{x + 26} 1330 Q{x + 52} 1338 {x + 46} 1392 Z" fill="{SH}"/>'
                      f'<rect x="{x - 56}" y="1382" width="106" height="14" rx="6" fill="#2b2b33"/><ellipse cx="{x - 18}" cy="1350" rx="14" ry="7" fill="#fff" opacity=".5"/>')),
    ('z3', '靴子', shoes(lambda x: f'<path d="M{x - 44} 1200 L{x + 40} 1200 L{x + 44} 1330 Q{x + 58} 1350 {x + 50} 1394 L{x - 54} 1394 Q{x - 60} 1350 {x - 44} 1330 Z" fill="{SH}"/>'
                      f'<rect x="{x - 50}" y="1192" width="96" height="30" rx="12" fill="{SH}"/><rect x="{x - 50}" y="1192" width="96" height="30" rx="12" {shade(.2)}/><rect x="{x - 58}" y="1380" width="114" height="16" rx="6" fill="#3b2a24"/>')),
    ('z4', '涼鞋', shoes(lambda x: f'<ellipse cx="{x - 4}" cy="1372" rx="40" ry="24" fill="{SK}"/><rect x="{x - 56}" y="1382" width="106" height="14" rx="7" fill="{SH}"/>'
                      + stroke(f'M{x - 38} 1360 L{x + 30} 1360 M{x - 30} 1340 L{x - 4} 1376 L{x + 22} 1340', SH, 10))),
    ('z5', '雨鞋', shoes(lambda x: f'<path d="M{x - 46} 1190 L{x + 42} 1190 L{x + 46} 1336 Q{x + 58} 1352 {x + 50} 1394 L{x - 54} 1394 Q{x - 62} 1350 {x - 46} 1336 Z" fill="{SH}"/>'
                      + stroke(f'M{x - 30} 1214 L{x - 30} 1330', '#fff', 10, ' opacity=".45"') + f'<rect x="{x - 58}" y="1380" width="114" height="16" rx="6" {shade(.3)}/>')),
    ('z6', '帆布鞋', shoes(lambda x: f'<path d="M{x - 50} 1392 Q{x - 56} 1332 {x - 22} 1324 L{x + 28} 1324 Q{x + 54} 1334 {x + 48} 1392 Z" fill="{SH}"/>'
                        f'<path d="M{x - 54} 1392 Q{x - 52} 1356 {x - 2} 1354 Q{x + 48} 1356 {x + 50} 1392 Z" fill="#fff"/><rect x="{x - 58}" y="1380" width="112" height="16" rx="8" fill="#fff" stroke="#d9d6e3" stroke-width="3"/>'
                        + stroke(f'M{x - 16} 1336 L{x + 16} 1344 M{x - 16} 1344 L{x + 16} 1336', '#fff', 5))),
    ('z7', '魔法尖頭鞋', shoes(lambda x: f'<path d="M{x + 42} 1392 L{x - 30} 1392 Q{x - 80} 1392 {x - 100} 1350 Q{x - 70} 1366 {x - 40} 1340 Q{x - 20} 1324 {x + 30} 1326 Q{x + 52} 1340 {x + 42} 1392 Z" fill="{SH}"/>'
                           f'<circle cx="{x - 100}" cy="1346" r="10" fill="#ffc531"/>')),
    ('z8', '兔兔拖鞋', shoes(lambda x: f'<ellipse cx="{x - 22}" cy="1312" rx="12" ry="30" fill="{SH}" transform="rotate(-14 {x - 22} 1340)"/><ellipse cx="{x + 18}" cy="1312" rx="12" ry="30" fill="{SH}" transform="rotate(14 {x + 18} 1340)"/>'
                          f'<ellipse cx="{x - 2}" cy="1368" rx="58" ry="32" fill="{SH}"/><circle cx="{x - 18}" cy="1360" r="5" fill="#2b2b33"/><circle cx="{x + 14}" cy="1360" r="5" fill="#2b2b33"/><circle cx="{x - 2}" cy="1372" r="5" fill="#ff8fb3"/>')),
]


# ---------- 手持物（握在右手，握點 HOLD） ----------
def held(s):
    return f'<g transform="translate({HOLD[0]} {HOLD[1]})">{s}</g>'


HANDS = [
    ('k1', '麥克風', held('<g transform="rotate(-8)"><rect x="-16" y="-120" width="32" height="170" rx="14" fill="#2b2b33"/><circle cx="0" cy="-150" r="44" fill="#8b8f9c"/>'
                       + stroke('M-40 -158 h80 M-38 -138 h76 M-18 -188 v76 M18 -188 v76', '#5c606c', 5) + f'<rect x="-22" y="-112" width="44" height="22" rx="6" fill="{C2}"/></g>')),
    ('k2', '星星魔法棒', held(stroke('M0 50 L18 -150', '#8d6e63', 16) + star(22, -184, 50, '#ffc531') + star(22, -184, 22, '#fff6b0'))),
    ('k3', '書本', held(f'<g transform="rotate(-8)"><rect x="-176" y="-130" width="196" height="160" rx="12" fill="{C2}"/><rect x="-176" y="-130" width="196" height="160" rx="12" {shade(.12)}/>'
                     f'<rect x="-166" y="-122" width="176" height="144" rx="8" fill="{C2}"/><rect x="-140" y="-90" width="120" height="16" rx="6" fill="#fff" opacity=".7"/></g>')),
    ('k4', '氣球', held(stroke('M0 0 Q90 -140 200 -300', '#8b8f9c', 5) + f'<ellipse cx="216" cy="-400" rx="82" ry="98" fill="{C2}"/><ellipse cx="186" cy="-436" rx="18" ry="30" fill="#fff" opacity=".45"/><path d="M204 -304 L228 -304 L216 -290 Z" fill="{C2}"/>')),
    ('k5', '冰淇淋', held('<path d="M-38 -30 L38 -30 L0 60 Z" fill="#e8b46a"/>' + stroke('M-26 -14 L14 40 M26 -14 L-14 40', '#c48a3f', 5)
                       + f'<circle cx="0" cy="-70" r="46" fill="{C2}"/><circle cx="-28" cy="-38" r="22" fill="{C2}"/><circle cx="28" cy="-40" r="22" fill="{C2}"/><circle cx="0" cy="-128" r="34" fill="#fff4e0"/><circle cx="6" cy="-168" r="12" fill="#e2553b"/>')),
    ('k6', '平板', held(f'<g transform="rotate(-6)"><rect x="-200" y="-150" width="230" height="170" rx="20" fill="#2b2b33"/><rect x="-186" y="-136" width="202" height="142" rx="10" fill="{C2}" opacity=".85"/>'
                     '<circle cx="-120" cy="-80" r="24" fill="#fff" opacity=".7"/><rect x="-80" y="-60" width="80" height="14" rx="7" fill="#fff" opacity=".7"/></g>')),
    ('k7', '籃球', held('<circle cx="0" cy="-74" r="76" fill="#f28c28"/>' + stroke('M-76 -74 L76 -74 M0 -150 L0 2 M-52 -128 Q-10 -74 -52 -20 M52 -128 Q10 -74 52 -20', '#7a3b12', 6))),
    ('k8', '畫筆', held(stroke('M-10 60 L30 -150', '#c48a3f', 18) + f'<rect x="20" y="-170" width="26" height="30" rx="4" fill="#9aa3b5" transform="rotate(11 33 -155)"/><path d="M28 -168 Q40 -220 52 -170 Z" fill="{C2}"/>')),
    ('k9', '花束', held('<path d="M-30 40 L-60 -70 L60 -70 L30 40 Z" fill="#fff" opacity=".9"/>' + stroke('M0 30 L-30 -110 M0 30 L0 -130 M0 30 L30 -110', '#5bb36a', 8)
                     + ''.join(f'<circle cx="{x + 16 * math.cos(math.radians(a)):.0f}" cy="{y + 16 * math.sin(math.radians(a)):.0f}" r="14" fill="{col}"/>' for x, y, col in [(-34, -130, '#ff8fb3'), (0, -150, C2), (34, -130, '#ffc531')] for a in range(0, 360, 72))
                     + ''.join(f'<circle cx="{x}" cy="{y}" r="9" fill="#fff6b0"/>' for x, y in [(-34, -130), (0, -150), (34, -130)]))),
    ('k10', '加油旗', held(stroke('M0 60 L0 -260', '#8d6e63', 12) + f'<path d="M6 -256 L190 -210 L6 -150 Z" fill="{C2}"/>' + star(70, -206, 24, '#fff'))),
    ('k11', '獎盃', held('<rect x="-50" y="10" width="100" height="30" rx="8" fill="#8d6e63"/><rect x="-14" y="-60" width="28" height="74" fill="#e6a700"/>'
                      '<path d="M-70 -200 L70 -200 Q70 -80 0 -60 Q-70 -80 -70 -200 Z" fill="#ffc531"/>' + stroke('M-70 -180 Q-112 -170 -100 -130 Q-90 -110 -60 -112 M70 -180 Q112 -170 100 -130 Q90 -110 60 -112', '#ffc531', 12)
                      + star(0, -144, 26, '#fff6b0'))),
    ('k12', '珍珠奶茶', held('<path d="M-46 -150 L46 -150 L36 40 L-36 40 Z" fill="#e8c9a0" opacity=".95"/><path d="M-50 -170 L50 -170 L46 -146 L-46 -146 Z" fill="#fff"/>'
                          + stroke('M14 -170 L36 -260', C2, 14) + ''.join(f'<circle cx="{x}" cy="{y}" r="9" fill="#3b2a24"/>' for x, y in [(-20, 20), (0, 26), (20, 18), (-10, 4), (12, 2), (-24, -4)]))),
]

# ---------- 背後 ----------
BACKS = [
    {'id': 'q1', 'name': '後背包', 'svg': f'<rect x="300" y="690" width="400" height="330" rx="70" fill="{BK}"/><rect x="300" y="690" width="400" height="330" rx="70" {shade(.12)}/>',
     'front': sym(f'<path d="M404 716 L428 716 L424 980 L398 980 Z" fill="{BKD}"/>') + sym(f'<rect x="388" y="900" width="44" height="24" rx="6" fill="{BKD}"/>')},
    {'id': 'q2', 'name': '披風', 'svg': f'<path d="M370 716 Q250 1000 212 1316 Q500 1356 788 1316 Q750 1000 630 716 Z" fill="{BK}"/><path d="M370 716 Q250 1000 212 1316 Q300 1330 330 1326 Q340 1000 400 740 Z" {shade(.15)}/>',
     'front': sym(f'<path d="M380 712 Q440 700 470 730 L440 760 Z" fill="{BKD}"/>') + '<circle cx="500" cy="738" r="20" fill="#ffc531"/>'},
    {'id': 'q3', 'name': '天使翅膀', 'svg': sym('<g fill="#ffffff" stroke="#d9d6e3" stroke-width="5"><path d="M380 760 Q250 600 120 650 Q150 700 140 740 Q180 760 172 800 Q220 818 214 860 Q270 870 276 910 Q330 900 380 860 Z"/>'
                                               '<path d="M372 800 Q280 760 214 790 Q240 820 236 850 Q290 860 300 890 Q340 880 372 860 Z"/></g>')},
    {'id': 'q4', 'name': '蝴蝶翅膀', 'svg': sym(f'<path d="M420 780 Q300 560 150 620 Q110 760 300 830 Z" fill="{BK}"/><path d="M420 820 Q300 840 210 950 Q260 1040 400 900 Z" fill="{BK}"/><path d="M420 820 Q300 840 210 950 Q260 1040 400 900 Z" {shade(.12)}/>'
                                              '<circle cx="230" cy="680" r="30" fill="#fff" opacity=".7"/><circle cx="300" cy="740" r="18" fill="#fff" opacity=".7"/><circle cx="290" cy="930" r="20" fill="#fff" opacity=".7"/>')},
    {'id': 'q5', 'name': '火箭背包', 'svg': sym(f'<path d="M270 1010 Q290 1100 310 1010 Q300 1150 330 1010 Z" fill="#ffc531"/><path d="M282 1010 Q300 1070 318 1010 Z" fill="#ff6f3c"/>'
                                              f'<rect x="262" y="720" width="80" height="290" rx="40" fill="{BK}"/><rect x="262" y="720" width="80" height="290" rx="40" {shade(.12)}/><rect x="276" y="740" width="22" height="200" rx="11" fill="#fff" opacity=".35"/>'
                                              '<rect x="268" y="990" width="68" height="34" rx="8" fill="#6c7383"/>')},
    {'id': 'q6', 'name': '吉他', 'svg': f'<g transform="rotate(-40 500 900)"><rect x="472" y="420" width="56" height="420" rx="10" fill="#8d6e63"/><rect x="462" y="380" width="76" height="70" rx="16" fill="#5c3d2e"/>'
                                     f'<circle cx="500" cy="1000" r="140" fill="{BK}"/><circle cx="500" cy="860" r="104" fill="{BK}"/><circle cx="500" cy="930" r="40" fill="#3b2a24"/><rect x="456" y="1040" width="88" height="20" rx="6" fill="#3b2a24"/></g>',
     'front': stroke('M636 720 L360 1010', BKD, 24)},
]


# ---------- 夥伴（以腳底中心為原點畫） ----------
def pet_eyes(y=-150, dx=22):
    return f'<circle cx="{-dx}" cy="{y}" r="9" fill="#2b2b33"/><circle cx="{dx}" cy="{y}" r="9" fill="#2b2b33"/><circle cx="{-dx + 3}" cy="{y - 3}" r="3" fill="#fff"/><circle cx="{dx + 3}" cy="{y - 3}" r="3" fill="#fff"/>'


PETS_RAW = [
    ('x1', '小貓', stroke('M46 -40 Q120 -60 104 -150', PET, 24) + f'<ellipse cx="0" cy="-62" rx="66" ry="62" fill="{PET}"/><ellipse cx="0" cy="-50" rx="38" ry="40" fill="#fff" opacity=".55"/>'
     + f'<path d="M-56 -168 L-48 -232 L-10 -196 Z" fill="{PET}"/><path d="M56 -168 L48 -232 L10 -196 Z" fill="{PET}"/><path d="M-46 -184 L-42 -216 L-22 -198 Z" fill="#ffb3c7"/><path d="M46 -184 L42 -216 L22 -198 Z" fill="#ffb3c7"/>'
     + f'<circle cx="0" cy="-150" r="60" fill="{PET}"/>' + pet_eyes() + '<path d="M-7 -132 L7 -132 L0 -124 Z" fill="#ff8fb3"/>' + stroke('M-12 -116 Q-6 -110 0 -118 Q6 -110 12 -116', '#2b2b33', 4)
     + stroke('M-30 -128 L-74 -134 M-30 -120 L-72 -112 M30 -128 L74 -134 M30 -120 L72 -112', '#2b2b33', 3, ' opacity=".6"') + '<ellipse cx="-24" cy="-6" rx="20" ry="12" fill="#fff"/><ellipse cx="24" cy="-6" rx="20" ry="12" fill="#fff"/>'),
    ('x2', '小狗', stroke('M50 -50 Q100 -70 96 -120', PET, 20) + f'<ellipse cx="0" cy="-62" rx="64" ry="62" fill="{PET}"/>'
     + f'<circle cx="0" cy="-150" r="62" fill="{PET}"/><ellipse cx="-58" cy="-140" rx="22" ry="44" fill="{PETD}" transform="rotate(16 -58 -140)"/><ellipse cx="58" cy="-140" rx="22" ry="44" fill="{PETD}" transform="rotate(-16 58 -140)"/>'
     + '<ellipse cx="0" cy="-120" rx="34" ry="26" fill="#fff"/>' + pet_eyes(-160) + '<ellipse cx="0" cy="-130" rx="11" ry="8" fill="#2b2b33"/><path d="M-8 -112 Q0 -96 8 -112 Z" fill="#ff8fb3"/>'
     + '<ellipse cx="-24" cy="-6" rx="20" ry="12" fill="#fff"/><ellipse cx="24" cy="-6" rx="20" ry="12" fill="#fff"/>'),
    ('x3', '小鳥', f'<path d="M-60 -110 L-104 -150 L-96 -90 Z" fill="{PETD}"/><circle cx="0" cy="-90" r="72" fill="{PET}"/><ellipse cx="0" cy="-64" rx="44" ry="40" fill="#fff" opacity=".6"/>'
     + f'<ellipse cx="-54" cy="-86" rx="22" ry="40" fill="{PETD}" transform="rotate(20 -54 -86)"/><path d="M-8 -168 Q0 -200 12 -170 Q20 -196 24 -162 Z" fill="{PETD}"/>' + pet_eyes(-110, 24)
     + '<path d="M-12 -92 L12 -92 L0 -74 Z" fill="#ffb300"/>' + stroke('M-20 -18 L-20 0 M20 -18 L20 0 M-30 0 L-10 0 M10 0 L30 0', '#ffb300', 6)),
    ('x4', '機器人', f'<rect x="-48" y="-30" width="30" height="30" rx="8" fill="#6c7383"/><rect x="18" y="-30" width="30" height="30" rx="8" fill="#6c7383"/><rect x="-62" y="-130" width="124" height="104" rx="22" fill="{PET}"/>'
     + '<rect x="-34" y="-104" width="68" height="50" rx="10" fill="#fff" opacity=".6"/><circle cx="-14" cy="-80" r="8" fill="#e2553b"/><circle cx="14" cy="-80" r="8" fill="#ffc531"/>'
     + '<rect x="-58" y="-232" width="116" height="94" rx="26" fill="#c9ccd6"/><rect x="-44" y="-214" width="88" height="56" rx="16" fill="#2b2b33"/><circle cx="-20" cy="-186" r="10" fill="#7cf0ff"/><circle cx="20" cy="-186" r="10" fill="#7cf0ff"/>'
     + stroke('M0 -232 L0 -262', '#6c7383', 6) + f'<circle cx="0" cy="-268" r="12" fill="{PET}"/>'),
    ('x5', '小兔', f'<ellipse cx="-24" cy="-236" rx="18" ry="56" fill="{PET}" transform="rotate(-10 -24 -200)"/><ellipse cx="24" cy="-236" rx="18" ry="56" fill="{PET}" transform="rotate(10 24 -200)"/>'
     + '<ellipse cx="-24" cy="-236" rx="8" ry="40" fill="#ffb3c7" transform="rotate(-10 -24 -200)"/><ellipse cx="24" cy="-236" rx="8" ry="40" fill="#ffb3c7" transform="rotate(10 24 -200)"/>'
     + f'<circle cx="64" cy="-40" r="22" fill="#fff"/><ellipse cx="0" cy="-60" rx="62" ry="60" fill="{PET}"/><circle cx="0" cy="-150" r="56" fill="{PET}"/>' + pet_eyes(-156, 20)
     + '<path d="M-6 -136 L6 -136 L0 -128 Z" fill="#ff8fb3"/><ellipse cx="-34" cy="-128" rx="12" ry="7" fill="#ff9e9e" opacity=".6"/><ellipse cx="34" cy="-128" rx="12" ry="7" fill="#ff9e9e" opacity=".6"/>'
     + '<ellipse cx="-24" cy="-6" rx="22" ry="12" fill="#fff"/><ellipse cx="24" cy="-6" rx="22" ry="12" fill="#fff"/>'),
    ('x6', '小恐龍', f'<path d="M50 -40 Q140 -30 150 -90 Q120 -20 50 -10 Z" fill="{PET}"/><ellipse cx="0" cy="-64" rx="66" ry="64" fill="{PET}"/><ellipse cx="0" cy="-56" rx="38" ry="44" fill="#fff4cc"/>'
     + ''.join(f'<path d="M{x} {y} l12 -22 l12 22 Z" fill="{PETD}"/>' for x, y in [(-20, -214), (6, -218), (32, -206)])
     + f'<ellipse cx="6" cy="-156" rx="66" ry="58" fill="{PET}"/>' + pet_eyes(-166, 24) + stroke('M-16 -132 Q6 -118 30 -132', '#2b2b33', 5)
     + '<circle cx="-14" cy="-144" r="4" fill="#2b2b33" opacity=".4"/><circle cx="26" cy="-144" r="4" fill="#2b2b33" opacity=".4"/>'
     + stroke('M-46 -80 L-62 -66 M46 -80 L62 -66', PET, 14) + f'<ellipse cx="-26" cy="-4" rx="24" ry="12" fill="{PETD}"/><ellipse cx="26" cy="-4" rx="24" ry="12" fill="{PETD}"/>'),
]
PET_FULL = 'translate(830 1396)'
PET_HALF = 'translate(160 1000) scale(.82)'
PETS = [{'id': i, 'name': n, 'svg': f'<g transform="{PET_FULL}">{s}</g>', 'half': f'<g transform="{PET_HALF}">{s}</g>'} for i, n, s in PETS_RAW]

# ---------- 表情（覆蓋眼睛、嘴巴、眉毛，再加一層特效） ----------
CLOSED_DOWN = both(lambda x: stroke(f'M{x - 30} {EYE_Y + 8} Q{x} {EYE_Y - 22} {x + 30} {EYE_Y + 8}', INK, 12))
EXPR = {
    'normal': {'name': '一般'},
    'happy': {'name': '開心', 'eyes': {'open': both(lambda x: stroke(f'M{x - 32} {EYE_Y + 12} Q{x} {EYE_Y - 30} {x + 32} {EYE_Y + 12}', INK, 14)), 'blink': CLOSED_DOWN},
              'mouth': {'closed': f'<path d="M436 510 Q500 600 564 510 Z" fill="{MOUTH_IN}"/><path d="M450 512 L550 512 L544 528 L456 528 Z" fill="#fff"/><path d="M470 566 Q500 584 530 566 Q500 552 470 566 Z" fill="{TONGUE}"/>',
                        'open': f'<path d="M428 504 Q500 640 572 504 Z" fill="{MOUTH_IN}"/><path d="M446 508 L554 508 L548 526 L452 526 Z" fill="#fff"/><path d="M462 584 Q500 612 538 584 Q500 562 462 584 Z" fill="{TONGUE}"/>'},
              'over': '<ellipse cx="350" cy="492" rx="34" ry="18" fill="#ff8fa8" opacity=".5"/><ellipse cx="650" cy="492" rx="34" ry="18" fill="#ff8fa8" opacity=".5"/>'},
    'surprised': {'name': '驚訝', 'brow': both(lambda x: stroke(f'M{x - 32} 330 Q{x} 300 {x + 32} 330', H2, 12)),
                  'mouth': {'closed': f'<ellipse cx="500" cy="540" rx="20" ry="26" fill="{MOUTH_IN}"/>', 'open': f'<ellipse cx="500" cy="546" rx="32" ry="42" fill="{MOUTH_IN}"/><ellipse cx="500" cy="572" rx="18" ry="10" fill="{TONGUE}"/>'},
                  'over': stroke('M700 300 L740 268 M716 330 L766 322 M690 270 L700 222', '#2b2b33', 8)},
    'angry': {'name': '生氣', 'brow': stroke('M370 330 L446 360', H2, 15) + stroke('M630 330 L554 360', H2, 15),
              'mouth': {'closed': stroke('M452 548 Q500 512 548 548', LIP, 14), 'open': f'<path d="M444 556 Q500 486 556 556 Z" fill="{MOUTH_IN}"/><rect x="462" y="532" width="76" height="14" rx="6" fill="#fff"/>'},
              'over': stroke('M660 250 Q680 270 700 250 M690 222 Q670 242 690 262 M720 252 Q700 272 720 292 M690 282 Q710 262 730 282', '#e2553b', 10)},
    'cry': {'name': '哭哭', 'brow': stroke('M376 356 L444 336', H2, 13) + stroke('M624 356 L556 336', H2, 13), 'eyes': {'open': CLOSED_DOWN, 'blink': CLOSED_DOWN},
            'mouth': {'closed': stroke('M448 548 Q474 530 500 548 Q526 566 552 548', LIP, 12), 'open': f'<path d="M446 562 Q500 470 554 562 Q500 548 446 562 Z" fill="{MOUTH_IN}"/>'},
            'over': both(lambda x: f'<path d="M{x - 14} 420 Q{x - 28} 500 {x - 18} 580 L{x + 6} 580 Q{x - 4} 500 {x + 10} 420 Z" fill="#8ad0ff" opacity=".85"/>')
            + '<path d="M300 520 Q290 548 300 560 Q312 548 300 520 Z" fill="#8ad0ff"/><path d="M704 540 Q694 568 704 580 Q716 568 704 540 Z" fill="#8ad0ff"/>'},
    'shy': {'name': '害羞', 'mouth': {'closed': stroke('M466 536 Q480 524 492 536 Q506 548 520 536 Q532 526 538 534', LIP, 10), 'open': f'<ellipse cx="500" cy="540" rx="18" ry="20" fill="{MOUTH_IN}"/>'},
            'over': '<ellipse cx="356" cy="490" rx="46" ry="26" fill="#ff7f9a" opacity=".55"/><ellipse cx="644" cy="490" rx="46" ry="26" fill="#ff7f9a" opacity=".55"/>'
            + stroke('M330 500 l14 -22 M356 502 l14 -22 M382 500 l14 -22 M610 500 l14 -22 M636 502 l14 -22 M662 500 l14 -22', '#e2557a', 5)},
    'love': {'name': '愛心眼', 'eyes': {'open': both(lambda x: heart(x, EYE_Y + 2, 1.15, '#ff4f7f') + f'<circle cx="{x - 12}" cy="{EYE_Y - 12}" r="7" fill="#fff" opacity=".8"/>'), 'blink': BLINK},
             'over': heart(700, 270, .7, '#ff6f9c') + heart(740, 220, .5, '#ff8fb3')},
    'sleepy': {'name': '想睡', 'eyes': {'open': both(lambda x: stroke(f'M{x - 30} {EYE_Y + 6} Q{x} {EYE_Y + 22} {x + 30} {EYE_Y + 6}', INK, 10)), 'blink': BLINK},
               'mouth': {'closed': f'<ellipse cx="500" cy="540" rx="12" ry="14" fill="{MOUTH_IN}"/>', 'open': f'<ellipse cx="500" cy="544" rx="24" ry="30" fill="{MOUTH_IN}"/>'},
               'over': stroke('M672 268 L702 268 L672 298 L702 298 M716 210 L756 210 L716 250 L756 250', '#6c7aa8', 8)},
    'wink': {'name': '眨眼', 'eyes': {'open': f'<circle cx="{EYE_L}" cy="{EYE_Y}" r="28" fill="{EY}"/><circle cx="{EYE_L + 10}" cy="{EYE_Y - 10}" r="10" fill="#fff"/>'
                                              + stroke(f'M{EYE_R - 30} {EYE_Y - 14} L{EYE_R + 24} {EYE_Y + 2} L{EYE_R - 30} {EYE_Y + 18}', INK, 12), 'blink': BLINK},
             'over': star(690, 290, 24, '#ffc531')},
}

VIEW = {'face': '200 150 600 600', 'hair': '110 30 780 780', 'brow': '270 220 460 460', 'eyes': '290 270 420 420', 'mouth': '330 400 340 340', 'nose': '340 330 320 320',
        'deco': '240 260 520 520', 'glasses': '240 200 520 520', 'hat': '110 20 780 780', 'headset': '180 120 640 640', 'top': '220 640 560 560', 'coat': '220 640 560 560',
        'bottom': '250 950 500 500', 'shoes': '320 1180 360 360', 'hand': '300 440 640 640', 'back': '60 560 880 880', 'pet': '700 1130 260 260',
        'expr': '270 220 460 460', 'pose': '0 0 1000 1400'}

DEFAULTS = {'face': 'f1', 'hair': 'h1', 'brow': 'b1', 'eyes': 'e1', 'mouth': 'm1', 'nose': '', 'deco': 'd1', 'glasses': '', 'hat': '', 'headset': '',
            'top': 't1', 'coat': '', 'bottom': 'p1', 'shoes': 'z1', 'hand': '', 'back': '', 'pet': ''}


def cat(name, opts, none=False, none_name=None):
    c = {'name': name, 'none': none, 'opts': opts}
    if none_name:
        c['noneName'] = none_name
    return c


def build():
    simple = lambda L: [{'id': i, 'name': n, 'svg': s} for i, n, s in L]
    return {
        'format': 2, 'id': 'flat', 'name': '扁平圓潤風', 'version': '2.0', 'date': '2026-11-15', 'author': 'Claude',
        'base': {'neck': NECK, 'ears': EARS, 'legs': LEGS, 'arms': arms()},
        'poses': POSES, 'expr': EXPR, 'defaults': DEFAULTS, 'view': VIEW,
        'cats': {
            'face': cat('臉型', simple(FACE)),
            'hair': cat('髮型', [dict({'id': i, 'name': n, 'front': f}, **({'back': b} if b else {})) for i, n, b, f in HAIR], True, '光頭'),
            'brow': cat('眉毛', simple(BROW), True),
            'eyes': cat('眼睛', [{'id': i, 'name': n, 'open': s, 'blink': BLINK} for i, n, s in EYES]),
            'mouth': cat('嘴巴', [{'id': i, 'name': n, 'closed': a, 'open': b} for i, n, a, b in MOUTH]),
            'nose': cat('鼻子', simple(NOSE), True),
            'deco': cat('臉部裝飾', simple(DECO), True),
            'glasses': cat('眼鏡', simple(GLASS), True),
            'hat': cat('帽子頭飾', simple(HATS), True),
            'headset': cat('耳機麥克風', simple(HEADSET), True),
            'top': cat('上衣', TOPS),
            'coat': cat('外套', COATS, True),
            'bottom': cat('下身', simple(BOTTOMS)),
            'shoes': cat('鞋子', simple(SHOES), True, '赤腳'),
            'hand': cat('手持物', simple(HANDS), True),
            'back': cat('背後', BACKS, True),
            'pet': cat('夥伴', PETS, True),
        }}


if __name__ == '__main__':
    p = build()
    out = sys.argv[1] if len(sys.argv) > 1 else 'packs/flat/pack.json'
    import os
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    json.dump(p, open(out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('ok', out, sum(len(c['opts']) for c in p['cats'].values()), '個部件')
