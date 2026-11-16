#!/usr/bin/env python3
"""點陣部件處理 v1.4 2026-11-16（頭髮補洞不補進臉；--fine-faces：手遊風表情的細閉眼線另外加回來；帽子也做擦除遮罩；鞋子門檻降到 12，白襪不會被當成淺膚色；對位會和「不移動」比較取好的；細線部件不被當雜點）：把 Codex 生的「人台＋某部件」圖，去背、對齊人台、減掉人台，拆出單一部件圖層。
用法：python tools/raster_parts.py <Codex 圖資料夾> <輸出資料夾> [--debug <除錯圖資料夾>]
輸入（1024×1536、純綠底）：base.png、hair_N.png、top_N.png、face_X_closed|open|blink.png；items.png（1024×1024 四格）
輸出：base.webp＋每個部件裁切後的 webp，以及 parts.json（每張的位置 x, y, w, h）
做法：
  1. 綠幕去背（綠色距離→透明度，邊緣去綠溢色）
  2. 用 OpenCV ECC 把每張圖對齊到人台（平移＋縮放，以人台不變的部分當基準）
  3. 和人台比顏色差，差很多或人台那裡本來是空的 → 算部件；只留部件該在的區域、去掉小雜點
"""
import sys, os, json, argparse
import numpy as np
import cv2
from PIL import Image

KEY = np.array([0, 255, 0], np.float32)


def load(p):
    return np.array(Image.open(p).convert('RGB'), np.float32)


def chroma(rgb):
    """回傳 rgba（0～255 float），綠幕去背"""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    green = g - np.maximum(r, b)                    # 越綠越大
    alpha = np.clip(1 - (green - 40) / (140 - 40), 0, 1)   # green<40 不透明，>140 全透明
    # 去綠溢色：邊緣半透明處把 G 壓到 R、B 的最大值
    spill = np.minimum(g, np.maximum(r, b) + 10)
    g2 = np.where(green > 10, spill, g)
    out = np.dstack([r, g2, b, alpha * 255])
    # 去掉孤立雜點
    m = (alpha > .5).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n > 1:
        big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
        keep = np.zeros(n, bool); keep[big] = True
        keep[1:] |= st[1:, cv2.CC_STAT_AREA] > 1500
        out[..., 3] *= keep[lab] | (alpha <= .5)
    return out


def align(img, base, mask_region):
    """ECC 對齊：回傳把 img 對到 base 的 2×3 矩陣（只用 mask_region 內、兩邊都不透明的像素）"""
    s = .25
    a = cv2.resize(cv2.cvtColor(base[..., :3].astype(np.uint8), cv2.COLOR_RGB2GRAY), None, fx=s, fy=s).astype(np.float32)
    b = cv2.resize(cv2.cvtColor(img[..., :3].astype(np.uint8), cv2.COLOR_RGB2GRAY), None, fx=s, fy=s).astype(np.float32)
    msk = cv2.resize(mask_region.astype(np.uint8) * (base[..., 3] > 128), None, fx=s, fy=s, interpolation=cv2.INTER_NEAREST)
    warp = np.eye(2, 3, dtype=np.float32)
    try:
        cv2.findTransformECC(a, b, warp, cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-5), msk, 5)
    except cv2.error:
        warp = np.eye(2, 3, dtype=np.float32)
    warp[:, 2] /= s
    return warp


def align_err(img, base, M, mask_region):
    """對位後，在不該變的區域裡兩張圖的平均差（越小越好）"""
    w = warp_rgba(img, M, base.shape)
    m = mask_region & (base[..., 3] > 128) & (w[..., 3] > 128)
    if m.sum() < 1000:
        return 1e9
    return float(np.abs(w[..., :3][m] - base[..., :3][m]).mean())


def best_align(img, base, mask_region):
    """ECC 有時會被大面積的新部件（例如長褲蓋住小腿）帶歪：和「不移動」比，取差比較小的"""
    M = align(img, base, mask_region)
    I = np.eye(2, 3, dtype=np.float32)
    return M if align_err(img, base, M, mask_region) < align_err(img, base, I, mask_region) else I


def warp_rgba(img, M, shape):
    return cv2.warpAffine(img, M, (shape[1], shape[0]), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))


def lab(rgb):
    return cv2.cvtColor((rgb / 255).astype(np.float32), cv2.COLOR_RGB2LAB)


def extract(img, base, region, thresh=22, min_area=600, grow=3, open_k=5, fill=True, same_hue=False, protect=None):
    """img、base 都已對齊的 rgba；region＝部件可能出現的範圍（bool）"""
    ia, ba = img[..., 3] / 255, base[..., 3] / 255
    d = np.linalg.norm(lab(img[..., :3]) - lab(base[..., :3]), axis=2)
    new = (ia > .5) & ((ba < .5) | (d > thresh))
    new &= region
    if same_hue:
        # 帽簷在額頭投的陰影：和人台同色相、只是變暗的皮膚，不算部件（否則配上頭髮會蓋住瀏海）
        hi = cv2.cvtColor(np.clip(img[..., :3], 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        hb = cv2.cvtColor(np.clip(base[..., :3], 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        dh = np.abs(hi[..., 0] - hb[..., 0]); dh = np.minimum(dh, 180 - dh)
        new &= ~((ba > .5) & (dh < 7) & (hi[..., 1] > 50) & (hb[..., 1] > 30))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_k, open_k))
    m = cv2.morphologyEx(new.astype(np.uint8), cv2.MORPH_OPEN, k)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    n, labl, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros(n, bool)
    keep[1:] = st[1:, cv2.CC_STAT_AREA] >= min_area
    m = keep[labl].astype(np.uint8)
    # 把洞補起來（部件內部和人台同色的地方，例如白襯衫）
    # 帽子、眼鏡不補洞：鏡片裡、帽簷下是人台的皮膚，補進來會蓋住表情和瀏海
    if fill:
        cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filled = np.zeros_like(m)
        cv2.drawContours(filled, cnts, -1, 1, -1)
        m = filled
        if protect is not None:   # 補洞不可以補進臉（捲髮把整張臉圍起來時，會把空白臉當成頭髮的一部分、蓋住表情）
            m = m & ~(protect & ~new).astype(np.uint8)
    m = m & (ia > .05)
    if grow:
        m = cv2.dilate(m.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (grow * 2 + 1,) * 2)) & (ia > .05)
    soft = cv2.GaussianBlur(m.astype(np.float32), (5, 5), 0)
    out = img.copy()
    out[..., 3] = img[..., 3] * np.clip(soft * 1.4, 0, 1)
    return out


def add_dark_lines(part, img, base, region, dl=12, min_area=30):
    """臉裡面比人台暗很多的細線（閉眼線、眉毛、小嘴）→ 併進部件；只看暗的，避免把皮膚明暗差異當成部件"""
    li, lb = lab(img[..., :3])[..., 0], lab(base[..., :3])[..., 0]
    m = ((img[..., 3] > 128) & (lb - li > dl) & region).astype(np.uint8)
    n, labl, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros(n, bool)
    keep[1:] = st[1:, cv2.CC_STAT_AREA] >= min_area
    m = cv2.dilate(keep[labl].astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    soft = np.clip(cv2.GaussianBlur(m.astype(np.float32), (5, 5), 0) * 1.4, 0, 1)
    out = part.copy()
    a = np.maximum(part[..., 3], img[..., 3] * soft)
    out[..., :3] = np.where((part[..., 3:4] < 1) & (a[..., None] > 0), img[..., :3], part[..., :3])
    out[..., 3] = a
    return out


def erase_mask(img, base, region, min_area=250):
    """人台有、新圖沒有的地方（例如外套比白 T 恤窄，露出來的 T 恤）→ 網頁畫這個部件前要先把人台這些地方擦掉"""
    e = (img[..., 3] < 90) & (base[..., 3] > 150) & region
    e = cv2.morphologyEx(e.astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    n, labl, st, _ = cv2.connectedComponentsWithStats(e, 8)
    keep = np.zeros(n, bool)
    keep[1:] = st[1:, cv2.CC_STAT_AREA] >= min_area
    e = keep[labl].astype(np.uint8)
    if not e.any():
        return None
    e = cv2.dilate(e, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    out = np.zeros(img.shape, np.float32)
    out[..., :3] = 255
    out[..., 3] = cv2.GaussianBlur(e.astype(np.float32), (3, 3), 0) * 255
    return out


def bbox_save(rgba, path, pad=4):
    a = rgba[..., 3]
    ys, xs = np.where(a > 3)
    if not len(xs):
        raise ValueError(f'{path} 是空的')
    x0, y0 = max(0, xs.min() - pad), max(0, ys.min() - pad)
    x1, y1 = min(a.shape[1], xs.max() + pad + 1), min(a.shape[0], ys.max() + pad + 1)
    crop = np.clip(rgba[y0:y1, x0:x1], 0, 255).astype(np.uint8)
    Image.fromarray(crop, 'RGBA').save(path, 'WEBP', quality=90, method=6)
    return {'x': int(x0), 'y': int(y0), 'w': int(x1 - x0), 'h': int(y1 - y0)}


def regions(base):
    """依人台輪廓估出頭、臉、身體的範圍"""
    m = base[..., 3] > 128
    ys, xs = np.where(m)
    top, bot = ys.min(), ys.max()
    Hh = bot - top
    rows = np.where(m.any(1))[0]
    widths = m.sum(1)
    # 頭：從頭頂往下，到寬度最窄的脖子為止
    search = range(top + int(Hh * .15), top + int(Hh * .45))
    neck = min(search, key=lambda y: widths[y] if widths[y] > 0 else 1e9)
    cx = int(np.median(xs))
    H, W = m.shape
    yy, xx = np.mgrid[0:H, 0:W]
    head_h = neck - top
    face_c = (cx, top + head_h * .58)
    face = ((xx - face_c[0]) / (head_h * .42)) ** 2 + ((yy - face_c[1]) / (head_h * .40)) ** 2 < 1
    return {'top': int(top), 'bot': int(bot), 'neck': int(neck), 'cx': cx,
            'hair': yy < neck + Hh * .30, 'face': face, 'body': (yy > neck - 10) & (yy < top + Hh * .80),
            'still': yy > top + Hh * .80}   # 腳和小腿：所有圖都不變，拿來對齊


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('--debug'); ap.add_argument('--fine-faces', action='store_true')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.debug:
        os.makedirs(a.debug, exist_ok=True)
    base = chroma(load(os.path.join(a.src, 'base.png')))
    R = regions(base)
    meta = {'canvas': [base.shape[1], base.shape[0]], 'neck': R['neck'], 'top': R['top'], 'bot': R['bot'], 'cx': R['cx'], 'parts': {}}
    meta['parts']['base'] = bbox_save(base, os.path.join(a.out, 'base.webp'))
    # 右手（畫面右邊）的位置：身體最下面 35% 裡、中線右邊 150px 外的人台像素中心
    Hh = R['bot'] - R['top']
    hm = base[..., 3] > 128
    hm[:int(R['top'] + Hh * .64)] = False; hm[int(R['top'] + Hh * .74):] = False; hm[:, :R['cx'] + 150] = False
    ys, xs = np.where(hm)
    meta['hand'] = {'x': int(xs.mean()), 'y': int(ys.mean()), 'size': int(Hh * .22)} if len(xs) else {'x': R['cx'] + 220, 'y': int(R['top'] + Hh * .65), 'size': int(Hh * .22)}
    head_still = ~R['hair']   # 換頭髮時：身體不變
    body_still = R['still'] | (np.mgrid[0:base.shape[0], 0:base.shape[1]][0] < R['neck'] - 20)   # 換衣服時：頭和腳不變
    yy, xx = np.mgrid[0:base.shape[0], 0:base.shape[1]]
    frac = lambda f: R['top'] + Hh * f
    legs = (yy > frac(.46))   # 從褲頭開始（v1.0 用 .55 會少掉腰頭、露出灰短褲）
    feet = (yy > frac(.86))
    headz = (yy < R['neck'] + 30)
    handz = (yy > frac(.28)) & (yy < frac(.92)) & (xx > R['cx'] + 60)   # 魔法棒、螢光棒比較長，往上放寬
    face_inner = cv2.erode(R['face'].astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 41))).astype(bool)   # 不碰臉的外輪廓和耳朵
    face_big = cv2.dilate(R['face'].astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (81, 81))).astype(bool)
    plan = []
    for f in sorted(os.listdir(a.src)):
        n = f[:-4]
        if n.startswith('hair_'):
            plan.append((f, n, head_still, R['hair'] | R['body'], 22))
        elif n.startswith('top_'):
            plan.append((f, n, body_still, R['body'], 14))
        elif n.startswith('face_'):
            plan.append((f, n, ~R['face'], R['face'], 18))
        elif n.startswith('bottom_'):
            plan.append((f, n, (yy < frac(.45)) | feet, legs & ~feet | (legs & (yy < frac(.90))), 22))
        elif n.startswith('shoes_'):
            plan.append((f, n, yy < frac(.70), yy > frac(.72), 12))   # 白襪和淺膚色差不到 22（kawaii 足球襪會不見）
        elif n.startswith('hat_'):
            plan.append((f, n, yy > R['neck'] + 40, headz, 22))
        elif n.startswith('glasses_'):
            plan.append((f, n, ~face_big, face_big & (yy < R['top'] + (R['neck'] - R['top']) * .80), 20))
        elif n.startswith('hand_'):
            plan.append((f, n, ~handz, handz, 22))
        elif n.startswith('pet_'):
            plan.append((f, n, yy < frac(.5), (yy > frac(.45)) & ((xx < R['cx'] - 200) | (xx > R['cx'] + 200)), 22))
    for f, n, still, region, th in plan:
        img = chroma(load(os.path.join(a.src, f)))
        M = best_align(img, base, still)
        al = warp_rgba(img, M, base.shape)
        thin = n.startswith(('glasses_', 'hat_'))   # 細鏡框、耳麥線：開運算用小核、小塊也留
        part = extract(al, base, region, th, min_area=300 if n.startswith('face_') else 150 if thin else 1500, open_k=3 if thin else 5, fill=not thin, same_hue=n.startswith('hat_'), protect=face_big if n.startswith('hair_') else None)
        if a.fine_faces and n.startswith('face_'):   # 手遊風閉眼線、眉毛很細：開運算會把它們當雜點去掉 → 另外把臉內「變深的細線」加回來
            part = add_dark_lines(part, al, base, face_inner)
        meta['parts'][n] = bbox_save(part, os.path.join(a.out, n + '.webp'))
        meta['parts'][n]['warp'] = [round(float(v), 4) for v in M.ravel()]
        er = None
        if n.startswith(('top_', 'bottom_', 'shoes_', 'hat_')):   # 帽子也要：魔術師高帽帽身比頭窄，帽身兩側要擦掉人台的光頭
            er = erase_mask(al, base, region)
            if er is not None:
                meta['parts'][n]['erase'] = bbox_save(er, os.path.join(a.out, n + '_erase.webp'))
        if a.debug:
            comp = base.copy()
            if er is not None:
                comp[..., 3] *= 1 - er[..., 3] / 255
            pa = part[..., 3:4] / 255
            comp[..., :3] = comp[..., :3] * (1 - pa) + part[..., :3] * pa
            comp[..., 3] = np.maximum(comp[..., 3], part[..., 3])
            side = np.concatenate([al, comp, part], 1)
            bg = np.full(side.shape[:2] + (3,), 235, np.float32)
            aa = side[..., 3:4] / 255
            Image.fromarray((bg * (1 - aa) + side[..., :3] * aa).astype(np.uint8)).resize((side.shape[1] // 3, side.shape[0] // 3)).save(os.path.join(a.debug, n + '.png'))
        print(n, meta['parts'][n]['w'], 'x', meta['parts'][n]['h'], '位移', [round(M[0, 2], 1), round(M[1, 2], 1)], '縮放', round(float(M[0, 0]), 3))
    # 手持物：四格各一個
    ip = os.path.join(a.src, 'items.png')
    if os.path.exists(ip):
        it = chroma(load(ip))
        h, w = it.shape[:2]
        k = 0
        for gy in range(2):
            for gx in range(2):
                cell = np.zeros_like(it)
                cell[gy * h // 2:(gy + 1) * h // 2, gx * w // 2:(gx + 1) * w // 2] = it[gy * h // 2:(gy + 1) * h // 2, gx * w // 2:(gx + 1) * w // 2]
                k += 1
                meta['parts'][f'item_{k}'] = bbox_save(cell, os.path.join(a.out, f'item_{k}.webp'))
    json.dump(meta, open(os.path.join(a.out, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('完成', len(meta['parts']), '個圖層')


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
