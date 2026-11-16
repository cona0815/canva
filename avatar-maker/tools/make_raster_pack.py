#!/usr/bin/env python3
"""點陣風格包產生程式 v1.4 2026-11-16（加第四畫風 game＝R11；不到 3 款的類別先不放；老師說手持物、夥伴不要了：DROP 的類別不收；加 R6～R9）
把交接站 AVA-03 裡 Codex 畫的圖（人台＋部件，綠底）拆成圖層，做成網頁用的風格包 packs/<畫風>/。
用法：python tools/make_raster_pack.py <AVA-03 案件資料夾> [畫風 ...]
  會讀：art/R1/base_<畫風>.png、art/R2/<畫風>/*.png、art/R3、R3b、R4/<畫風>/*.png（有就讀）
  會寫：packs/<畫風>/parts.json＋每個圖層的 .webp，packs/index.json
"""
import json, os, sys, shutil, subprocess, tempfile

STYLES = {'kawaii': '日式可愛', 'anime': '日式漫畫', 'sticker': '韓系貼圖', 'game': '手遊冒險風'}
MIN_OPTS = 3   # 還沒畫齊、只有一兩款的類別先不放（11-16 老師：手遊風帽子只有 1 款先藏起來）
FINE_FACES = ('game',)   # 線條細的畫風：表情的細閉眼線要另外補回來
FACES = ['微笑', '開心大笑', '酷酷', '害羞', '驚訝', '生氣', '眨眼得意', '愛心眼', '星星眼', '亮晶晶大眼', '調皮吐舌', '自信帥氣', '思考中', '感動淚汪汪']
HAIR = ['清爽短髮', '刺蝟頭', '中分', '旁分瀏海', '齊瀏海長直髮', '雙馬尾', '高馬尾', '丸子頭', '鮑伯頭', '單邊辮子', '蓬鬆捲髮', '層次狼尾', '超長直髮＋呆毛', '雙丸子長辮', '韓系逗號瀏海', '偶像碎蓋', '公主切長髮', '高雙馬尾＋髮圈', '半紮側編髮', '平頭', '短翹髮', '大波浪長捲髮', '雙麻花辮', '側邊單馬尾', '微捲蓬鬆短髮', '兩側推短髮', '低雙馬尾', '蓬鬆中長髮']
TOPS = ['主播西裝', '帽 T', '水手服', '運動球衣', '制服背心', '條紋 T 恤', '毛衣', '偶像舞台裝', '醫師袍', '廚師服', '太空衣', '魔法袍',
        '主播套裝', '襯衫領結', '潮 T', '時尚短外套', '針織背心', '亮片舞台外套', '足球衣', '籃球衣',
        '和風羽織', '科技偶像外套', '小耳朵斗篷', '街頭連帽外套', '棒球外套', '偶像禮服外套', '反光科技外套',
        '格紋襯衫', '牛仔外套', '羽絨外套', '高領毛衣', 'POLO 衫', '恐龍連帽衣', '熊熊連帽衣', '夏威夷花襯衫', '運動拉鍊外套', '偵探風衣', '畫家罩衫', '消防員外套', '學校運動服外套', '立領盤扣上衣', '牛角扣大衣', '開襟毛衣', '羽絨背心', '雨衣', '西裝背心領帶', '毛毛泰迪外套', '衝鋒衣', '鯊魚連帽衣', '貓咪連帽衣', '泡泡袖上衣', '交領漢服上衣', '魔術師燕尾服', '機長制服', '樂隊指揮服', '英雄披風裝', '圍巾毛衣', '冒險者短夾克', '星際旅人長大衣', '單肩斗篷外套', '探險家工裝外套', '飄帶機能外套', '金邊高領外套']
BOTTOMS = ['西裝褲', '牛仔褲', '百褶裙', '長褲', '舞台短裙', '皮褲', '運動短褲', '籃球褲', '吊帶褲', '格紋裙', '工作褲', '運動長褲', '蓬蓬紗裙', '寬褲', '牛仔短褲', '吊帶裙', 'A字牛仔裙', '碎花長裙', '蛋糕裙', '褲裙', '短裙配內搭褲', '喇叭牛仔褲', '百褶長裙', '網球裙', '圓點圓裙']
SHOES = ['皮鞋', '短靴', '舞台靴', '足球鞋', '籃球鞋', '高筒帆布鞋', '雪靴', '雨鞋', '瑪莉珍鞋']
HATS = ['主播耳麥', '頭戴耳機', '棒球帽', '貝雷帽', '漁夫帽', '頭戴麥克風', '蝴蝶結', '運動頭帶', '貓耳髮箍', '狐狸耳髮箍', '兔耳髮箍', '天使光環', '小惡魔角', '貓耳耳機', '星星髮夾', '毛帽', '草帽', '報童帽', '寬髮帶', '小皇冠', '花圈', '魔術師高帽', '機長帽']
GLASSES = ['圓框眼鏡', '方框眼鏡', '太陽眼鏡', '臉頰星星貼紙', '科技單眼鏡片', 'OK繃貼紙', '愛心墨鏡', '半框眼鏡', '臉頰彩繪']
ITEMS = ['麥克風', '新聞稿', '自拍手機', '遊戲手把', '攝影機', '相機', '珍珠奶茶', '螢光棒', '足球', '籃球', '獎盃', '直播麥克風', '星星魔法棒', '愛心應援手燈', '彩虹棉花糖']
PETS = ['小貓', '小狗', '小兔', '小機器人', '飄浮小精靈', '迷你小龍', '水豚', '小幽靈', '果凍史萊姆']
# 11-16 老師說「手持物」「夥伴」可以不要 → 不收這兩類的圖（名單留著，角色代碼格式不變）
DROP = ('hand_', 'pet_')
# 分類：(id, 名稱, 檔名前綴, 款式名, 可以不要時的名字, 換色方式)
CATS = [('face', '表情', 'face', FACES, None, None), ('hair', '髮型', 'hair', HAIR, '光頭', 'all'), ('top', '上衣', 'top', TOPS, None, 'main'),
        ('bottom', '下身', 'bottom', BOTTOMS, '灰短褲', 'main'), ('shoes', '鞋子', 'shoes', SHOES, '白球鞋', 'main'), ('hat', '帽子頭飾', 'hat', HATS, '不要', None),
        ('glasses', '眼鏡臉飾', 'glasses', GLASSES, '不要', None), ('hand', '手持物', 'hand', ITEMS, '不要', None), ('pet', '夥伴', 'pet', PETS, '不要', None)]


def main():
    case = sys.argv[1]
    styles = sys.argv[2:] or list(STYLES)
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    index = []
    for st in styles:
        tmp = tempfile.mkdtemp()
        shutil.copy(os.path.join(case, 'art', 'R1', f'base_{st}.png'), os.path.join(tmp, 'base.png'))
        # 只收已驗收的輪次（環境變數 ROUNDS 可指定，例如 ROUNDS=R2,R3,R3b；避免把 Codex 還在畫的半成品包進去）
        for r in os.environ.get('ROUNDS', 'R2,R3,R3b,R4,R5,R6,R7,R8,R9,R11').split(','):
            d = os.path.join(case, 'art', r, st)
            if os.path.isdir(d):
                for f in os.listdir(d):
                    if f.endswith('.png') and not f.startswith(DROP):
                        shutil.copy(os.path.join(d, f), os.path.join(tmp, f))
        out = os.path.join(root, 'packs', st)
        if os.path.isdir(out):
            shutil.rmtree(out)
        subprocess.run([sys.executable, os.path.join(here, 'raster_parts.py'), tmp, out] + (['--fine-faces'] if st in FINE_FACES else []), check=True, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
        meta = json.load(open(os.path.join(out, 'parts.json'), encoding='utf-8'))
        P = meta['parts']
        pack = {'format': 3, 'id': st, 'name': STYLES[st], 'version': '1.0', 'date': '2026-11-15', 'author': 'Codex 畫圖、Claude 拆圖層',
                'canvas': meta['canvas'], 'halfH': meta['canvas'][0], 'base': P['base'], 'cats': {}}
        W, H = meta['canvas']; hs = (meta['neck'] - meta['top']) * 1.35
        top = meta['top']; hd = meta['neck'] - top
        if (W - top) / hd > 3.6:   # 頭身比高（手遊風約 6 頭身）：半身模式只取頭頂上方一點到約 3.1 個頭高，放大成正方形，取景才和其他畫風一樣
            side = round(hd * 3.4); pack['halfBox'] = [round(meta['cx'] - side / 2), max(0, round(top - hd * .3)), side]
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
            if len(opts) >= MIN_OPTS:
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
