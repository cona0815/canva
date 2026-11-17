#!/usr/bin/env python3
"""把手遊冒險風（game）的造型服搬到日式漫畫（anime）v1.0 2026-11-17
11-17 老師：「把手遊這幾件衣服移到日式漫畫裡，並先把手遊隱藏起來」。
兩個人台頭身比不同（game 細長 6 頭身、anime 大頭短身），所以用身體對位點做薄板樣條變形（TPS），
把 packs/game 的上衣圖層和擦除圖層變形到 anime 人台上，存成 packs/anime/top_gNN，排在上衣最前面。
make_raster_pack.py 做 anime 時會自動呼叫；也可以單獨跑：python tools/port_tops.py [--debug 輸出資料夾]
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy.interpolate import RBFInterpolator
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, DST = 'game', 'anime'
W, H = 1024, 1536
STAR = '✦'   # 名稱前面加星號，和日式漫畫原本的同名款分開

# 對位點：(game 座標) → (anime 座標)，左右各一（x 以人台中線 512 左右對稱量）
PAIRS = [
    ((512, 305), (512, 385)),   # 下巴
    ((512, 330), (512, 410)),   # 領口中間
    ((455, 335), (450, 413)), ((570, 335), (575, 413)),   # 領口兩側
    ((400, 355), (398, 432)), ((625, 355), (628, 432)),   # 肩膀
    ((338, 490), (332, 548)), ((688, 492), (692, 548)),   # 袖口外角
    ((425, 515), (408, 578)), ((600, 515), (616, 578)),   # 腋下
    ((324, 645), (311, 690)), ((370, 645), (376, 690)),   # 左手肘外、內
    ((653, 645), (645, 690)), ((698, 645), (710, 690)),   # 右手肘內、外
    ((390, 705), (382, 770)), ((634, 705), (640, 770)),   # 上衣下襬兩側
    ((512, 712), (512, 785)),   # 下襬中間
    ((382, 875), (367, 925)), ((642, 875), (655, 925)),   # 短褲下緣兩側
    ((422, 960), (408, 1000)), ((502, 960), (499, 1000)), ((521, 960), (523, 1000)), ((600, 960), (614, 1000)),   # 大腿
    ((423, 1080), (405, 1100)), ((498, 1080), (495, 1100)), ((525, 1080), (527, 1100)), ((599, 1080), (617, 1100)),   # 膝蓋
    ((0, 0), (0, 0)), ((W - 1, 0), (W - 1, 0)), ((0, H - 1), (0, H - 1)), ((W - 1, H - 1), (W - 1, H - 1)),
]


def arm_pairs():
    """上臂、手腕：兩個人台各量同一段手臂的左右邊緣（自動量，比目測準）"""
    out = []
    rows = [(560, 620), (760, 780)]   # (game 列, anime 列)：上臂中段、手腕
    bases = {}
    for st in (SRC, DST):
        a = np.array(Image.open(os.path.join(ROOT, 'packs', st, 'base.webp')).convert('RGBA'))
        bases[st] = a[..., 3] > 128
    for gy, ay in rows:
        runs = {}
        for st, y in ((SRC, gy), (DST, ay)):
            pk = json.load(open(os.path.join(ROOT, 'packs', st, 'parts.json'), encoding='utf-8'))['base']
            r = np.zeros(W, bool)
            yy = y - pk['y']
            r[pk['x']:pk['x'] + pk['w']] = bases[st][yy]
            d = np.diff(np.r_[0, r.astype(int), 0]); s = np.where(d == 1)[0]; e = np.where(d == -1)[0] - 1
            runs[st] = [(a, b) for a, b in zip(s, e) if b - a > 5]
        g, a = runs[SRC], runs[DST]
        for i in (0, -1):   # 最左、最右那段＝左右手臂
            out += [((g[i][0], gy), (a[i][0], ay)), ((g[i][1], gy), (a[i][1], ay))]
    return out


def mapping():
    P = PAIRS + arm_pairs()
    g = np.array([p[0] for p in P], float); a = np.array([p[1] for p in P], float)
    f = RBFInterpolator(a, g, kernel='thin_plate_spline', smoothing=2.0)   # anime 座標 → 要去 game 哪裡取色
    step = 8
    gy, gx = np.mgrid[0:H + step:step, 0:W + step:step]
    src = f(np.c_[gx.ravel(), gy.ravel()]).reshape(gy.shape + (2,)).astype(np.float32)
    mx = cv2.resize(src[..., 0], (W, H), interpolation=cv2.INTER_LINEAR)
    my = cv2.resize(src[..., 1], (W, H), interpolation=cv2.INTER_LINEAR)
    # resize 會把格點放到像素格線上，誤差不到 1/8 格，衣服用不到這麼準
    return mx, my


def tee_mask(bp):
    """anime 人台的白 T 範圍（領口到下襬、不是皮膚的淺色像素，往外擴幾格把外框線也包進來）"""
    im = full(os.path.join(ROOT, 'packs', DST, 'base.webp'), bp['x'], bp['y']).astype(int)
    r, g, b, a = im[..., 0], im[..., 1], im[..., 2], im[..., 3]
    mx_, mn_ = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    light = (a > 128) & (mx_ > 150) & ((mx_ - mn_) < 0.22 * mx_)   # 白、淡紫灰陰影
    yy = np.arange(H)[:, None]
    light &= (yy > 395) & (yy < 720)   # 只擦到腰：再下面是白 T 下襬蓋著短褲腰頭，擦了會露出底色
    m = cv2.dilate(light.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    skin = (a > 128) & (r - b > 40) & (r > 170)
    return m & ~skin & (a > 20)


def full(path, x, y):
    im = np.zeros((H, W, 4), np.uint8)
    p = np.array(Image.open(path).convert('RGBA'))
    im[y:y + p.shape[0], x:x + p.shape[1]] = p
    return im


def warp(im, mx, my):
    # 預乘 alpha 再取樣，邊緣才不會出現黑邊
    f = im.astype(np.float32); f[..., :3] *= f[..., 3:4] / 255
    w = cv2.remap(f, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    a = w[..., 3:4]; w[..., :3] = np.where(a > 0, w[..., :3] * 255 / np.maximum(a, 1e-3), 0)
    return np.clip(w, 0, 255)


def save(rgba, path, pad=4):
    a = rgba[..., 3]; ys, xs = np.where(a > 3)
    x0, y0 = max(0, xs.min() - pad), max(0, ys.min() - pad)
    x1, y1 = min(W, xs.max() + pad + 1), min(H, ys.max() + pad + 1)
    Image.fromarray(rgba[y0:y1, x0:x1].astype(np.uint8), 'RGBA').save(path, 'WEBP', quality=90, method=6)
    return {'x': int(x0), 'y': int(y0), 'w': int(x1 - x0), 'h': int(y1 - y0)}


def main():
    dbg = sys.argv[sys.argv.index('--debug') + 1] if '--debug' in sys.argv else None
    gp = json.load(open(os.path.join(ROOT, 'packs', SRC, 'parts.json'), encoding='utf-8'))
    ap_path = os.path.join(ROOT, 'packs', DST, 'parts.json')
    ap = json.load(open(ap_path, encoding='utf-8'))
    mx, my = mapping()
    tee = tee_mask(ap['base'])
    new = []
    for o in gp['cats']['top']['opts']:
        nid = o['id'].replace('top_', 'top_g')
        lay = warp(full(os.path.join(ROOT, 'packs', SRC, o['id'] + '.webp'), o['x'], o['y']), mx, my)
        opt = {'id': nid, 'name': STAR + o['name']}
        opt.update(save(lay, os.path.join(ROOT, 'packs', DST, nid + '.webp')))
        opt['warp'] = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        er = np.zeros((H, W, 4), np.float32)
        if o.get('erase'):
            e = o['erase']
            er = warp(full(os.path.join(ROOT, 'packs', SRC, o['id'] + '_erase.webp'), e['x'], e['y']), mx, my)
        # anime 的白 T 比 game 寬：沒被造型服蓋住的白 T（含外框線）也要擦掉，不然腋下、袖子旁會露白
        keep = er[..., 3] > 100
        keep |= tee & (lay[..., 3] < 200)
        er[..., 3] = np.where(keep, 255, 0); er[..., :3] = 255
        if keep.any():
            opt['erase'] = save(er, os.path.join(ROOT, 'packs', DST, nid + '_erase.webp'))
        new.append(opt)
        if dbg:
            os.makedirs(dbg, exist_ok=True)
            Image.fromarray(lay.astype(np.uint8), 'RGBA').save(os.path.join(dbg, nid + '.png'))
    top = ap['cats']['top']
    top['opts'] = new + [o for o in top['opts'] if not o['id'].startswith('top_g')]
    json.dump(ap, open(ap_path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('anime 上衣加入', [o['name'] for o in new], '共', len(top['opts']))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
