#!/usr/bin/env python3
"""紙娃娃角色產生器 建置程式 v1.0 2026-11-15
用法（在 avatar-maker 資料夾執行）：python tools/build.py
1. 重新產生風格包：flat（make_flat.py）、chibi（make_chibi.py）、sketch（make_sketch.py，Codex 寫的）
2. 由 src/app.html 產生：
   - index.html                                   上線版（內建扁平圓潤風，其他畫風從 packs/ 載入）
   - 紙娃娃角色產生器_v<版本>_<日期>.html          版本存檔（和 index.html 一樣）
   - 紙娃娃角色產生器_離線版_v<版本>_<日期>.html   離線版（所有畫風都包進去，直接雙擊就能開）
版本號和日期改下面兩行。
"""
import json, os, subprocess, sys

VERSION = '0.4'
DATE = '2026-11-15'

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
py = sys.executable
for cmd in (['tools/make_flat.py', 'packs/flat/pack.json'], ['tools/make_chibi.py', 'packs/chibi/pack.json'], ['tools/make_sketch.py', 'packs/sketch/pack.json']):
    subprocess.run([py] + cmd, check=True, env=dict(os.environ, PYTHONIOENCODING='utf-8'))

src = open('src/app.html', encoding='utf-8').read().replace('@@VERSION@@', VERSION).replace('@@DATE@@', DATE)
dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
flat = json.load(open('packs/flat/pack.json', encoding='utf-8'))
styles = json.load(open('packs/index.json', encoding='utf-8'))


def make(embed_all):
    s = src.replace('/*@@FLAT@@*/null', dump(flat))
    if embed_all:
        packs = {x['id']: json.load(open(f'packs/{x["id"]}/pack.json', encoding='utf-8')) for x in styles if x['id'] != 'flat'}
        s = s.replace('/*@@EMBED@@*/{}', dump(packs)).replace('/*@@EMBED_LIST@@*/[]', dump([x for x in styles if x['id'] != 'flat']))
        s = s.replace('href="guide.html"', 'href="https://cona0815.github.io/canva/avatar-maker/guide.html"')
    return s


online, offline = make(False), make(True)
outs = {'index.html': online, f'紙娃娃角色產生器_v{VERSION}_{DATE}.html': online, f'紙娃娃角色產生器_離線版_v{VERSION}_{DATE}.html': offline}
for name, text in outs.items():
    open(name, 'w', encoding='utf-8', newline='\n').write(text)
    print(f'{name}  {len(text.encode("utf-8")) // 1024} KB')
