#!/usr/bin/env python3
"""紙娃娃角色產生器 建置程式 v2.0 2026-11-15
用法（在 avatar-maker 資料夾執行）：python tools/build.py
由 src/app.html 產生：
  - index.html                                   上線版（從 packs/<畫風>/ 載入 AI 圖層）
  - 紙娃娃角色產生器_v<版本>_<日期>.html          版本存檔（和 index.html 一樣）
  - 紙娃娃角色產生器_離線版_v<版本>_<日期>.html   離線版（三種畫風的圖都包進去，直接雙擊就能開）
風格包由 tools/make_raster_pack.py 產生（Codex 畫的圖 → 拆圖層）。
v0.4 以前的 SVG 版：src/app_svg_v0.4.html，產生程式 make_flat.py／make_chibi.py／make_sketch.py 保留不再使用。
版本號和日期改下面兩行。
"""
import base64, json, os

VERSION = '1.8'
DATE = '2026-11-24'

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
src = open('src/app.html', encoding='utf-8').read().replace('@@VERSION@@', VERSION).replace('@@DATE@@', DATE)
styles = json.load(open('packs/index.json', encoding='utf-8'))


def embed():
    out = {}
    for st in styles:
        d = f'packs/{st["id"]}'
        pack = json.load(open(f'{d}/parts.json', encoding='utf-8'))
        img = {}
        for f in os.listdir(d):
            if f.endswith('.webp'):
                img[f[:-5]] = 'data:image/webp;base64,' + base64.b64encode(open(f'{d}/{f}', 'rb').read()).decode()
        out[st['id']] = {'pack': pack, 'img': img}
    return json.dumps(out, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


online = src
offline = src.replace('/*@@EMBED@@*/null', embed()).replace('href="guide.html"', 'href="https://cona0815.github.io/canva/avatar-maker/guide.html"')
outs = {'index.html': online, f'紙娃娃角色產生器_v{VERSION}_{DATE}.html': online, f'紙娃娃角色產生器_離線版_v{VERSION}_{DATE}.html': offline}
for name, text in outs.items():
    open(name, 'w', encoding='utf-8', newline='\n').write(text)
    print(f'{name}  {len(text.encode("utf-8")) // 1024} KB')
