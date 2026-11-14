# 給 Codex 的任務：紙娃娃「手繪線條風」風格包 v1.0（2026-11-15）

把下面整段貼給 Codex（選 GitHub repo `cona0815/canva`）。

---

請在這個 repo 的 `avatar-maker/` 裡，幫我新增一個紙娃娃畫風「手繪線條風」。

1. 先讀 `avatar-maker/packs/README.md`（格式規則），再看範例 `avatar-maker/packs/chibi/pack.json`。
2. 新增 `avatar-maker/packs/sketch/pack.json`，`id` 用 `sketch`，`name` 用「手繪線條風」，`author` 寫 `Codex`，`date` 寫今天。
3. 畫風要求：
   - 像兒童繪本的手繪插畫：所有形狀都有深色手繪描邊（#2d2a32，粗細 8～12），線條可以有一點點不規則的抖動感。
   - 上色是平塗，再加一兩塊淺色的蠟筆感陰影（用半透明形狀做，不要用漸層或濾鏡）。
   - 跟範例的 Q 版描邊風要明顯不同：頭身比例正常一點（頭不要特別大），眼睛偏小、鼻子明顯。
4. 每一個 SVG 都要自己用程式碼畫（path、circle、ellipse、rect 等），不要嵌入圖片，不要文字。
5. 款數至少：臉型 4、髮型 10、眉毛 4、眼睛 6、嘴巴 6、鼻子 3、臉部裝飾 4、眼鏡 3、帽子頭飾 8、上衣 10、手持物 5。
   - 眼睛每款都要有 `open` 和 `blink`（眨眼）；嘴巴每款都要有 `closed` 和 `open`（張嘴說話用）。
   - 髮型、服裝不分男女，要涵蓋：學院、運動、舞台偶像、職業（主播、醫生、廚師、消防員、太空人）、奇幻（魔法師、騎士）、動物裝。
   - 可換色的地方一定要用顏色代號 `{skin}{skin2}{hair}{hair2}{eye}{c1}{c1d}{c2}{hat}`。
6. 所有部件都要對齊同一個 1000×1000 畫布：先決定臉的位置，眼睛、嘴巴、頭髮、帽子都照它對齊。
7. 寫完後執行 `python avatar-maker/tools/check_pack.py avatar-maker/packs/sketch/pack.json`，有錯誤就修到顯示「通過」。
8. 用瀏覽器打開 `avatar-maker/packs/sketch/overview.svg`，自己檢查有沒有對不齊、超出畫布、顏色怪的部件，修好再重新檢查。
9. 在 `avatar-maker/packs/index.json` 加上 `{"id":"sketch","name":"手繪線條風"}`。
10. 開一個新分支，提交成一個 Pull Request，說明裡附上每一類的款數。不要改 `avatar-maker/index.html` 和其他畫風的檔案。
