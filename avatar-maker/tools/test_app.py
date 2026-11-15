#!/usr/bin/env python3
"""紙娃娃角色產生器 自動驗收 v2.0 2026-11-15（v0.5 點陣圖版）
先開本機伺服器（在 avatar-maker 資料夾）：python -m http.server 8766
再執行：python tools/test_app.py [網址] [截圖資料夾]
檢查：1366×768 一頁放得下、三種畫風都載得進來、隨機 60 次畫得出來且不是空白、角色代碼來回、
      下載主播包（PNG 尺寸、GIF、代碼）、離線版雙擊可開、手機寬度不橫向捲動、沒有 console 錯誤。
"""
import asyncio, io, sys, zipfile, os, glob, pathlib
from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8766/'
SHOTS = sys.argv[2] if len(sys.argv) > 2 else None
HERE = pathlib.Path(__file__).resolve().parent.parent
fails = []


def check(ok, msg):
    print(('  ✔ ' if ok else '  ✘ ') + msg)
    if not ok:
        fails.append(msg)


RANDOM_JS = """(n)=>{const A=window.__avatar,bad=[];
  for(let i=0;i<n;i++){A.randomize();
    for(const mode of ['half','full']){A.commit({mode});
      const c=A.renderTo({mouth:i%2?'open':'closed'},200);const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
      let op=0;for(let j=3;j<d.length;j+=16)if(d[j]>200)op++;
      if(op<200)bad.push('畫出來幾乎是空的 '+JSON.stringify(A.state));}
    const back=A.dec(A.enc(A.state));for(const k of Object.keys(A.state))if(k!=='v'&&JSON.stringify(back[k])!==JSON.stringify(A.state[k])){bad.push('代碼還原不一樣：'+k);break;}}
  return bad.slice(0,6);}"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 1366, 'height': 657}, accept_downloads=True)
        pg = await ctx.new_page()
        errs = []
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL)
        await pg.evaluate('localStorage.clear()')
        await pg.reload()
        await pg.wait_for_function('window.__avatar && __avatar.PACK && document.getElementById("loading").hidden', timeout=60000)
        styles = await pg.evaluate('__avatar.STYLES.map(s=>s.id)')
        print('畫風：', styles)
        print('【版面 1366×657】')
        for mode in ('half', 'full'):
            await pg.evaluate(f'__avatar.commit({{mode:"{mode}"}})')
            d = await pg.evaluate('[document.documentElement.scrollWidth,document.documentElement.scrollHeight,innerWidth,innerHeight]')
            check(d[0] <= d[2] and d[1] <= d[3], f'{mode} 整頁不用捲動 {d}')
        for st in styles:
            print(f'【畫風 {st}】')
            await pg.evaluate(f'__avatar.setStyle("{st}")')
            await pg.wait_for_function(f'__avatar.state.style==="{st}" && document.getElementById("loading").hidden', timeout=60000)
            cats = await pg.evaluate('Object.fromEntries(Object.entries(__avatar.PACK.cats).map(([k,v])=>[k,v.opts.length]))')
            print('  部件：', cats)
            over = []
            for t in cats:
                await pg.evaluate(f'__avatar.tab="{t}"')
                r = await pg.evaluate('(()=>{const o=document.querySelector("#opts");return [o.scrollHeight,o.clientHeight]})()')
                if r[0] > r[1] + 2:
                    over.append(t)
            check(not over, '每一類選項都不用捲動' + (f'：{over}' if over else ''))
            bad = await pg.evaluate(RANDOM_JS, 60)
            check(not bad, f'{st} 隨機 60 次（半身＋全身）都畫得出來、代碼可還原' + (f'：{bad}' if bad else ''))
            if SHOTS:
                await pg.evaluate('__avatar.randomize();__avatar.commit({mode:"half",bg:"news"})')
                await pg.locator('#stage').screenshot(path=os.path.join(SHOTS, f'stage_{st}.png'))
        print('【下載】')
        await pg.evaluate('__avatar.commit({mode:"full", name:"小橋/測試", bg:"none"})')
        async with pg.expect_download() as dl:
            await pg.click('#bPack')
        d = await dl.value
        z = zipfile.ZipFile(io.BytesIO(open(await d.path(), 'rb').read()))
        names = z.namelist()
        check(d.suggested_filename == '小橋測試_主播包.zip' and len(names) == 6, f'主播包 {d.suggested_filename}：{names}')
        png = z.read('小橋測試_閉嘴.png')
        w, h = int.from_bytes(png[16:20], 'big'), int.from_bytes(png[20:24], 'big')
        check((w, h) == (1024, 1536), f'全身 PNG 尺寸 {w}×{h}')
        gif = z.read('小橋測試_說話.gif')
        check(gif[:6] == b'GIF89a', f'說話 GIF {int.from_bytes(gif[6:8], "little")}×{int.from_bytes(gif[8:10], "little")}')
        code = z.read('小橋測試_角色代碼.txt').decode()
        check(code.startswith('DQ5-'), f'角色代碼 {len(code)} 字')
        if SHOTS:
            for n in names:
                if n.endswith(('.png', '.gif')):
                    open(os.path.join(SHOTS, 'dl_' + n), 'wb').write(z.read(n))
        print('【手機 390 寬】')
        await pg.set_viewport_size({'width': 390, 'height': 844})
        await pg.wait_for_timeout(300)
        d = await pg.evaluate('[document.documentElement.scrollWidth, innerWidth]')
        check(d[0] <= d[1], f'不會左右捲動 {d}')
        check(not errs, '沒有 console 錯誤' + (f'：{errs[:5]}' if errs else ''))
        print('【離線版】')
        off = sorted(glob.glob(str(HERE / '紙娃娃角色產生器_離線版_v*.html')))[-1]
        pg2 = await b.new_page(viewport={'width': 1366, 'height': 657})
        e2 = []
        pg2.on('pageerror', lambda e: e2.append(str(e)))
        await pg2.goto(pathlib.Path(off).as_uri())
        await pg2.wait_for_function('window.__avatar && __avatar.PACK && document.getElementById("loading").hidden', timeout=60000)
        n = await pg2.evaluate('__avatar.STYLES.length')
        check(n == len(styles) and not e2, f'{os.path.basename(off)} 雙擊可開，{n} 種畫風')
        await b.close()
    print('結果：' + ('全部通過' if not fails else f'{len(fails)} 項沒通過'))
    return 1 if fails else 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(asyncio.run(main()))
