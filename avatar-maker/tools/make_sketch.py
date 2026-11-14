#!/usr/bin/env python3
"""Hand-drawn picture-book wardrobe, format 2.

Run from avatar-maker: python tools/make_sketch.py packs/sketch/pack.json
All artwork is authored here. Only joint coordinates and pose metadata are shared.
Paths use absolute coordinates; seeded sub-pixel/1.3px perturbations and irregular
ellipse contours give the ink a quiet pencil wobble, without filters or gradients.
"""
import datetime
import json
import math
from pathlib import Path
import random
import re
import sys

from make_flat import ARMS_GEO, HOLD, POSES

INK = '#2d2a32'
PAPER = '#fff5df'
SK, SK2, H, H2 = '{skin}', '{skin2}', '{hair}', '{hair2}'
C, CD, C2 = '{c1}', '{c1d}', '{c2}'
CO, COD, PA, PAD = '{coat}', '{coatd}', '{pants}', '{pantsd}'
RNG = random.Random(271828)


def path(d, fill='none', ink=INK, w=8, opacity=None, jitter=True):
    if jitter:
        d = re.sub(r'-?\d+(?:\.\d+)?',
                   lambda m: f'{float(m[0]) + RNG.uniform(-1.3, 1.3):.1f}', d)
    op = f' opacity="{opacity}"' if opacity is not None else ''
    return (f'<path d="{d}" fill="{fill}" stroke="{ink}" stroke-width="{w}"'
            f' stroke-linecap="round" stroke-linejoin="round"{op}/>')


def oval(x, y, rx, ry, fill, ink=INK, w=8, opacity=None):
    # Closed Catmull-Rom contour: twelve slightly unequal arcs, no perfect circles.
    pts = []
    for i in range(12):
        a = i * math.tau / 12
        q = RNG.uniform(.985, 1.015)
        pts.append((x + rx * math.cos(a) * q, y + ry * math.sin(a) * q))
    d = f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
    for i in range(12):
        p0, p1, p2, p3 = [pts[j % 12] for j in (i-1, i, i+1, i+2)]
        d += (f' C{p1[0]+(p2[0]-p0[0])/6:.1f} {p1[1]+(p2[1]-p0[1])/6:.1f}'
              f' {p2[0]-(p3[0]-p1[0])/6:.1f} {p2[1]-(p3[1]-p1[1])/6:.1f}'
              f' {p2[0]:.1f} {p2[1]:.1f}')
    return path(d+' Z', fill, ink, w, opacity, jitter=False)


def box(x, y, w, h, fill, r=12, ink=INK):
    return path(f'M{x+r} {y} L{x+w-r} {y} Q{x+w} {y} {x+w} {y+r}'
                f' L{x+w} {y+h-r} Q{x+w} {y+h} {x+w-r} {y+h}'
                f' L{x+r} {y+h} Q{x} {y+h} {x} {y+h-r}'
                f' L{x} {y+r} Q{x} {y} {x+r} {y} Z', fill, ink)


def group(s, transform):
    return f'<g transform="{transform}">{s}</g>'


def mirror(s):
    return group(s, 'matrix(-1 0 0 1 1000 0)')


def pair(s):
    return s + mirror(s)


def wash(x, y, w, h, color=PAPER, alpha=.28):
    # Two ragged, translucent wax-pencil swatches; deliberately restrained.
    s = path(f'M{x} {y+5} L{x+w*.7} {y} L{x+w} {y+8}'
             f' L{x+w-6} {y+h*.7} L{x+w*.6} {y+h} L{x+4} {y+h-5} Z',
             color, 'none', 0, alpha)
    s += path(f'M{x+8} {y+9} L{x+w-12} {y+5} L{x+w-16} {y+14} L{x+6} {y+19} Z',
              color, 'none', 0, alpha*.6)
    return s


def star(x, y, r, fill=C2):
    pts = []
    for i in range(10):
        a = i*math.pi/5-math.pi/2
        rr = r if i % 2 == 0 else r*.46
        pts.append((x+math.cos(a)*rr, y+math.sin(a)*rr))
    return path('M'+' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts)+' Z', fill, w=7)


def heart(x, y, r, fill=C2):
    return path(f'M{x} {y+r} C{x-r*2} {y-r*.3} {x-r} {y-r*1.5} {x} {y-r*.5}'
                f' C{x+r} {y-r*1.5} {x+r*2} {y-r*.3} {x} {y+r} Z', fill, w=7)


def stitch(d, color=INK):
    return path(d, ink=color, w=7)


def blush():
    return pair(oval(349, 478, 32, 23, '#de897f', 'none', 0, .25)
                + wash(330, 471, 33, 10, '#efa59a', .24))


def arms():
    out = {}
    for key, (s, e, v, kind) in ARMS_GEO.items():
        # Rebuilt ribbon contours around the shared centreline. Shoulder caps
        # overlap the torso by 35px, so raised arms never detach at the seam.
        def ribbon(end, radius, fill):
            pts = [s, e, end] if end == v else [s, end]
            normals = []
            for i, p in enumerate(pts):
                a, b = pts[max(0, i-1)], pts[min(len(pts)-1, i+1)]
                dx, dy = b[0]-a[0], b[1]-a[1]
                ln = math.hypot(dx, dy)
                normals.append((-dy/ln*radius, dx/ln*radius))
            a = [(p[0]+n[0], p[1]+n[1]) for p, n in zip(pts, normals)]
            b = [(p[0]-n[0], p[1]-n[1]) for p, n in zip(pts, normals)]
            d = f'M{a[0][0]} {a[0][1]}'
            d += ''.join(f' L{x} {y}' for x, y in a[1:])
            d += f' Q{end[0]+(end[0]-pts[-2][0])*.09} {end[1]+(end[1]-pts[-2][1])*.09} {b[-1][0]} {b[-1][1]}'
            d += ''.join(f' L{x} {y}' for x, y in reversed(b[:-1]))
            d += f' Q{s[0]-(pts[1][0]-s[0])*.3} {s[1]-(pts[1][1]-s[1])*.3} {a[0][0]} {a[0][1]} Z'
            return path(d, fill)
        short = (s[0]+(e[0]-s[0])*.53, s[1]+(e[1]-s[1])*.53)
        dx, dy = v[0]-e[0], v[1]-e[1]
        ln = math.hypot(dx, dy)
        hx, hy = v[0]+dx/ln*13, v[1]+dy/ln*13
        if kind == 'open':
            hand = path(f'M{hx-26} {hy+22} L{hx-29} {hy-23} Q{hx-30} {hy-50} {hx-17} {hy-43}'
                        f' L{hx-10} {hy-22} L{hx-10} {hy-52} Q{hx} {hy-64} {hx+8} {hy-50}'
                        f' L{hx+12} {hy-23} Q{hx+29} {hy-58} {hx+36} {hy-33}'
                        f' L{hx+30} {hy} Q{hx+55} {hy-19} {hx+54} {hy+1}'
                        f' Q{hx+33} {hy+45} {hx} {hy+38} Z', SK)
        elif kind == 'thumb':
            hand = path(f'M{hx-30} {hy+25} L{hx-29} {hy-15} L{hx-10} {hy-25}'
                        f' L{hx-12} {hy-61} Q{hx+4} {hy-81} {hx+15} {hy-57}'
                        f' L{hx+18} {hy-22} Q{hx+48} {hy-17} {hx+38} {hy+25}'
                        f' Q{hx+5} {hy+43} {hx-30} {hy+25} Z', SK)
        else:
            hand = oval(hx, hy, 29, 32, SK)
        hand += stitch(f'M{hx-12} {hy+3} Q{hx} {hy-7} {hx+16} {hy+3}', SK2)
        out[key] = {'skin': ribbon(v, 25, SK), 'long': ribbon(v, 29, '{sleeve}'),
                    'short': ribbon(short, 31, '{sleeve}'), 'hand': hand}
    return out


def faces():
    shapes = [
        ('柔和鵝蛋臉', 'M295 400 C291 267 371 208 496 207 C632 201 710 284 706 416 C711 551 616 648 503 652 C384 649 290 548 295 400 Z'),
        ('圓圓蘋果臉', 'M285 413 C279 284 372 212 498 214 C634 209 718 301 714 430 C716 557 628 643 501 646 C377 648 282 551 285 413 Z'),
        ('溫柔方臉', 'M292 384 Q285 222 426 214 L572 212 Q713 223 708 388 L701 515 Q684 642 553 650 L451 650 Q310 635 296 520 Z'),
        ('小梨子臉', 'M309 385 C306 264 387 214 499 210 C619 212 693 282 691 399 C739 521 653 647 503 654 C357 654 264 538 309 385 Z')]
    return [{'id': f'f{i}', 'name': n, 'svg': path(d, SK)+wash(321, 361, 30, 89)+blush()}
            for i, (n, d) in enumerate(shapes, 1)]


def hairs():
    # Independent silhouettes and strand directions, all keeping eyes uncovered.
    front = [
        'M285 421 Q255 224 418 187 Q604 146 706 291 L719 424 L678 350 L622 289 Q519 362 411 319 L348 351 Z',
        'M286 453 Q255 204 482 182 Q712 162 722 447 L684 418 L661 323 L607 351 L546 317 L493 350 L433 318 L376 349 L332 327 L319 449 Z',
        'M281 431 Q270 215 451 185 Q664 153 715 375 L721 430 L667 345 Q559 277 500 249 Q444 293 339 342 Z',
        'M286 418 L280 300 L326 314 L346 214 L410 258 L470 177 L523 254 L603 194 L625 286 L689 259 L718 421 L664 343 Q500 295 338 354 Z',
        'M283 426 Q258 203 469 180 Q715 174 718 427 L675 355 Q569 349 502 261 Q434 332 328 356 Z',
        'M285 418 C244 366 273 301 325 294 C300 226 368 184 419 210 C442 139 523 154 550 196 C610 152 669 211 653 258 C723 254 748 332 709 371 L714 424 L668 348 Q570 320 500 285 Q400 338 331 351 Z',
        'M281 440 Q265 196 483 179 Q709 158 721 438 L685 388 Q612 277 518 257 Q457 357 326 349 Z',
        'M286 384 Q292 203 492 195 Q696 182 715 391 L677 332 Q500 271 327 334 Z',
        'M278 465 Q264 205 479 183 Q724 171 723 467 L691 466 L668 318 Q519 333 332 313 L311 468 Z',
        'M282 442 Q253 201 477 177 Q718 164 721 426 L680 348 Q594 293 548 260 Q460 352 331 365 Z',
        'M279 448 Q264 200 494 181 Q717 177 722 450 L686 420 Q652 304 549 258 L500 232 Q412 257 349 334 L312 448 Z',
        'M282 451 Q256 214 462 182 Q685 152 720 401 L709 446 L663 347 L625 314 Q526 404 438 356 Q510 338 528 286 Q428 337 336 356 Z']
    names = ['紙片短髮', '齊瀏海長髮', '高高馬尾', '蓬鬆碎髮', '雙丸子', '雲朵捲髮',
             '兩束辮子', '清爽平頭', '小書僮鮑伯', '側邊長辮', '中分及肩', '舞台翹瀏海']
    out = []
    for i, (n, d) in enumerate(zip(names, front), 1):
        back = ''
        if i in (2, 9, 11):
            end = {2: 873, 9: 611, 11: 741}[i]
            back = path(f'M279 375 Q245 187 496 177 Q748 176 722 390 L743 {end}'
                        f' Q678 {end+26} 616 {end-25} L387 {end-25} Q324 {end+32} 257 {end} Z', H)
            back += pair(wash(276, 490, 23, max(40, end-530), PAPER, .16))
        if i == 3:
            back = path('M657 256 Q853 195 833 396 Q822 583 746 699 L716 658 Q777 490 701 384 Z', H)
            back += stitch('M769 314 Q806 451 761 582', H2)+box(682, 265, 61, 22, C2)
        if i == 5:
            back = pair(oval(320, 219, 75, 76, H)+stitch('M278 213 Q313 173 358 214', H2))
        if i in (7, 10):
            for side in ((270, 730) if i == 7 else (737,)):
                for j in range(7):
                    xx = side+(9 if j % 2 else -9)
                    back += oval(xx, 431+j*43, 30-j*1.4, 30, H)
                    back += stitch(f'M{xx-13} {426+j*43} L{xx+12} {444+j*43}', H2)
                back += box(side-25, 726, 50, 20, C2)
        f = path(d, H)+wash(337, 239, 90, 27, PAPER, .18)
        f += stitch('M352 279 Q381 238 423 230 M581 219 Q635 241 660 284', H2)
        out.append({'id': f'h{i}', 'name': n, 'front': f, **({'back': back} if back else {})})
    return out


def eye_pair(kind):
    s = ''
    for x in (410, 590):
        if kind in (0, 1, 2, 3, 6):
            rx, ry = [(13, 19), (18, 18), (10, 23), (15, 16), (0, 0), (0, 0), (17, 23)][kind]
            s += oval(x, 400, rx, ry, '{eye}', w=7)
            s += oval(x-3, 394, 3.5, 5, PAPER, 'none', 0)
            if kind == 3:
                s += stitch(f'M{x-22} 381 Q{x} 368 {x+20} 381')
            if kind == 6:
                s += stitch(f'M{x-20} 377 L{x-24} 369 M{x+18} 379 L{x+24} 371')
        elif kind == 4:
            s += stitch(f'M{x-23} 405 Q{x} 373 {x+23} 405')
        elif kind == 5:
            s += oval(x, 403, 21, 16, PAPER)+oval(x, 403, 8, 12, '{eye}')
        else:
            s += oval(x, 403, 14, 14, '{eye}')
            s += stitch(f'M{x-23} 384 L{x+21} 384')
    return s


def blink():
    return ''.join(stitch(f'M{x-23} 399 Q{x} 415 {x+23} 398') for x in (410, 590))


def mouths():
    closed = ['M465 527 Q500 551 536 526', 'M457 521 Q500 565 543 520',
              'M478 533 Q500 525 523 533', 'M464 541 Q500 518 535 541',
              'M480 526 Q491 537 501 526 Q513 538 525 526', 'M475 532 L525 532']
    names = ['鉛筆微笑', '大大笑容', '輕聲說話', '小小嘟嘴', '俏皮貓嘴', '認真抿嘴']
    out = []
    for i, (n, d) in enumerate(zip(names, closed), 1):
        width, height = [(28, 19), (39, 28), (17, 24), (22, 17), (27, 20), (24, 25)][i-1]
        o = oval(500, 538, width, height, '#71444b')
        o += path(f'M{500-width*.65} {543+height*.1} Q500 {535+height*.2} {500+width*.65} {543+height*.1}'
                  f' Q500 {538+height*.8} {500-width*.65} {543+height*.1} Z', '#e9a09a', 'none', 0)
        out.append({'id': f'm{i}', 'name': n, 'closed': stitch(d), 'open': o})
    return out


def brows():
    ds = ['M378 353 Q407 342 434 352', 'M377 350 Q410 331 436 350',
          'M380 350 L435 348', 'M381 356 Q402 330 432 339']
    return [{'id': f'b{i}', 'name': n, 'svg': pair(path(d, ink=H2, w=8+i*.3))}
            for i, (n, d) in enumerate(zip(['輕柔彎眉', '濃濃圓眉', '平直眉', '好奇眉'], ds), 1)]


def hats():
    shapes = [
        ('畫家貝雷帽', path('M276 243 Q258 177 401 164 Q585 102 701 205 Q750 270 660 291 L325 294 Z', '{hat}')
         +stitch('M479 162 L485 137')+wash(328, 199, 123, 28)),
        ('學院軟帽', path('M290 296 Q292 166 489 158 Q680 146 710 301 Z', '{hat}')
         +path('M278 296 Q481 266 737 311 L769 334 Q560 319 290 335 Z', '{hat}')+wash(333, 208, 76, 35)),
        ('星光魔法帽', path('M342 259 Q406 171 494 67 Q542 104 561 139 L656 260 Z', '{hat}')
         +oval(500, 268, 243, 35, '{hat}')+star(488, 161, 26, C2)+wash(429, 172, 34, 44)),
        ('雲朵廚師帽', path('M331 217 C260 164 334 85 400 133 C426 65 523 64 548 129 C614 78 705 138 666 215'
                           ' L658 300 L342 300 Z', '{hat}')+stitch('M346 253 L652 251 M419 202 L420 236 M580 197 L578 234')+wash(358, 155, 57, 34)),
        ('消防軟盔', path('M297 281 Q302 131 481 126 Q684 115 704 286 L750 310 L740 342 Q500 310 259 342 L248 310 Z', '{hat}')
         +path('M470 162 L532 163 L547 243 L500 268 L456 242 Z', C2)+stitch('M489 178 L510 231')+wash(332, 192, 60, 45)),
        ('貓咪耳箍', path('M296 280 L305 118 L419 208 Q500 184 583 208 L697 118 L706 283 L670 260'
                        ' Q500 205 330 262 Z', '{hat}')+pair(path('M321 230 L326 162 L377 207 Z', C2))),
        ('節慶毛線帽', path('M292 295 Q298 160 482 157 Q654 115 698 296 Z', '{hat}')
         +box(280, 281, 439, 59, '{hat}', 18)+oval(489, 124, 38, 36, C2)
         +''.join(stitch(f'M{x} 294 L{x-3} 325') for x in range(307, 700, 29))+wash(342, 220, 76, 25)),
        ('舞台蝴蝶結', path('M639 224 Q589 161 552 177 L557 273 Q601 283 639 235'
                          ' Q686 281 724 262 L718 171 Q677 167 639 224 Z', '{hat}')
         +oval(639, 224, 21, 27, C2)+wash(571, 195, 30, 18)),
        ('星際透明盔', path('M260 445 C215 111 756 83 747 440', 'none', '{hat}', 10)
         +pair(box(229, 381, 55, 132, '{hat}', 20))+path('M291 534 Q500 668 710 534 L701 579 Q500 699 300 579 Z', '{hat}')
         +path('M313 278 Q343 218 385 207', ink=PAPER, w=10)),
        ('花園小花冠', stitch('M292 272 Q500 123 706 275', '{hat}'))]
    petals = ''
    for x, y in [(334, 244), (414, 205), (502, 192), (590, 207), (673, 245)]:
        for a in range(5):
            petals += oval(x+math.cos(a*math.tau/5)*17, y+math.sin(a*math.tau/5)*17, 13, 14, '{hat}', w=7)
        petals += oval(x, y, 10, 10, C2, w=7)
    shapes[-1] = (shapes[-1][0], shapes[-1][1]+petals)
    return simple('a', shapes)


def torso(fill=C):
    return path('M383 711 Q430 708 453 712 Q500 745 546 712 L617 714 Q665 720 671 776'
                ' L658 1034 Q501 1052 341 1035 L330 779 Q333 726 383 711 Z', fill)


def collar(fill=PAPER):
    return pair(path('M446 714 L499 747 L472 791 L418 727 Z', fill))


def pocket(x, y, fill):
    return box(x, y, 62, 63, fill, 5)+stitch(f'M{x+5} {y+17} L{x+57} {y+17}')


def garment(i, name, detail, fill=C, sleeve='long'):
    return {'id': i, 'name': name, 'svg': torso(fill)+wash(358, 825, 28, 120)+detail,
            'sleeve': {'type': sleeve, 'fill': fill}}


def tops():
    tie = path('M489 753 L512 752 L517 776 L510 876 L499 889 L487 876 L482 777 Z', C2)
    school = collar()+path('M427 814 L499 861 L572 813', ink=C2, w=10)+pocket(571, 877, CD)
    sport = path('M344 820 L656 818 L654 859 L346 860 Z', C2)+stitch('M448 716 Q500 770 553 715', CD)+box(463, 892, 76, 64, C2)+stitch('M487 908 L506 908 L501 938', PAPER)
    idol = collar()+pair(path('M500 792 L435 763 L438 828 Z', C2))+oval(500, 794, 17, 18, C2)+star(588, 904, 26, C2)
    idol += path('M351 1008 Q382 1039 413 1008 Q446 1041 478 1008 Q511 1039 544 1008 Q577 1041 610 1008 L649 1012', ink=C2)
    anchor = collar()+tie+pair(path('M423 719 L404 747 L461 856 L483 831 Z', CD))+pocket(571, 842, C)
    doctor = collar(C2)+stitch('M434 769 C401 894 442 938 478 908 C500 886 483 852 468 885 M568 767 L566 867')+oval(565, 884, 17, 20, C2)+pocket(580, 903, CD)
    chef = path('M435 716 Q500 763 564 716 L553 754 L500 781 L443 752 Z', C2)+stitch('M501 786 L504 1031')
    chef += ''.join(oval(x, y, 6, 6, C2, w=7) for x in (454, 552) for y in (823, 889, 955))
    fire = box(347, 874, 307, 30, C2, 1)+box(345, 981, 311, 30, C2, 1)+stitch('M500 740 L500 1029')+pair(path('M397 745 L416 847', ink=PAPER, w=10))+pocket(565, 791, CD)
    space = path('M422 713 Q500 776 579 714', ink=C2, w=10)+box(422, 824, 156, 122, CD)
    space += box(439, 843, 120, 46, C2)+''.join(oval(x, 918, 8, 8, PAPER) for x in (449, 500, 550))+star(606, 783, 20, C2)
    magic = path('M413 718 L499 1034 L584 719 L550 740 L500 922 L450 740 Z', CD)+star(575, 862, 29, C2)+star(420, 960, 18, C2)
    knight = path('M410 746 Q500 719 591 749 L584 942 Q500 987 416 942 Z', CD)+stitch('M501 751 L501 964')+path('M500 818 L546 838 L535 893 L500 917 L465 890 L456 837 Z', C2)+star(500, 865, 19, PAPER)
    animal = oval(500, 902, 96, 111, C2)+path('M446 879 Q500 928 556 877', ink=CD)+heart(501, 845, 21, C)
    festival = box(442, 708, 116, 36, C2, 8)+stitch('M501 747 L499 1032', C2)
    festival += ''.join(path(f'M468 {y} Q485 {y-13} 500 {y} Q517 {y-14} 534 {y}', ink=C2) for y in (789, 852, 915, 979))
    details = [school, sport, idol, anchor, doctor, chef, fire, space, magic, knight, animal, festival]
    names = ['學院針織衫', '操場運動衫', '星光舞台服', '小主播西裝', '實習醫師服', '小廚師雙排扣',
             '消防勤務衣', '探索太空服', '口袋魔法師', '童話騎士甲', '暖暖動物裝', '新年盤扣衫']
    return [garment(f't{i}', n, d, sleeve='short' if i in (2, 3) else 'long')
            for i, (n, d) in enumerate(zip(names, details), 1)]


def coats():
    panel = path('M428 716 L382 717 Q335 727 331 782 L342 1040 L457 1044 L462 863 Z', CO)
    panel += wash(353, 816, 24, 124)
    base = pair(panel)
    variants = [
        ('散步開襟外套', base+pair(stitch('M435 739 L449 1020', COD))+pair(pocket(363, 926, COD))),
        ('學院翻領外套', base+pair(path('M425 718 L405 747 L465 870 L473 837 Z', COD))+pair(oval(449, 943, 6, 7, C2))),
        ('運動拉鍊外套', base+pair(path('M356 771 L366 1009', ink=C2, w=10))+pair(stitch('M453 810 L453 1020', COD))),
        ('魔法旅行斗篷', pair(path('M424 716 L375 730 Q309 828 294 1106 L411 1120 L464 835 Z', CO))
         +pair(wash(329, 865, 28, 145))+path('M417 715 Q500 796 584 716 L562 755 Q500 815 438 755 Z', COD)+star(453, 787, 16, C2))]
    return [{'id': f'o{i}', 'name': n, 'svg': s, 'sleeve': {'type': 'none' if i == 4 else 'long', 'fill': CO}}
            for i, (n, s) in enumerate(variants, 1)]


def bottoms():
    long = 'M346 997 L654 997 L650 1091 L605 1335 L519 1336 L502 1114 L482 1335 L394 1335 L348 1092 Z'
    short = 'M346 995 L651 995 L661 1155 L518 1157 L501 1102 L483 1157 L337 1154 Z'
    wide = 'M347 995 L654 995 L681 1319 L521 1321 L501 1110 L480 1320 L319 1318 Z'
    skirt = 'M346 996 L652 996 Q680 1093 709 1196 Q500 1224 292 1195 Z'
    names = ['鉛筆直筒褲', '操場短褲', '寬鬆旅行褲', '書頁百褶裙', '口袋工作褲', '節慶燈籠褲']
    shapes = [long, short, wide, skirt, long,
              'M346 995 L654 995 Q710 1111 650 1203 L521 1204 L501 1114 L483 1204 L350 1203 Q290 1110 346 995 Z']
    out = []
    for i, (n, d) in enumerate(zip(names, shapes), 1):
        s = path(d, PA)+wash(371, 1055, 29, 73)+stitch('M356 1021 Q500 1032 644 1022', PAD)
        if i in (1, 3, 5):
            s += pair(stitch('M416 1109 L429 1299', PAD))
        if i == 2:
            s += pair(stitch('M350 1132 L476 1134', PAD))
        if i == 4:
            s += ''.join(stitch(f'M{x} 1043 L{x+(x-500)*.25} 1197', PAD) for x in (378, 437, 500, 561, 620))
        if i == 5:
            s += pair(pocket(359, 1138, PAD))
        if i == 6:
            s += pair(box(351, 1180, 131, 30, PAD, 6))
        out.append({'id': f'p{i}', 'name': n, 'svg': s})
    return out


def shoes():
    out = []
    for i, name in enumerate(['散步帆布鞋', '學院皮鞋', '冒險短靴', '兔兔室內鞋'], 1):
        top = 1239 if i == 3 else 1324
        s = path(f'M404 {top} L477 {top} L480 1346 Q493 1363 489 1390 L384 1390'
                 f' Q380 1362 402 1345 Z', '{shoe}')
        s += path('M386 1378 L486 1379 L487 1391 L384 1391 Z', PAPER)
        s += wash(414, top+13, 24, 19)
        if i == 1:
            s += stitch('M423 1343 L461 1348 M421 1359 L460 1362', PAPER)
        elif i == 2:
            s += stitch('M407 1366 Q441 1353 477 1366')
        elif i == 3:
            s += box(400, 1244, 80, 25, '{shoe}', 5)+box(453, 1290, 20, 26, C2, 3)
        else:
            s += oval(420, 1320, 12, 30, '{shoe}')+oval(455, 1320, 12, 30, '{shoe}')
            s += oval(423, 1358, 4, 5, INK)+oval(455, 1358, 4, 5, INK)+oval(439, 1370, 5, 4, '#de897f')
        out.append({'id': f'z{i}', 'name': name, 'svg': pair(s)})
    return out


def hands():
    microphone = box(-14, -109, 30, 156, C2, 10)+oval(1, -147, 35, 43, '{acc}')
    microphone += stitch('M-24 -159 L25 -160 M-25 -139 L26 -140 M-10 -181 L-9 -116 M10 -182 L12 -116')+wash(-19, -173, 16, 23)
    wand = path('M0 37 L13 -157', ink=INK, w=20)+path('M0 37 L13 -157', ink=C2, w=10)+star(14, -184, 43, '{hat}')+wash(-4, -202, 20, 21)
    book = box(-145, -139, 165, 179, C2, 8)+path('M-127 -127 L-121 20 L15 17 L15 35 L-142 39 L-145 -134 Z', PAPER)
    book += stitch('M-111 -115 L-104 -8')+star(-53, -71, 28, C)+wash(-86, -119, 57, 13)
    balloon = path('M0 0 Q64 -85 120 -151 Q177 -204 166 -284', ink=INK, w=7)+oval(167, -361, 66, 83, C2)
    balloon += path('M162 -278 L180 -265 L150 -264 Z', C2)+wash(127, -404, 23, 42)
    brush = path('M-10 48 L17 -139 L34 -137 L8 49 Z', '{hat}')+box(16, -163, 26, 31, '{acc}', 3)
    brush += path('M17 -164 Q8 -192 35 -218 Q55 -180 41 -163 Z', C2)+wash(26, -197, 8, 19)
    flower = path('M0 31 Q3 -67 0 -143', ink=INK, w=16)+path('M0 31 Q3 -67 0 -143', ink='{back}', w=7)
    flower += path('M0 -42 Q-60 -94 -52 -112 Q0 -104 0 -42 Z', '{back}')
    for a in range(6):
        flower += oval(math.cos(a*math.tau/6)*29, -165+math.sin(a*math.tau/6)*29, 24, 25, C2)
    flower += oval(0, -165, 22, 22, '{hat}')+wash(-15, -177, 19, 15)
    return simple('k', [(n, group(s, f'translate({HOLD[0]} {HOLD[1]})')) for n, s in zip(
        ['採訪麥克風', '紙星魔法棒', '口袋故事書', '一顆小氣球', '蠟筆畫筆', '花園小花'],
        [microphone, wand, book, balloon, brush, flower])])


def backs():
    bag = box(289, 742, 422, 377, '{back}', 53)+pair(box(275, 842, 61, 176, '{backd}', 15))+wash(305, 792, 39, 113)
    strap = pair(path('M386 745 Q359 830 385 1002 L411 1000 Q389 828 411 747 Z', '{backd}'))
    wings = pair(path('M351 824 C259 624 92 669 147 838 Q113 952 311 1017 L372 991 Z', '{back}'))
    wings += pair(path('M319 871 Q251 761 185 738 M317 929 Q239 836 170 838', ink='{backd}'))+pair(wash(177, 760, 44, 58))
    cape = path('M395 721 Q500 683 608 723 Q701 883 752 1256 L627 1279 L500 1259 L376 1281 L247 1257 Q302 893 395 721 Z', '{back}')
    cape += pair(path('M389 811 Q353 1008 322 1211', ink='{backd}'))+wash(288, 1110, 36, 80)
    return [{'id': 'q1', 'name': '遠足小背包', 'svg': bag, 'front': strap},
            {'id': 'q2', 'name': '紙羽精靈翅膀', 'svg': wings},
            {'id': 'q3', 'name': '故事旅行披風', 'svg': cape}]


def pets():
    out = []
    for i, n in enumerate(['花園小貓', '長耳小兔', '發條小機器人'], 1):
        if i < 3:
            s = oval(0, -64, 68, 62, '{pet}')
            s += oval(-33, -10, 27, 8, '{pet}')+oval(32, -10, 27, 8, '{pet}')
            if i == 1:
                s += path('M-57 -137 L-60 -208 L-16 -173 L21 -174 L58 -207 L58 -134 Z', '{pet}')
                s += path('M-73 -53 Q-118 -91 -93 -125 Q-72 -144 -67 -114', ink=INK, w=20)
                s += path('M-73 -53 Q-118 -91 -93 -125 Q-72 -144 -67 -114', ink='{pet}', w=10)
            else:
                s += oval(-28, -197, 19, 61, '{pet}')+oval(26, -198, 19, 61, '{pet}')
                s += oval(-28, -201, 7, 36, '{petd}', 'none', 0)+oval(26, -201, 7, 36, '{petd}', 'none', 0)
            s += oval(0, -141, 65, 53, '{pet}')+oval(0, -61, 33, 38, PAPER, 'none', 0, .4)
            s += oval(-23, -147, 5, 8, INK)+oval(22, -147, 5, 8, INK)+path('M-6 -132 L6 -132 L0 -126 Z', '{petd}')
            s += stitch('M0 -125 Q-9 -114 -17 -123 M0 -125 Q8 -115 16 -122')
            s += wash(-39, -164, 18, 10)
        else:
            s = box(-59, -111, 119, 91, '{pet}', 13)+box(-71, -208, 143, 97, '{pet}', 17)
            s += pair_local_robot_ears()
            s += stitch('M1 -209 L4 -238')+oval(4, -247, 10, 10, '{petd}')
            s += oval(-29, -165, 13, 16, PAPER)+oval(30, -165, 13, 16, PAPER)
            s += oval(-29, -164, 5, 8, INK)+oval(30, -164, 5, 8, INK)+stitch('M-18 -137 L22 -138')
            s += box(-41, -22, 29, 17, '{petd}', 3)+box(13, -22, 29, 17, '{petd}', 3)+heart(0, -66, 18, '{petd}')+wash(-54, -194, 28, 15)
        out.append({'id': f'x{i}', 'name': n, 'svg': group(s, 'translate(830 1396)'),
                    'half': group(s, 'translate(160 1000) scale(0.82)')})
    return out


def pair_local_robot_ears():
    return box(-85, -182, 15, 44, '{petd}', 4)+box(72, -181, 15, 44, '{petd}', 4)


def simple(prefix, shapes):
    return [{'id': f'{prefix}{i}', 'name': n, 'svg': s} for i, (n, s) in enumerate(shapes, 1)]


def expressions(mouth):
    bl = blink()
    def es(s):
        return {'open': s, 'blink': bl}
    def ms(i):
        return {k: mouth[i][k] for k in ('closed', 'open')}
    e = {'normal': {'name': '一般'},
         'happy': {'name': '開心', 'eyes': es(eye_pair(4)), 'mouth': ms(1)},
         'surprised': {'name': '驚訝', 'eyes': es(eye_pair(5)),
                       'mouth': {'closed': oval(500, 534, 13, 18, '#71444b'), 'open': oval(500, 538, 22, 32, '#71444b')},
                       'brow': pair(stitch('M382 337 Q408 318 435 333', H2))},
         'angry': {'name': '生氣', 'brow': pair(stitch('M378 342 L437 362', H2)), 'mouth': ms(3),
                   'over': stitch('M660 302 L676 302 L679 284 M686 306 L704 305 L706 289', '#b76f68')},
         'cry': {'name': '哭哭', 'eyes': es(eye_pair(4)), 'mouth': ms(3),
                 'over': pair(path('M391 425 Q367 465 390 478 Q415 471 391 425 Z', '#91bfc6'))},
         'shy': {'name': '害羞', 'mouth': ms(0), 'over': pair(oval(350, 478, 39, 27, '#de897f', 'none', 0, .22)
                    +stitch('M330 477 L339 489 M348 473 L358 487', '#c9867b'))},
         'love': {'name': '喜歡', 'eyes': es(heart(410, 400, 18, C2)+heart(590, 400, 18, C2)), 'mouth': ms(1),
                  'over': heart(750, 300, 22, C2)},
         'sleepy': {'name': '想睡', 'eyes': es(pair(stitch('M389 404 L431 405'))), 'mouth': ms(2),
                    'over': stitch('M690 263 L717 263 L692 289 L720 289 M730 218 L766 218 L733 250 L770 250', '#839099')},
         'wink': {'name': '眨眼', 'eyes': es(oval(410, 400, 13, 19, '{eye}')+stitch('M569 389 L592 401 L569 415')),
                  'mouth': ms(4), 'over': star(742, 321, 21, C2)}}
    return e


def build():
    RNG.seed(271828)  # build() is reproducible even when called twice in one process.
    neck = path('M457 604 L543 603 L544 719 Q502 752 456 718 Z', SK2)+wash(468, 658, 21, 42)
    ears = pair(oval(284, 449, 31, 38, SK2)+stitch('M277 438 Q299 430 294 461', SK))
    legs = pair(path('M404 989 L480 987 L477 1367 Q439 1380 403 1365 Z', SK)+wash(416, 1211, 20, 88))
    arm = arms()
    face, hair, brow, mouth = faces(), hairs(), brows(), mouths()
    eyes = [{'id': f'e{i+1}', 'name': n, 'open': eye_pair(i), 'blink': blink()}
            for i, n in enumerate(['小墨點眼', '圓豆豆眼', '細長眼', '溫柔上眼線', '彎彎笑眼', '好奇白眼', '小睫毛眼', '慵懶眼'])]
    nose = simple('n', [('小圓鼻', path('M491 440 Q477 479 505 485 Q531 481 520 466', SK2)),
                        ('鉛筆三角鼻', path('M499 439 L482 479 L517 481', SK2)),
                        ('彎彎鼻樑', path('M500 437 Q505 460 494 473 Q481 489 516 486', SK2))])
    deco = simple('d', [('小雀斑', pair(''.join(oval(x, y, 3, 3, '#aa7568', 'none', 0) for x, y in [(327, 471), (345, 462), (365, 475), (347, 485)]))),
                        ('蠟筆腮紅', blush()),
                        ('星星貼紙', star(347, 484, 22, C2)+wash(337, 472, 12, 10)),
                        ('花瓣臉彩', pair(path('M324 479 L370 486 M328 494 L368 501', ink=C2, w=9)))])
    glasses = []
    for i, name in enumerate(['圓圓鉛筆框', '方方讀書框', '彩色太陽鏡'], 1):
        lens = oval(410, 401, 47, 45, 'none', '{acc}') if i == 1 else box(357, 363, 106, 78, '{acc}' if i == 3 else 'none', 14, '{acc}')
        if i == 1:
            # Transparent lenses preserve small eyes; only the rim is opaque.
            lens += path('M383 375 L396 371', ink=PAPER, w=7)
        s = pair(lens)+path('M458 398 Q500 383 541 398 M360 391 L305 379 M643 392 L695 378', ink='{acc}')
        if i == 3:
            s += pair(wash(374, 376, 38, 15, PAPER, .45))
        glasses.append({'id': f'g{i}', 'name': name, 'svg': s})
    headset = []
    for i, n in enumerate(['繪本主播耳麥', '音樂大耳機'], 1):
        s = path('M265 422 Q242 161 490 150 Q748 143 738 426', ink=INK, w=20)
        s += path('M265 422 Q242 161 490 150 Q748 143 738 426', ink='{acc}', w=10)
        s += pair(box(239, 397, 56, 115, '{acc}', 19)+wash(251, 413, 17, 53))
        if i == 1:
            s += path('M267 510 Q280 579 400 577', ink='{acc}', w=9)+oval(412, 576, 19, 13, '{acc}')
        headset.append({'id': f's{i}', 'name': n, 'svg': s})
    top, coat, bottom, shoe = tops(), coats(), bottoms(), shoes()
    hand, back, pet = hands(), backs(), pets()
    cats = {}
    data = [('face', '臉型', face), ('hair', '髮型', hair), ('brow', '眉毛', brow), ('eyes', '眼睛', eyes),
            ('mouth', '嘴巴', mouth), ('nose', '鼻子', nose), ('deco', '臉部裝飾', deco), ('glasses', '眼鏡', glasses),
            ('hat', '帽子頭飾', hats()), ('headset', '耳機麥克風', headset), ('top', '上衣', top), ('coat', '外套', coat),
            ('bottom', '下身', bottom), ('shoes', '鞋子', shoe), ('hand', '手持物', hand), ('back', '背後', back), ('pet', '夥伴', pet)]
    defaults = {k: '' for k, _, _ in data}
    defaults.update(face='f1', hair='h1', brow='b1', eyes='e1', mouth='m1', nose='n1', top='t1', bottom='p1', shoes='z1')
    for k, n, opts in data:
        cats[k] = {'name': n, 'none': k not in ('face', 'eyes', 'mouth', 'top', 'bottom'), 'opts': opts}
    return {'format': 2, 'id': 'sketch', 'name': '手繪線條風', 'author': 'Codex', 'version': '1.0',
            'date': '2026-11-15', 'base': {'neck': neck, 'ears': ears, 'legs': legs, 'arms': arm},
            'poses': POSES, 'expr': expressions(mouth), 'defaults': defaults,
            'view': {'face': '200 150 600 600', 'hair': '100 40 800 800', 'brow': '270 220 460 460',
                     'eyes': '290 270 420 420', 'mouth': '330 400 340 340', 'nose': '340 330 320 320',
                     'deco': '240 260 520 520', 'glasses': '240 200 520 520', 'hat': '100 20 800 800',
                     'headset': '180 120 640 640', 'top': '220 640 560 560', 'coat': '200 620 600 600',
                     'bottom': '250 950 500 500', 'shoes': '300 1150 400 400', 'hand': '300 440 640 640',
                     'back': '60 560 880 880', 'pet': '700 1110 260 300'}, 'cats': cats}


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    out = Path(sys.argv[1] if len(sys.argv) > 1 else 'packs/sketch/pack.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    pack = build()
    out.write_text(json.dumps(pack, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'已產生 {out}：' + '、'.join(f'{c["name"]} {len(c["opts"])}' for c in pack['cats'].values()))
