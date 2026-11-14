# 紙娃娃風格包格式 v2.0（2026-11-15）

每一種畫風是一個資料夾：`packs/<id>/pack.json`。網頁會讀 `packs/index.json` 列出畫風，選了才載入那一包。
現在有兩種格式，網頁兩種都能讀：

| | 格式 1（v1.0） | 格式 2（v2.0，建議） |
| --- | --- | --- |
| 寫法 | 沒有 `format` 欄位 | `"format": 2` |
| 身體 | 只有半身 1000×1000 | 全身 1000×1400，半身＝裁上方 1000×1000 |
| 分類 | 11 類 | 17 類 |
| 表情、動作 | 沒有 | 表情 9 種、動作 4 種 |

扁平圓潤風（`flat`）和 Q 版描邊風（`chibi`）是格式 2，由 `tools/make_flat.py`、`tools/make_chibi.py` 產生，**不要手改 pack.json**，改產生程式再跑 `python tools/build.py`。

## 共同規則

- 部件全部是 **SVG 片段**（不含外層 `<svg>`），只能用 `g path circle ellipse rect line polyline polygon`，可以用 `transform`。
- 不可以有：文字、圖片、`<use>`、`<style>`、`<script>`、`<defs>`、漸層、濾鏡、連結、`url()`、事件屬性。
- 不可以畫：真實商標、球隊隊徽、國旗、現有動漫或遊戲角色的造型、暴露服裝、真實武器、血腥恐怖。服裝、髮型不分男女。
- 可換色的地方用顏色代號，網頁會換成學生選的顏色：

| 代號 | 意思 | 格式 |
| --- | --- | --- |
| `{skin}` `{skin2}` | 膚色、暗一點的膚色（脖子、耳朵、鼻子） | 1、2 |
| `{hair}` `{hair2}` | 髮色、暗一點的髮色（眉毛） | 1、2 |
| `{eye}` | 眼睛顏色 | 1、2 |
| `{c1}` `{c1d}` `{c2}` | 上衣主色、暗一點的主色、副色（領帶、圖案、手持物） | 1、2 |
| `{hat}` | 帽子頭飾 | 1、2 |
| `{acc}` | 耳機麥克風 | 2 |
| `{coat}` `{coatd}` | 外套 | 2 |
| `{pants}` `{pantsd}` | 下身 | 2 |
| `{shoe}` | 鞋子 | 2 |
| `{back}` `{backd}` | 背後的東西 | 2 |
| `{pet}` `{petd}` | 夥伴 | 2 |
| `{sleeve}` | 袖子（只能用在 `base.arms`，網頁會換成上衣或外套的袖子顏色） | 2 |

## 格式 2 的座標（全部部件都要對齊）

| 東西 | 位置 |
| --- | --- |
| 臉 | 圓心 (500, 430)，半徑約 220；頭頂約 y=184 |
| 眼睛 | (410, 400)、(590, 400) |
| 嘴巴 | 約 (500, 530) |
| 耳朵 | (282, 450)、(718, 450) |
| 脖子 | x 456～544，y 600～730 |
| 身體 | 肩膀 y≈714，左右 x 328～672，衣服下襬 y≈1040 |
| 腿 | 左腿 x 400～482、右腿 x 518～600，y 980～1370 |
| 鞋子 | 腳底 y≈1395，左腳中心 x=440、右腳 x=560 |
| 右手拿東西的握點 | (604, 886) |
| 夥伴 | 全身：腳底中心 (830, 1396)；半身：(160, 1000) 縮小 0.82 |
| 帽子最高 | 不要高過 y=40 |

半身時只看得到 y=0～1000，所以上衣的重點圖案要畫在 y=1000 以上。

## pack.json 結構（格式 2）

```json
{
  "format": 2,
  "id": "sketch",                 // 小寫英文、數字、減號
  "name": "手繪線條風",
  "version": "1.0", "date": "2026-11-15", "author": "Codex",
  "base": {
    "neck": "<SVG>", "ears": "<SVG>",
    "legs": "<SVG，兩條腿（膚色）>",
    "arms": {                     // 7 種手臂，每種都要有 skin long short hand 四段
      "L_down":  {"skin":"<整隻手臂膚色>","long":"<長袖，用 {sleeve}>","short":"<短袖，用 {sleeve}>","hand":"<手掌>"},
      "L_wave": {...}, "L_hip": {...}, "L_thumb": {...},
      "R_down": {...}, "R_hip": {...}, "R_hold": {...}   // R_hold：手在握點 (604,886)
    }
  },
  "poses": {                      // 4 種動作：左手、右手各用哪一種手臂
    "stand": {"name":"站立","L":"L_down","R":"R_down"},
    "wave":  {"name":"揮手","L":"L_wave","R":"R_down"},
    "hips":  {"name":"叉腰","L":"L_hip","R":"R_hip"},
    "thumb": {"name":"比讚","L":"L_thumb","R":"R_down"}
  },
  "expr": {                       // 9 種表情，可以換掉眼睛、嘴巴、眉毛，再加一層特效 over
    "normal":   {"name":"一般"},
    "happy":    {"name":"開心","eyes":{"open":"..","blink":".."},"mouth":{"closed":"..","open":".."},"over":".."},
    "surprised":{"name":"驚訝","brow":"..","mouth":{...}},
    "angry": {...}, "cry": {...}, "shy": {...}, "love": {...}, "sleepy": {...}, "wink": {...}
  },
  "defaults": {"face":"f1","hair":"h1","brow":"b1","eyes":"e1","mouth":"m1","nose":"","deco":"","glasses":"","hat":"","headset":"",
               "top":"t1","coat":"","bottom":"p1","shoes":"z1","hand":"","back":"","pet":""},
  "view": {"eyes":"290 270 420 420"},   // 各分類選項縮圖的放大範圍（viewBox），可省略
  "cats": {
    "face":  {"name":"臉型","none":false,"opts":[{"id":"f1","name":"圓臉","svg":"<SVG>"}]},
    "hair":  {"name":"髮型","none":true,"noneName":"光頭","opts":[{"id":"h1","name":"短髮","front":"<臉前面>","back":"<身體後面，可省略>"}]},
    "eyes":  {"name":"眼睛","none":false,"opts":[{"id":"e1","name":"圓圓眼","open":"<SVG>","blink":"<眨眼>"}]},
    "mouth": {"name":"嘴巴","none":false,"opts":[{"id":"m1","name":"微笑","closed":"<閉嘴>","open":"<張嘴>"}]},
    "top":   {"name":"上衣","none":false,"opts":[{"id":"t1","name":"T 恤","svg":"<SVG>","sleeve":{"type":"short","fill":"{c1}"}}]},
    "coat":  {"name":"外套","none":true,"opts":[{"id":"o1","name":"運動外套","svg":"<SVG>","sleeve":{"type":"long","fill":"{coat}"}}]},
    "back":  {"name":"背後","none":true,"opts":[{"id":"q1","name":"後背包","svg":"<身體後面>","front":"<身體前面，例如背帶，可省略>"}]},
    "pet":   {"name":"夥伴","none":true,"opts":[{"id":"x1","name":"小貓","svg":"<全身時的位置>","half":"<半身時的位置>"}]}
    // 其他分類 brow nose deco glasses hat headset bottom shoes hand 都是 {"id","name","svg"}
  }
}
```

- 17 個分類都要有：`face hair brow eyes mouth nose deco glasses hat headset top coat bottom shoes hand back pet`。
- `none:true` 表示學生可以選「不要」。臉型、眼睛、嘴巴、上衣、下身不能是空的。
- `sleeve.type`：`long` 長袖、`short` 短袖、`none` 無袖（外套用 `none` 時就用上衣的袖子）。

## 疊圖順序（從底到頂，格式 2）

背後 → 後髮 → 腿 → 鞋子 → 下身 → 上衣 → 外套 → 背後物的前面（背帶） → 左手臂 → 右手臂 → 脖子 → 耳朵 → 臉型 → 臉部裝飾 → 嘴巴 → 鼻子 → 眼睛 → 前髮 → 眉毛 → 表情特效 → 眼鏡 → 帽子頭飾 → 耳機麥克風 → 手持物 → 兩隻手掌 → 夥伴

- 有拿東西時，右手自動換成 `R_hold`。
- 學生選「沒有眉毛」時，表情的眉毛也不畫。

格式 1 的疊圖順序：後髮 → 上衣 → 脖子 → 耳朵 → 臉型 → 臉部裝飾 → 嘴巴 → 鼻子 → 眼睛 → 眉毛 → 前髮 → 眼鏡 → 帽子頭飾 → 手持物。

## 款數

| 分類 | 完整包 | 最少 |
| --- | --- | --- |
| 臉型 | 4 | 3 |
| 髮型 | 24 | 6 |
| 眉毛 | 6 | 3 |
| 眼睛 | 10 | 4 |
| 嘴巴 | 7 | 4 |
| 鼻子 | 4 | 2 |
| 臉部裝飾 | 8 | 3 |
| 眼鏡 | 6 | 2 |
| 帽子頭飾 | 14 | 5 |
| 耳機麥克風 | 4 | 2 |
| 上衣 | 24 | 6 |
| 外套 | 8 | 3 |
| 下身 | 12 | 4 |
| 鞋子 | 8 | 3 |
| 手持物 | 10 | 3 |
| 背後 | 6 | 2 |
| 夥伴 | 6 | 2 |

## 檢查

```
python avatar-maker/tools/check_pack.py avatar-maker/packs/<id>/pack.json
```

通過後會在同一個資料夾輸出 `overview.svg`：所有部件套在預設角色上，最後還有表情、動作、半身的總覽，用瀏覽器打開檢查。
最後把 `{"id":"<id>","name":"<名稱>"}` 加進 `packs/index.json`，網頁不用改就會出現在「畫風」選單。

範例：`tools/make_flat.py`（產生扁平圓潤風）、`tools/make_chibi.py`（拿扁平風加工成 Q 版）。
