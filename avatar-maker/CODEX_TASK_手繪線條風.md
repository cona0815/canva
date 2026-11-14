# 給 Codex 的任務：紙娃娃「手繪線條風」風格包 v2.0（2026-11-15）

v2.0 改成格式 2（全身、17 類、表情、動作）。Claude 會直接用命令列叫 Codex 做，老師也可以把分隔線以下整段貼給 Codex（repo 選 `cona0815/canva`）。

---

請在這個 repo 的 `avatar-maker/` 裡，幫我新增一個紙娃娃畫風「手繪線條風」（格式 2）。

1. 先讀 `avatar-maker/packs/README.md`（格式 2 的規則、座標、疊圖順序），再看 `avatar-maker/tools/make_flat.py`（扁平圓潤風的產生程式，格式 2 的完整範例）。
2. 寫一支產生程式 `avatar-maker/tools/make_sketch.py`，執行 `python tools/make_sketch.py packs/sketch/pack.json` 會輸出風格包。
   - 可以 `import make_flat` 拿座標常數（眼睛位置、身體、手臂的肩肘腕位置 `ARMS_GEO`、握點 `HOLD`、夥伴位置），也可以照抄 `POSES`。
   - **每一個部件都要自己重新畫**，不可以直接拿 make_flat 的 SVG 字串來包一層。
   - `id` 用 `sketch`，`name` 用「手繪線條風」，`author` 寫 `Codex`，`version` 寫 `1.0`，`date` 寫今天，`"format": 2`。
3. 畫風要求（要跟扁平圓潤風、Q 版描邊風一眼就看得出不同）：
   - 像兒童繪本的手繪插畫：形狀都有深色手繪描邊（#2d2a32，粗細 7～10），線條要有一點點不規則的抖動感（用程式在路徑上加小小的隨機偏移，固定亂數種子，每次產生結果一樣）。
   - 上色是平塗，再加一兩塊淺色的蠟筆感陰影或亮面（用半透明形狀做，不要用漸層或濾鏡）。
   - 頭身比例正常一點（頭不要特別大），眼睛偏小、鼻子明顯，臉頰有淡淡的圓形腮紅。
4. 款數至少：臉型 4、髮型 12、眉毛 4、眼睛 8、嘴巴 6、鼻子 3、臉部裝飾 4、眼鏡 3、帽子頭飾 8、耳機麥克風 2、上衣 12、外套 4、下身 6、鞋子 4、手持物 6、背後 3、夥伴 3。
   - 眼睛每款都要有 `open` 和 `blink`；嘴巴每款都要有 `closed` 和 `open`。
   - 表情 9 種（normal happy surprised angry cry shy love sleepy wink）、動作 4 種、手臂 7 種都要有。
   - 髮型、服裝不分男女，要涵蓋：學院、運動、舞台偶像、職業（主播、醫生、廚師、消防員、太空人）、奇幻（魔法師、騎士）、動物裝、節慶。
   - 可換色的地方一定要用顏色代號（見 README）。
   - 不可以有真實商標、國旗、隊徽、現有動漫角色造型、暴露服裝、真實武器、血腥恐怖。
5. 執行 `python avatar-maker/tools/check_pack.py avatar-maker/packs/sketch/pack.json`，有錯誤就修到顯示「通過」。
6. 打開 `avatar-maker/packs/sketch/overview.svg` 看圖（可以用 Playwright 截圖），自己檢查有沒有對不齊、超出畫布、手臂和身體接不起來、顏色怪的部件，修好再重新檢查。
7. 在 `avatar-maker/packs/index.json` 加上 `{"id":"sketch","name":"手繪線條風"}`。
8. 只新增或修改這些檔案：`tools/make_sketch.py`、`packs/sketch/`、`packs/index.json`。不要改 `index.html`、`src/`、其他畫風、其他工具程式。
9. 完成後 commit，說明裡附上每一類的款數。
