#!/usr/bin/env python3
"""動物夥伴（貓、狗、恐龍）圖層 v1.0 2026-11-22
11-22 老師：「多一個類別是可愛的貓狗還有恐龍」。R13 每隻動物三張表情 pet_NN_closed／open／blink（1024×1024 綠底，沒有人台），
動物也可以當主角（網頁 state.hero＝pet：畫面中間只畫這隻動物、會說話）；
這支程式去綠底、裁切，放進 packs/<畫風>/pet_NN.webp，並在 parts.json 加「動物主角」類別（11-22 老師：不要動物夥伴，只當主角；x,y,w,h、half 留著沒用到）：
  x,y,w,h ＝ 當夥伴、全身時的位置（角色右手邊、腳邊地上）；half ＝ 半身時的位置（畫面右下角、肩膀旁邊，放大一點）。
用法：python tools/make_pets.py <AVA-03 案件資料夾> [畫風 ...] [--only=pet_01,pet_05]
  --only：只收驗收過的那幾隻（例如 11-22 先上線三隻樣品：PET_MIN=1 --only=pet_01,pet_05,pet_09）
make_raster_pack.py 做完畫風包也會自動呼叫（只收 R13 驗收過的圖）。
"""
import json, os, sys
import numpy as np
import cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from raster_parts import load, chroma

PETS = ['橘白小貓', '賓士貓', '虎斑貓', '三花貓', '柴犬', '柯基', '白色小狗', '黃金獵犬', '小暴龍', '三角龍', '長頸龍', '劍龍']
STYLES = ('kawaii', 'anime', 'sticker')
MIN_OPTS = int(os.environ.get('PET_MIN', 3))   # 測試時可設 PET_MIN=1


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    case, styles = args[0], [s for s in (args[1:] or STYLES) if s in STYLES]
    only = next((a.split('=', 1)[1].split(',') for a in sys.argv[1:] if a.startswith('--only=')), None)
    for st in styles:
        src = os.path.join(case, 'art', 'R13', st)
        pj = os.path.join(ROOT, 'packs', st, 'parts.json')
        if not os.path.isdir(src) or not os.path.exists(pj):
            continue
        P = json.load(open(pj, encoding='utf-8'))
        W, H = P['canvas']; halfH = P.get('halfH', W); b = P['base']
        cx = b['x'] + b['w'] / 2; bottom = b['y'] + b['h']
        # 大小：全身時約人台身高 23%（到膝蓋上下）；半身時邊長約畫面寬 30%
        full_h = b['h'] * .23; half_h = W * .30
        opts = []
        for i, name in enumerate(PETS, 1):
            pid = f'pet_{i:02d}'
            if only and pid not in only:
                continue
            f = {st_: os.path.join(src, f'{pid}_{st_}.png') for st_ in ('closed', 'open', 'blink')}
            if not os.path.exists(f['closed']):
                continue
            # 三張表情用同一個裁切框（三張的聯集），疊起來才對得齊；缺 open／blink 就先用 closed 代替
            imgs = {k: chroma(load(v if os.path.exists(v) else f['closed'])) for k, v in f.items()}
            # 張嘴、眨眼：只取頭部「真的有變」的地方（嘴巴、眼睛），其他全部用閉嘴那張 → 說話時身體完全不閃
            base_ = imgs['closed']; bm = base_[..., 3] > 128
            if bm.any():
                yy = np.where(bm.any(1))[0]; head_bot = int(yy.min() + (yy.max() - yy.min()) * .55)
                for k in ('open', 'blink'):
                    if not os.path.exists(f[k]):
                        continue
                    v = imgs[k]; d = np.abs(v - base_).max(-1) > 30
                    d[head_bot:] = False
                    d = cv2.dilate(d.astype(np.uint8), np.ones((9, 9), np.uint8))
                    w = cv2.GaussianBlur(d.astype(np.float32), (0, 0), 3)[..., None]
                    imgs[k] = base_ * (1 - w) + v * w
            m = np.zeros(imgs['closed'].shape[:2], bool)
            for v in imgs.values():
                m |= v[..., 3] > 20
            ys, xs = np.where(m)
            if not len(xs):
                continue
            x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
            for k, v in imgs.items():
                im = Image.fromarray(np.clip(v[y0:y1, x0:x1], 0, 255).astype(np.uint8), 'RGBA')
                # 動物主角會放很大（半身時約 900 畫布像素高）：存高 900px
                q = 900 / im.height
                if q < 1:
                    im = im.resize((max(1, round(im.width * q)), 900), Image.LANCZOS)
                im.save(os.path.join(ROOT, 'packs', st, f'{pid}_{k}.webp'), 'WEBP', quality=88, method=6)
            r = im.width / im.height
            fh = full_h; fw = fh * r
            fx = min(W - fw - 8, cx + b['w'] * .30); fy = bottom - fh   # 角色右手邊、腳底對齊
            hh = half_h; hw = hh * r
            if hw > W * .36:   # 長頸龍、劍龍比較寬：寬度限制
                hw = W * .36; hh = hw / r
            hx = W - hw - W * .02; hy = halfH - hh - W * .01       # 半身：右下角
            opts.append({'id': pid, 'name': name, 'x': round(fx, 1), 'y': round(fy, 1), 'w': round(fw, 1), 'h': round(fh, 1),
                         'half': {'x': round(hx, 1), 'y': round(hy, 1), 'w': round(hw, 1), 'h': round(hh, 1)}})
        if len(opts) >= MIN_OPTS:
            P['cats']['pet'] = {'name': '動物主角', 'opts': opts}   # 11-22 老師：不要動物夥伴，動物只當主角
        else:
            P['cats'].pop('pet', None)
        json.dump(P, open(pj, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        print(st, '動物主角', len(opts), '隻')


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
