# 交接文件：紙娃娃角色產生器 v1.1（2026-11-15）

給接手的 Claude Code。v1.0 交接文件（`HANDOFF_紙娃娃角色產生器_v1.0_2026-11-15.md`）的第 1、2 節（課程需求、老師的工作習慣）仍然有效，這份只寫 v0.3 之後的現況。

- Repo：`cona0815/canva`（GitHub Pages），本專案在 `avatar-maker/`
- 網址：https://cona0815.github.io/canva/avatar-maker/　教學頁：`avatar-maker/guide.html`
- 目前版本：網頁 v0.4（2026-11-15）：三種畫風（扁平圓潤風、Q 版描邊風、手繪線條風）

---

## 1. v0.3 做了什麼（第 2 階段完成、第 3、4 階段大部分完成）

- **風格包格式 2**：全身 1000×1400、半身＝裁上方 1000×1000；17 類部件；手臂依動作畫；表情 9 種可覆蓋眼睛、嘴巴、眉毛並加特效；動作 4 種（站立、揮手、叉腰、比讚）。格式 1 的包仍可讀（只有半身、不顯示新分類）。
- **扁平圓潤風、Q 版描邊風各 164 個部件**（臉 4、髮 24、眉 6、眼 10、嘴 7、鼻 4、裝飾 8、眼鏡 6、帽子 15、耳機 4、上衣 24、外套 8、下身 12、鞋 8、手持物 12、背後 6、夥伴 6）。
- **背景 11 種**（透明、6 種純色、天空、新聞台、教室、舞台、星空），下載時可選要不要背景，預設透明。
- **角色代碼 DQ2**（約 330 字，比 DQ1 短一半）；v0.2 的 DQ1 代碼和舊的自動存檔都還能還原（舊「白色」背景 id 是 `none`、「格線」是 `grid`，已自動轉換）。
- **版面**：1366×768 螢幕（瀏覽器內 1366×657）一頁放得下，每一類選項都不用捲；平板、手機改成上下排。
- **離線版**：所有畫風包在一個 HTML，直接雙擊就能開（網路不穩時用）。
- **教學頁** `guide.html`：下載 → 解壓縮 → 上傳 → 閉嘴墊底 → 文字轉語音 → 說話 GIF 疊在有聲音的地方 → 眨眼 → 下載 MP4。
- 主播包 zip 多了「使用說明.txt」。

### 採用的建議值（v1.0 第 7 節）

| 問題 | 採用 |
| --- | --- |
| 第一版畫風 | 扁平、Q 版、手繪（手繪交給 Codex，見第 5 節） |
| 日系動漫風、像素風 | 先不做 |
| 全身動作 | 4 種；用「手臂分開畫」的做法，上衣和外套不用每個動作各畫一版 |
| 規格書「一個部件一個檔＋manifest.json」 | 不採用，繼續用一個 pack.json（檢查、載入、離線打包都比較簡單） |

## 2. 檔案結構

```
avatar-maker/
├─ index.html                                       ← 上線版 v0.4（build.py 產生，不要手改）
├─ 紙娃娃角色產生器_v0.3_2026-11-15.html             ← 版本存檔（同 index.html）
├─ 紙娃娃角色產生器_離線版_v0.3_2026-11-15.html      ← 離線版（全部畫風包進去）
├─ 紙娃娃角色產生器_v0.1／v0.2_….html               ← 舊版存檔
├─ guide.html、教學_主播包放進Canva_v1.0_2026-11-15.html
├─ src/app.html                                     ← 網頁原始檔（要改網頁改這裡）
├─ packs/
│  ├─ index.json        ← 畫風清單（flat 內建，不用列）
│  ├─ README.md         ← 風格包格式 v2.0（座標、疊圖順序、款數）
│  ├─ flat/  pack.json overview.svg   ← make_flat.py 產生
│  └─ chibi/ pack.json overview.svg   ← make_chibi.py 產生
├─ tools/
│  ├─ build.py          ← 重做風格包＋產生三個 HTML；版本號、日期改檔頭兩行
│  ├─ make_flat.py      ← 扁平圓潤風（所有部件都在這裡畫）
│  ├─ make_chibi.py     ← 拿扁平風加工成 Q 版：頭 ×1.12、身體 ×0.85 往上提、加描邊、換眼睛嘴巴
│  ├─ check_pack.py     ← 風格包檢查 v2.0（格式 1／2），輸出 overview.svg
│  └─ test_app.py       ← Playwright 自動驗收
└─ CODEX_TASK_手繪線條風.md   ← 給 Codex 的任務 v2.0（格式 2）
```

## 3. 改版流程

1. 改 `src/app.html` 或 `tools/make_*.py`。
2. 改 `tools/build.py` 檔頭的 `VERSION`、`DATE`。
3. `cd avatar-maker && python tools/build.py`（會重做風格包、產生 index.html＋存檔＋離線版）。
4. `python tools/check_pack.py packs/<id>/pack.json` 每一包都要「通過」，打開 overview.svg 看圖。
5. 開伺服器 `python -m http.server 8766`，跑 `python tools/test_app.py http://localhost:8766/ <截圖資料夾>`，要「全部通過」。
6. README 版本紀錄加一行 → commit → push（老師的習慣：直接推，不用問）。

## 4. 程式架構重點（src/app.html）

- `inner(s, pose, mode)`：組角色。格式 2 疊圖順序見 `packs/README.md`；`check_pack.py` 的 `compose()` 是同一套，**改一邊要改另一邊**。
- 手臂：`base.arms` 7 種（L_down L_wave L_hip L_thumb R_down R_hip R_hold），每種有 `skin`、`long`、`short`、`hand`。袖子顏色由上衣或外套的 `sleeve:{type,fill}` 決定，`{sleeve}` 代號在組合時替換。有手持物時右手自動用 `R_hold`，握點 (604, 886)。
- 表情：`expr[id]` 可以有 `eyes`、`mouth`、`brow`、`over`。學生點眼睛／嘴巴／眉毛時，如果表情蓋住那一類，會自動改回「一般」並提示。
- 縮圖：`THUMB_HIDE` 先拿掉會擋住的東西（例如看上衣時拿掉外套）。
- 背景：`bgSvg()` 引擎自己畫，不在風格包裡。
- 存檔 key 仍是 `dq-avatar-v1`；`state.v=3`。
- 測試介面 `window.__avatar`：`state svg inner enc dec PACK FMT setStyle randomize commit buildGif tab`。

## 5. 手繪線條風（Codex）

- 任務：`CODEX_TASK_手繪線條風.md` v2.0（格式 2，至少約 100 個部件，要寫 `tools/make_sketch.py`）。
- 2026-11-15 Claude 已用命令列叫 Codex 在分支 `codex/sketch`（工作區 `D:\00AI\資訊活動\canva-sketch`）製作；結果見第 7 節。
- 叫 Codex 要用 `C:\Users\cona0\AppData\Local\OpenAI\Codex\bin\<版本資料夾>\codex.exe`（新版）；`bin\codex.exe` 是舊版，讀不了現在的 config.toml（`service_tier = "priority"`）。

## 6. 接下來

- **第 4 階段：課堂試用**：找一個班試一節課，記錄學生卡住的地方（建議觀察：找不到「全身」、下身鞋子在半身看不到、代碼有沒有人用、15 分鐘內能不能下載）。
- 電腦教室有沒有還原卡還沒確認；有的話上課要強調「複製角色代碼」。
- 想加款式：在 `make_flat.py` 對應的清單加一筆（Q 版會自動跟著有），跑 build。
- 第 5 階段（日系動漫風、像素風）照建議值先不做。

## 7. 手繪線條風驗收結果（2026-11-15，v0.4 上線）

- Codex 交件：`tools/make_sketch.py`、`packs/sketch/`（commit 685b999，已合併到 main）。
- 94 個部件：臉 4、髮 12、眉 4、眼 8、嘴 6、鼻 3、裝飾 4、眼鏡 3、帽子 10、耳機 2、上衣 12、外套 4、下身 6、鞋 4、手持物 6、背後 3、夥伴 3；表情 9、動作 4、手臂 7 都有。
- Claude 驗收：check_pack 通過；產生程式固定亂數種子、可重現（原本 date 用執行當天，已改成固定 2026-11-15）；逐頁看 overview：繪本手繪感、小眼睛明顯鼻子，跟另外兩種畫風看得出不同，手臂、袖子、表情都對得上；test_app 隨機 100 次通過。
- 還不是完整包（完整包約 160）。要補款式時，照 `CODEX_TASK_手繪線條風.md` 的格式另寫一份「補款式」任務給 Codex，改 `make_sketch.py` 後跑 `python tools/build.py`。
