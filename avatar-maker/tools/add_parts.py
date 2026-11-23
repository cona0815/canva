#!/usr/bin/env python3
"""只把新一輪的部件加進現有的畫風包 v1.0 2026-11-24
make_raster_pack.py 會把整個畫風包從頭重拆（11-17 起 anime 的頭髮圖層會被改掉、fix_holes 補過的洞也要重補），
所以之後加新部件改用這支：只拆指定輪次的圖（同一張人台，位置和整包重拆一模一樣），把新部件的 webp 和 parts.json 項目併進 packs/<畫風>/。
同 id 的舊部件會被換掉；新部件照款式名單的編號排進去（日式漫畫最前面的 ✦ 手遊造型服 top_gNN 不動）。
用法：python tools/add_parts.py <AVA-03 案件資料夾> <輪次，例如 R16> [畫風 ...]
加完記得：python tools/fix_holes.py <案件> <畫風...>（ROUNDS 要含這一輪）→ build.py → test_app.py
"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import make_raster_pack as MRP

PRE = ('hair_', 'top_', 'bottom_', 'shoes_', 'hat_', 'glasses_')


def order_key(o):
    m = re.match(r'[a-z]+_(g?)(\d+)$', o['id'])
    return (0 if m and m.group(1) else 1, int(m.group(2)) if m else 999)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    case, rnd = args[0], args[1]
    styles = [s for s in (args[2:] or ['kawaii', 'anime', 'sticker']) if s in MRP.STYLES]
    for st in styles:
        src = os.path.join(case, 'art', rnd, st)
        pj = os.path.join(ROOT, 'packs', st, 'parts.json')
        if not os.path.isdir(src) or not os.path.exists(pj):
            print(st, '沒有', src); continue
        tmp = tempfile.mkdtemp(); out = tempfile.mkdtemp()
        shutil.copy(os.path.join(case, 'art', 'R1', f'base_{st}.png'), os.path.join(tmp, 'base.png'))
        files = [f for f in os.listdir(src) if f.endswith('.png') and f.startswith(PRE) and re.match(r'[a-z]+_\d+\.png$', f)]
        for f in files:
            shutil.copy(os.path.join(src, f), os.path.join(tmp, f))
        subprocess.run([sys.executable, os.path.join(HERE, 'raster_parts.py'), tmp, out] + (['--fine-faces'] if st in MRP.FINE_FACES else []),
                       check=True, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
        M = json.load(open(os.path.join(out, 'parts.json'), encoding='utf-8'))['parts']
        P = json.load(open(pj, encoding='utf-8'))
        if M['base'] != P['base']:
            print(st, '⚠ 人台位置和現有的包不一樣', M['base'], P['base']); sys.exit(1)
        added = {}
        for cid, cname, pre, names, none, rc in MRP.CATS:
            if cid in ('face', 'hand', 'pet'):
                continue
            for i, n in enumerate(names, 1):
                k = f'{pre}_{i:02d}'
                if k not in M:
                    continue
                for suf in ('', '_erase'):
                    s = os.path.join(out, k + suf + '.webp')
                    if os.path.exists(s):
                        shutil.copy(s, os.path.join(ROOT, 'packs', st, k + suf + '.webp'))
                    elif suf:   # 這次沒有擦除遮罩：舊的也要拿掉
                        old = os.path.join(ROOT, 'packs', st, k + suf + '.webp')
                        if os.path.exists(old):
                            os.remove(old)
                C = P['cats'].setdefault(cid, dict({'name': cname, 'opts': []}, **({'none': none} if none else {}), **({'recolor': rc} if rc else {})))
                C['opts'] = [o for o in C['opts'] if o['id'] != k] + [dict({'id': k, 'name': n}, **M[k])]
                added.setdefault(cid, []).append(n)
        for cid in added:
            P['cats'][cid]['opts'].sort(key=order_key)
        json.dump(P, open(pj, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        shutil.rmtree(tmp); shutil.rmtree(out)
        print(st, '加入', {c: len(v) for c, v in added.items()}, '→', {c: len(v['opts']) for c, v in P['cats'].items()})


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
