#!/usr/bin/env python3
"""紙娃娃角色產生器 自動驗收 v1.0 2026-11-15
先開本機伺服器（在 avatar-maker 資料夾）：python -m http.server 8766
再執行：python tools/test_app.py [網址] [截圖資料夾]
需要 playwright（pip install playwright && playwright install chromium）。
檢查：1366×768 一頁放得下、各分類選項不用捲、每種畫風隨機 100 次沒有破圖、角色代碼來回、舊代碼 DQ1 還原、下載主播包、手機寬度不橫向捲動、沒有 console 錯誤。
"""
import asyncio, io, json, sys, zipfile, os
from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8766/'
SHOTS = sys.argv[2] if len(sys.argv) > 2 else None
fails = []


def check(ok, msg):
    print(('  ✔ ' if ok else '  ✘ ') + msg)
    if not ok:
        fails.append(msg)


RANDOM_JS = """async (n) => {
  const A = window.__avatar, bad = [];
  const P = new DOMParser();
  for (let i = 0; i < n; i++) {
    A.randomize();
    for (const mode of ['half', 'full']) for (const pose of [{mouth:'closed'}, {mouth:'open'}, {mouth:'closed', eyes:'blink'}]) {
      const s = Object.assign({}, A.state, {mode});
      const t = A.svg(s, pose, A.FMT === 2 ? mode : 'half', null, true);
      if (/\\{\\w+\\}/.test(t)) bad.push('沒換掉的顏色代號 ' + t.match(/\\{\\w+\\}/)[0] + ' ' + JSON.stringify(A.state));
      const d = P.parseFromString(t, 'image/svg+xml');
      if (d.querySelector('parsererror')) bad.push('SVG 解析錯誤 ' + JSON.stringify(A.state));
      if (/undefined|NaN/.test(t)) bad.push('出現 undefined/NaN ' + JSON.stringify(A.state));
    }
    if (i % 10 === 0) {  // 抽樣真的畫成圖片
      const t = A.svg(A.state, {mouth:'open'}, null, null, true, 400, 560);
      const ok = await new Promise(r => { const img = new Image(); img.onload = () => r(img.width > 0); img.onerror = () => r(false);
        img.src = URL.createObjectURL(new Blob([t], {type: 'image/svg+xml'})); });
      if (!ok) bad.push('圖片畫不出來 ' + JSON.stringify(A.state));
    }
    const code = A.enc(A.state), back = A.dec(code);
    for (const k of Object.keys(A.state)) if (k !== 'v' && JSON.stringify(back[k]) !== JSON.stringify(A.state[k])) { bad.push('代碼還原不一樣：' + k); break; }
  }
  return bad.slice(0, 8);
}"""


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
        await pg.wait_for_function('window.__avatar && document.querySelector("#styleSel").options.length >= 2')
        styles = await pg.evaluate('[...document.querySelector("#styleSel").options].map(o=>o.value)')
        print('畫風：', styles)

        print('【版面 1366×657（1366×768 螢幕扣掉瀏覽器工具列）】')
        for mode in ('half', 'full'):
            await pg.evaluate(f'__avatar.commit({{mode:"{mode}"}})')
            dims = await pg.evaluate('[document.documentElement.scrollWidth, document.documentElement.scrollHeight, innerWidth, innerHeight]')
            check(dims[0] <= dims[2] and dims[1] <= dims[3], f'{mode} 整頁不用捲動 {dims}')
            tabs = await pg.evaluate('[...document.querySelectorAll(".tab")].length')
            over = []
            for i in range(tabs):
                await pg.evaluate(f'document.querySelectorAll(".tab")[{i}].click()')
                r = await pg.evaluate('(()=>{const o=document.querySelector("#opts");return [document.querySelector(".tab[aria-selected=true]").textContent,o.scrollHeight,o.clientHeight]})()')
                if r[1] > r[2] + 2:
                    over.append(f'{r[0]}({r[1]}>{r[2]})')
            check(not over, f'{mode} 每一類的選項都不用捲動' + (f'：{over}' if over else ''))
            if SHOTS:
                await pg.evaluate('__avatar.tab="hair"')
                await pg.screenshot(path=os.path.join(SHOTS, f'layout_{mode}.png'))

        for st in styles:
            print(f'【畫風 {st}】')
            await pg.select_option('#styleSel', st)
            await pg.wait_for_function(f'__avatar.state.style==="{st}"')
            bad = await pg.evaluate(RANDOM_JS, 100)
            check(not bad, f'{st} 隨機 100 次（半身＋全身 × 閉嘴／張嘴／眨眼）沒有破圖、代碼可還原' + (f'：{bad}' if bad else ''))
            if SHOTS:
                for i, mode in enumerate(('half', 'full')):
                    await pg.evaluate(f'__avatar.randomize(); __avatar.commit({{mode:"{mode}", bg:"{["stage","news"][i]}"}})')
                    await pg.locator('#stage').screenshot(path=os.path.join(SHOTS, f'stage_{st}_{mode}.png'))

        print('【舊代碼 DQ1（v0.2）】')
        old = {'v': 1, 'style': 'flat', 'name': '測試', 'skin': '#ffdcbf', 'hairC': '#3b2a24', 'eyeC': '#2b2b33', 'c1': '#e2553b', 'c2': '#ffc531', 'hatC': '#e2553b',
               'flip': False, 'bg': 'grid', 'face': 'f2', 'hair': 'h3', 'brow': 'b2', 'eyes': 'e2', 'mouth': 'm2', 'nose': 'n1', 'deco': '', 'glasses': 'g1', 'hat': 'a3', 'top': 't5', 'hand': 'k2'}
        await pg.fill('#codeInput', await pg.evaluate('o=>"DQ1-"+btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/=+$/,"")', old))
        await pg.click('#bLoadCode')
        await pg.wait_for_function('__avatar.state.name==="測試"')
        s = await pg.evaluate('__avatar.state')
        check(all(s[k] == old[k] for k in ('face', 'hair', 'eyes', 'top', 'hand', 'c1')) and s['bg'] == 'none', 'DQ1 舊代碼還原成功（舊背景「格線」→透明）')

        print('【下載】')
        await pg.evaluate('__avatar.commit({mode:"full", name:"小橋/測試"})')
        async with pg.expect_download() as dl:
            await pg.click('#bPack')
        d = await dl.value
        data = open(await d.path(), 'rb').read()
        z = zipfile.ZipFile(io.BytesIO(data))
        names = z.namelist()
        check(d.suggested_filename == '小橋測試_主播包.zip' and len(names) == 6, f'主播包 {d.suggested_filename}：{names}')
        png = z.read('小橋測試_閉嘴.png')
        w, h = int.from_bytes(png[16:20], 'big'), int.from_bytes(png[20:24], 'big')
        check((w, h) == (1000, 1400), f'全身 PNG 尺寸 {w}×{h}')
        gif = z.read('小橋測試_說話.gif')
        gw, gh = int.from_bytes(gif[6:8], 'little'), int.from_bytes(gif[8:10], 'little')
        check(gif[:6] == b'GIF89a' and (gw, gh) == (500, 700), f'說話 GIF {gw}×{gh}')
        code = z.read('小橋測試_角色代碼.txt').decode()
        check(code.startswith('DQ2-') and len(code) < 520, f'角色代碼 {len(code)} 字')
        if SHOTS:
            for n in names:
                if n.endswith(('.png', '.gif')):
                    open(os.path.join(SHOTS, 'dl_' + n), 'wb').write(z.read(n))

        print('【手機 390 寬】')
        await pg.set_viewport_size({'width': 390, 'height': 844})
        await pg.wait_for_timeout(300)
        dims = await pg.evaluate('[document.documentElement.scrollWidth, innerWidth]')
        check(dims[0] <= dims[1], f'不會左右捲動 {dims}')
        if SHOTS:
            await pg.screenshot(path=os.path.join(SHOTS, 'mobile.png'), full_page=True)

        check(not errs, '沒有 console 錯誤' + (f'：{errs[:5]}' if errs else ''))
        await b.close()
    print('結果：' + ('全部通過' if not fails else f'{len(fails)} 項沒通過'))
    return 1 if fails else 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(asyncio.run(main()))
