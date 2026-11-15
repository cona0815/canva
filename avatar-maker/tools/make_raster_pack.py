#!/usr/bin/env python3
"""點陣風格包產生程式 v1.0 2026-11-15
把交接站 AVA-03 裡 Codex 畫的圖（人台＋部件，綠底）拆成圖層，做成網頁用的風格包 packs/<畫風>/。
用法：python tools/make_raster_pack.py <AVA-03 案件資料夾> [畫風 ...]
  會讀：art/R1/base_<畫風>.png、art/R2/<畫風>/*.png、art/R3/<畫風>/*.png（有就讀）
  會寫：packs/<畫風>/parts.json＋每個圖層的 .webp，packs/index.json
"""
import json, os, sys, shutil, subprocess, tempfile

STYLES = {'kawaii': '日式可愛', 'anime': '日式漫畫', 'sticker': '韓系貼圖'}
FACES = ['微笑', '開心大笑', '酷酷', '害羞', '驚訝', '生氣', '眨眼得意', '愛心眼']
HAIR = ['清爽短髮', '刺蝟頭', '中分', '旁分瀏海', '齊瀏海長直髮', '雙馬尾', '高馬尾', '丸子頭', '鮑伯頭', '單邊辮子', '蓬鬆捲髮', '層次狼尾']
TOPS = ['主播西裝', '帽 T', '水手服', '運動球衣', '制服背心', '條紋 T 恤', '毛衣', '偶像舞台裝', '醫師袍', '廚師服', '太空衣', '魔法袍',
        '主播套裝', '襯衫領結', '潮 T', '時尚短外套', '針織背心', '亮片舞台外套', '足球衣', '籃球衣']
BOTTOMS = ['西裝褲', '牛仔褲', '百褶裙', '長褲', '舞台短裙', '皮褲', '運動短褲', '籃球褲']
SHOES = ['皮鞋', '短靴', '舞台靴', '足球鞋', '籃球鞋']
HATS = ['主播耳麥', '頭戴耳機', '棒球帽', '貝雷帽', '漁夫帽', '頭戴麥克風', '蝴蝶結', '運動頭帶']
GLASSES = ['圓框眼鏡', '方框眼鏡', '太陽眼鏡']
ITEMS = ['麥克風', '新聞稿', '自拍手機', '遊戲手把', '攝影機', '相機', '珍珠奶茶', '螢光棒', '足球', '籃球', '獎盃']
PETS = ['小貓', '小狗', '小兔', '小機器人']
# 分類：(id, 名稱, 檔名前綴, 款式名, 可以不要時的名字, 換色方式)
CATS = [('face', '表情', 'face', FACES, None, None), ('hair', '髮型', 'hair', HAIR, '光頭', 'all'), ('top', '上衣', 'top', TOPS, None, 'main'),
        ('bottom', '下身', 'bottom', BOTTOMS, '灰短褲', 'main'), ('shoes', '鞋子', 'shoes', SHOES, '白球鞋', 'main'), ('hat', '帽子頭飾', 'hat', HATS, '不要', None),
        ('glasses', '眼鏡', 'glasses', GLASSES, '不要', None), ('hand', '手持物', 'hand', ITEMS, '不要', None), ('pet', '夥伴', 'pet', PETS, '不要', None)]


def main():
    case = sys.argv[1]
    styles = sys.argv[2:] or list(STYLES)
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    index = []
    for st in styles:
        tmp = tempfile.mkdtemp()
        shutil.copy(os.path.join(case, 'art', 'R1', f'base_{st}.png'), os.path.join(tmp, 'base.png'))
        for r in ('R2', 'R3', 'R4'):
            d = os.path.join(case, 'art', r, st)
            if os.path.isdir(d):
                for f in os.listdir(d):
                    if f.endswith('.png'):
                        shutil.copy(os.path.join(d, f), os.path.join(tmp, f))
        out = os.path.join(root, 'packs', st)
        if os.path.isdir(out):
            shutil.rmtree(out)
        subprocess.run([sys.executable, os.path.join(here, 'raster_parts.py'), tmp, out], check=True, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
        meta = json.load(open(os.path.join(out, 'parts.json'), encoding='utf-8'))
        P = meta['parts']
        pack = {'format': 3, 'id': st, 'name': STYLES[st], 'version': '1.0', 'date': '2026-11-15', 'author': 'Codex 畫圖、Claude 拆圖層',
                'canvas': meta['canvas'], 'halfH': meta['canvas'][0], 'base': P['base'], 'cats': {}}
        W, H = meta['canvas']; hs = (meta['neck'] - meta['top']) * 1.35
        pack['headBox'] = [round((meta['cx'] - hs / 2) / W, 4), round(max(0, meta['top'] - hs * .12) / H, 4), round(hs / W, 4)]
        for cid, cname, pre, names, none, rc in CATS:
            opts = []
            for i, n in enumerate(names, 1):
                if cid == 'face':
                    keys = [f'face_{i}_{s}' for s in ('closed', 'open', 'blink')]
                    if all(k in P for k in keys):
                        opts.append({'id': str(i), 'name': n, 'closed': P[keys[0]], 'open': P[keys[1]], 'blink': P[keys[2]]})
                else:
                    k = f'{pre}_{i:02d}'
                    if k in P:
                        opts.append(dict({'id': k, 'name': n}, **P[k]))
            if opts:
                c = {'name': cname, 'opts': opts}
                if none:
                    c['none'] = none
                if rc:
                    c['recolor'] = rc
                pack['cats'][cid] = c
        json.dump(pack, open(os.path.join(out, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        shutil.rmtree(tmp)
        print(st, {k: len(v['opts']) for k, v in pack['cats'].items()})
        index.append({'id': st, 'name': STYLES[st]})
    allidx = {x['id']: x for x in json.load(open(os.path.join(root, 'packs', 'index.json'), encoding='utf-8')) if x['id'] in STYLES} if os.path.exists(os.path.join(root, 'packs', 'index.json')) else {}
    for x in index:
        allidx[x['id']] = x
    order = [allidx[k] for k in STYLES if k in allidx]
    json.dump(order, open(os.path.join(root, 'packs', 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
