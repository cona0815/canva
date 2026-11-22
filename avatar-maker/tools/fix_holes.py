#!/usr/bin/env python3
"""補衣服圖層的破洞 v1.0 2026-11-22
11-22 老師：「先檢查所有物件因為帽子或上衣而導致破圖的，做修正」。
白色衣服（醫師袍、廚師服、西裝背心的白襯衫袖…）和人台的白 T 顏色太像，拆圖層時被當成「人台本來就有」挖掉，
圖層中間變成破洞；平常有白 T 墊著看不出來，留長髮時頭髮會從洞裡透出來（看起來像衣服破了一塊）。
做法：衣服輪廓（閉運算後填滿）裡面、圖層透明、原圖不是綠幕、人台那裡不是皮膚的像素，
用 Codex 原圖（同樣對位）的顏色補回去，補的地方不透明。
第二種：頭髮圖層沿著臉、身體邊緣黏到一圈人台的白 T／皮膚（拆圖沒切乾淨），頭髮疊在衣服上時肩膀會多一塊淺色斑。
  頭髮圖層裡「很淺、不飽和、底下人台不透明」的像素去掉（人台本來就有一樣的顏色，沒穿衣服時看起來不變）。
用法：python tools/fix_holes.py <AVA-03 案件資料夾> [畫風 ...] [--dry]
"""
import json, os, sys
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from raster_parts import load, chroma, warp_rgba
import make_raster_pack as MRP

CATS = ('top', 'bottom', 'shoes', 'hat')
CLOSE = {'top': 25, 'bottom': 25, 'shoes': 11, 'hat': 11}   # 閉運算直徑：把衣服輪廓的小缺口接起來，才填得到「從縫隙連到外面」的洞


def raw_path(case, st, pid):
    """和 make_raster_pack 一樣的輪次順序：後面的輪次蓋前面的"""
    hit = None
    for r in os.environ.get('ROUNDS', 'R2,R3,R3b,R4,R5,R6,R7,R8,R9,R11,R12').split(','):
        f = os.path.join(case, 'art', r, st, pid + '.png')
        if os.path.exists(f) and not pid.startswith(MRP.DROP) and not pid.startswith(MRP.SKIP.get((st, r), ())):
            hit = f
    return hit


def full(path, o, W, H):
    im = np.zeros((H, W, 4), np.float32)
    p = np.array(Image.open(path).convert('RGBA'), np.float32)
    im[o['y']:o['y'] + p.shape[0], o['x']:o['x'] + p.shape[1]] = p
    return im


def is_skin(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (r > 150) & (r - b > 35) & (r >= g) & (g >= b - 5)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry' in sys.argv
    case, styles = args[0], args[1:] or ['kawaii', 'anime', 'sticker']
    report = {}
    for st in styles:
        pj = os.path.join(ROOT, 'packs', st, 'parts.json')
        P = json.load(open(pj, encoding='utf-8'))
        W, H = P['canvas']
        base = full(os.path.join(ROOT, 'packs', st, 'base.webp'), P['base'], W, H)
        bskin = is_skin(base[..., :3]) & (base[..., 3] > 128)
        changed = 0
        for c in CATS:
            if c not in P['cats']:
                continue
            for o in P['cats'][c]['opts']:
                src = raw_path(case, st, o['id'])
                if not src:   # 例如從手遊風搬過來的 top_gNN：沒有原圖
                    continue
                lay = full(os.path.join(ROOT, 'packs', st, o['id'] + '.webp'), o, W, H)
                M = np.array(o.get('warp', [1, 0, 0, 0, 1, 0]), np.float32).reshape(2, 3)
                raw = warp_rgba(chroma(load(src)), M, (H, W))
                a = lay[..., 3]
                solid = a > 200
                k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (CLOSE[c], CLOSE[c]))
                G = ndimage.binary_fill_holes(cv2.morphologyEx(solid.astype(np.uint8), cv2.MORPH_CLOSE, k) > 0)
                hole = G & (a < 200) & (raw[..., 3] > 200) & ~bskin
                lab, n = ndimage.label(hole)
                if n:
                    sz = np.bincount(lab.ravel()); keep = np.zeros(n + 1, bool); keep[1:] = sz[1:] >= 40   # 邊緣抗鋸齒的零星像素不算洞
                    hole = keep[lab]
                npx = int(hole.sum())
                if npx < 200:
                    continue
                report.setdefault(st, []).append((o['name'], npx))
                if dry:
                    continue
                # 補：洞裡直接用原圖顏色、不透明；洞邊 1px 和原本的圖層混一下，免得接縫
                out = lay.copy()
                out[hole, :3] = raw[hole, :3]; out[hole, 3] = 255
                ys, xs = np.where(out[..., 3] > 3)
                x0, y0, x1, y1 = max(0, xs.min() - 4), max(0, ys.min() - 4), min(W, xs.max() + 5), min(H, ys.max() + 5)
                Image.fromarray(np.clip(out[y0:y1, x0:x1], 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'packs', st, o['id'] + '.webp'), 'WEBP', quality=90, method=6)
                o.update({'x': int(x0), 'y': int(y0), 'w': int(x1 - x0), 'h': int(y1 - y0)})
                changed += 1
        # 頭髮圖層：去掉黏到的人台淺色邊
        for o in P['cats'].get('hair', {}).get('opts', []):
            lay = full(os.path.join(ROOT, 'packs', st, o['id'] + '.webp'), o, W, H)
            mn, mx = lay[..., :3].min(-1), lay[..., :3].max(-1)
            res = (lay[..., 3] > 8) & (base[..., 3] > 128) & (mn > 150) & ((mx - mn) < .35 * mx)
            npx = int(res.sum())
            if npx < 50:
                continue
            report.setdefault(st + ' 頭髮淺邊', []).append((o['name'], npx))
            if dry:
                continue
            lay[res, 3] = 0
            ys, xs = np.where(lay[..., 3] > 3)
            x0, y0, x1, y1 = max(0, xs.min() - 4), max(0, ys.min() - 4), min(W, xs.max() + 5), min(H, ys.max() + 5)
            Image.fromarray(np.clip(lay[y0:y1, x0:x1], 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'packs', st, o['id'] + '.webp'), 'WEBP', quality=90, method=6)
            o.update({'x': int(x0), 'y': int(y0), 'w': int(x1 - x0), 'h': int(y1 - y0)})
            changed += 1
        if changed and not dry:
            json.dump(P, open(pj, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    for st, r in report.items():
        r.sort(key=lambda x: -x[1])
        print(st, len(r), '件有破洞：', '、'.join(f'{n}({p})' for n, p in r))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
