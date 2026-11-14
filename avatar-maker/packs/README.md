# 紙娃娃風格包格式 v1.0（2026-11-15）

每一種畫風是一個資料夾：`packs/<id>/pack.json`。網頁會讀 `packs/index.json` 列出畫風，選了才載入那一包。

## 基本規則

- 畫布 1000×1000，角色是半身，身體下緣貼齊畫布底部（y=1000）。
- 部件全部是 **SVG 片段**（不含外層 `<svg>`），只能用 `g path circle ellipse rect line polyline polygon`。
- 不可以有：文字、圖片、`<use>`、`<style>`、`<script>`、連結、`url()`、事件屬性。
- 不可以畫：真實商標、球隊隊徽、現有動漫或遊戲角色的造型、暴露服裝、真實武器、血腥。
- 可換色的地方用顏色代號，網頁會換成學生選的顏色：

| 代號 | 意思 |
| --- | --- |
| `{skin}` | 膚色 |
| `{skin2}` | 膚色暗一點（脖子、耳朵、鼻子） |
| `{hair}` | 髮色 |
| `{hair2}` | 髮色暗一點（眉毛） |
| `{eye}` | 眼睛顏色 |
| `{c1}` | 衣服主色 |
| `{c1d}` | 衣服主色暗一點 |
| `{c2}` | 副色（領帶、圖案、配件） |
| `{hat}` | 帽子顏色 |

## pack.json 結構

```json
{
  "id": "sketch",                 // 小寫英文、數字、減號
  "name": "手繪線條風",
  "version": "1.0",
  "date": "2026-11-15",
  "author": "Codex",
  "base":     { "neck": "<SVG>", "ears": "<SVG>" },
  "defaults": { "face":"f1","hair":"h1","brow":"b1","eyes":"e1","mouth":"m1","nose":"","deco":"d1","glasses":"","hat":"","top":"t1","hand":"" },
  "view":     { "eyes": "230 210 540 540" },   // 選項縮圖要放大的區域（viewBox），可省略
  "cats": {
    "face":  { "name":"臉型", "none":false, "opts":[ {"id":"f1","name":"圓臉","svg":"<SVG>"} ] },
    "hair":  { "name":"髮型", "none":true, "noneName":"光頭",
               "opts":[ {"id":"h1","name":"短髮","front":"<SVG 在臉前面>","back":"<SVG 在身體後面，可省略>"} ] },
    "eyes":  { "name":"眼睛", "none":false, "opts":[ {"id":"e1","name":"圓圓眼","open":"<SVG>","blink":"<眨眼 SVG>"} ] },
    "mouth": { "name":"嘴巴", "none":false, "opts":[ {"id":"m1","name":"微笑","closed":"<閉嘴 SVG>","open":"<張嘴 SVG>"} ] }
    // 其他分類 brow nose deco glasses hat top hand 都是 {"id","name","svg"}
  }
}
```

11 個分類都要有：`face hair brow eyes mouth nose deco glasses hat top hand`。
`none:true` 表示學生可以選「不要」。臉型、眼睛、嘴巴、上衣不能是空的。

## 疊圖順序（從底到頂）

後髮 → 上衣 → 脖子 → 耳朵 → 臉型 → 臉部裝飾 → 嘴巴 → 鼻子 → 眼睛 → 眉毛 → 前髮 → 眼鏡 → 帽子頭飾 → 手持物

## 每一類建議款數

臉型 3、髮型 6、眉毛 3、眼睛 4、嘴巴 4、鼻子 2、臉部裝飾 3、眼鏡 2、帽子頭飾 5、上衣 6、手持物 3（越多越好）。

## 檢查

```
python avatar-maker/tools/check_pack.py avatar-maker/packs/<id>/pack.json
```

通過後會在同一個資料夾輸出 `overview.svg`，所有部件套在預設角色上的總覽圖，用瀏覽器打開檢查。
最後把 `{"id":"<id>","name":"<名稱>"}` 加進 `packs/index.json`。

範例：`packs/chibi/pack.json`（Q 版描邊風）。
