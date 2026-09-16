---
name: ig-post-generator
description: 把一篇文章轉成 Instagram 圖文輪播（HTML 排版 + 一鍵出 1080×1350 PNG）。當用戶說「幫我出 IG 貼文」「把這篇文章變成 IG 圖」「做一個 IG carousel」「IG post 圖」「輪播圖」時使用。
agent_created: true
---

# IG Post Generator · Lester Liang 版

用 HTML 排版製作出 Instagram 貼文圖（1080×1350 直度輪播卡），風格骨架參考文字卡排版，色調字體採用 lesterliang.com 的森林綠 × 暖金大地色系 + 療癒系字體。

## 觸發條件

用戶說「幫我出 IG 貼文」「把這篇文章變成 IG 圖」「做一個 IG carousel」「IG post」等，並提供文章／主題／草稿時使用。即使只給一個主題（沒有全文）也可以，這時由你先把主題寫成短文，再拆卡。

## 工作流程

1. **讀輸入**：完整文章、幾段想法、或只有一個主題。
2. **拆卡**：拆成 5–8 張輪播卡：
   - **卡 1 · Hook 封面**：一句鉤子大標，讓人想滑下去。句式參考「如果你是……」或「你不需要……」。
   - **卡 2–N · 內文卡**：每卡只講一個重點，單卡正文不超過 90 字。長句拆行，寧少勿多。
   - **最後一卡 · CTA**：行動呼籲（DM 關鍵字、追蹤、預約連結）。
3. **生成 HTML**：複製 `assets/template.html` 的完整結構與 CSS，只替換每張卡 `.content` 內的文字（連 `<style>` 與 base64 素材一起保留，切勿只用片段）。
4. **改設定區**（見下節）：`handle` 一定要改成這次要發的帳號；`leaves` 決定要不要樹葉背景。
5. **跑檢查**（三支都要跑，很便宜、幾秒鐘）：
   ```
   python scripts/check-orphans.py <deck.html>        # 抓「一個字一行」
   python scripts/check-fit.py <deck.html>            # 抓「內容裝不下被裁切」
   python scripts/export-png.py <deck.html> --out out/  # 出圖
   ```
   `check-fit.py` 看的是每張卡的上下留白。**留白低於 50px 就該減字或降一級字級**——溢出被 `overflow:hidden` 切掉時畫面常常看不出來。
6. **交付**：`present_files` 同時給 HTML（可預覽、可微調）與 PNG（可直接發）。檢查若有孤字，修好再交付。

## 設定區（每次生成只改這裡）

模板 `<body>` 開頭有一個 `IG_CONFIG`：

```js
window.IG_CONFIG = {
  handle : 'lesterleung_07',   // IG 帳號，不用加 @，換帳號只改這行
  leaves : true                // 樹葉背景總開關：false = 全部卡片都不顯示
};
```

- **帳號**：所有 `.handle` 由 JS 統一填入，改一行就全卡生效。不同帳號發文就改這裡。
- **樹葉**：`false` 可一次關掉全部；要「只有某幾張有樹葉」，是在個別 `.card` 上加 class：
  - `class="card leaves-top"` → 樹葉在頂部（適合 Hook 封面）
  - `class="card leaves-bottom"` → 樹葉鏡像到底部（適合 CTA 收尾卡）
  - 不加 class → 乾淨版
  - **建議：不要每張都加。** 封面 + 收尾各一張最耐看，中間內文卡保持乾淨、資訊更清楚。

## 字體：三層分工（療癒感的關鍵）

| 角色 | 字體 | 用在哪 | CSS 變數 |
|---|---|---|---|
| 標題（硬） | Noto Serif TC 700 | Hook 大標、重點句、引號清單、CTA | `--font-title` |
| 正文（柔） | **LXGW WenKai TC** 霞鶩文楷 | 段落、藥丸條、四欄格詞、小標 | `--font-soft` |
| 手寫（點綴） | **Iansui** 芫荽 | note-box、`.kicker`、`.statement-lead` | `--font-hand` |
| 英文數字 | Cormorant Garamond | 數字 badge、頁尾帳號 | `--font-en` |

規則：
- **手寫體只用於「點綴」**——一句話、一個標籤、一個方框。整張卡都用手寫體會顯得隨便、也傷可讀性。
- 大標若想更柔，把 weight 從 900 降到 700（模板已預設 700）。
- 想換字體：改 `:root` 的四個變數即可，全卡生效。TC 手寫／圓潤體的其他選項：`Huninn`（圓潤）、`Cactus Classical Serif`（明體）。

## 排版：避免「一個字一行」

`text-wrap:pretty` 對中文幫助有限（已內建當保險），**真正可靠的是控制每行字數**。

內容區淨寬 = 1080 − 2×56（卡邊距）− 2×90（內距）= **788px**。中文一個字約佔 1em：

| 元素 | 字級 | 淨文字寬 | 建議每行字數 |
|---|---|---|---|
| Hook 大標 | 88px | 788 | **≤ 8** |
| 重點句 statement-body | 56px | 788 | ≤ 12 |
| CTA／引號清單 | 52px | 788／696※ | ≤ 12 |
| 正文 para、小標 kicker | 48px | 788 | ≤ 14 |
| note-box（字距 .08em） | 48px | 656 | ≤ 11 |
| 藥丸條 pill | 44px | 708 | ≤ 14 |
| 清單前言 list-intro | 44px | 788 | ≤ 15 |

※ 引號清單每項有 64px 數字 badge + 36px 間距，可用文字寬只有 696px。

做法：
1. 手動用 `<br>` 決定每一行，別讓瀏覽器自己斷。
2. 每行字數對照上表，留一格餘裕（letter-spacing 也會吃寬度）。
3. 句子太長就改寫短一點，或拆成兩張卡——不要硬縮字級。
4. 跑 `check-orphans.py` 驗證（它逐字量 rect、按行分組，抓出只剩 1 個字的行）。

## 版型規則

畫布 1080 × 1350 px（4:5）。所有尺寸寫死 px，不做響應式。

- **外框**：卡片內留 56px 邊距，內有圓角 48px、1.5px 細邊框的 frame —— 風格的 signature。
- **內容區**：`inset:56px; padding:80px 90px`，flex column 垂直置中。可用高度約 1038px；文字過多會被 `overflow:hidden` 靜默裁切。
- **圖層順序**：裝飾圓 0 → 樹葉 1 → 外框 2 → 內容 3 → 頁尾 4。
- **字級**（2026-09 整體放大一階，對齊參考圖的視覺重量）：
  - Hook 大標 88px / line-height 1.45 / 700
  - 重點句（statement-body）56px / line-height 1.9 / 700
  - CTA、引號清單 52px / 700
  - 正文 para、小標 kicker 48px / line-height 1.9 / 400
  - note-box 48px / letter-spacing .08em（手寫體）
  - 藥丸條 44px / 700 / 文字置中
  - 清單前言 44px
  - 頁尾 handle 28px
  - 數字 badge 64px 圓 / 34px 字
- **強調手法**（風格靈魂，每卡至少一種）：
  - 關鍵字變色 `<em>` = gold，不加斜體
  - 分隔線 `.divider`（64px gold-soft 橫線）或 `.divider.short`
  - 箭頭 `.arrow` ↓ 單獨一行置中
  - 藥丸條 `.pill` / `.pill.alt`（forest-tint 與 paper 交替）
  - 數字 badge `.num`（圓形 forest 底白字，Cormorant 數字）
  - 引號句「……」直接放正文，關鍵字用 `<em>`
  - `.note-box` 米色圓角方框（手寫體）
- **四欄格** `.grid4`：4 個並列概念，數字 → 詞 → SVG 線條 icon（`stroke:var(--forest)`，viewBox 24×24，92px）。**禁止 Emoji**，只用手繪風格 SVG。
- **裝飾** `.deco`：blur 圓形，sage／paper 色，放角落。
- **頁尾**：`.handle` 置中，帶柔光 `text-shadow`，墊在樹葉上仍看得清。

## 色票 tokens（來源 lesterliang.com，名稱與網站一致，勿改色值）

```
--warm-white: #FFFDF8          頁面底
--cream:      #FAF9F7          卡片底
--paper:      #F4F0E6          米色面塊／note-box
--gray:       #EBE8E0          次要面塊
--forest:     #2E5E4E          主色（badge、icon）
--forest-deep:#234839          標題
--forest-soft:#3D6B58          次要強調
--forest-tint:#E7EFEB          淺綠藥丸底
--gold:       #B8893B          關鍵字、分隔線
--gold-soft:  #C9A464          裝飾線、箭頭
--ink-soft:   #6B6256          正文、頁尾
--sage:       #A8BFB2          裝飾圓
--charcoal:   #14201B          最深文字
--on-forest:  #F7F5F0          深底上的文字
--line:       rgba(20,32,27,.10)  網站標準細線
--line-warm:  #E8DFD0          IG 卡片專用暖色框線（網站無此 token）
```

網站另有 dark theme 對應值（`--cream:#1A1E1C`、`--forest:#7FB39E`、`--gold:#D4A869` 等）與圓角規範（`--radius-card:18px`、`--radius-pill:999px`）。要確認最新色值，用 `html-render-verify` skill 的 `extract-tokens.py`：

```bash
python ~/.workbuddy/skills/html-render-verify/scripts/extract-tokens.py https://www.lesterliang.com/
```

## 樹葉素材

`assets/leaf-bg.png`（1280×1150、透明、134KB）由 `scripts/make-leaf-bg.py` 從帶棋盤格的 JPG 去背而來（同時清掉右下角浮水印）。

**它被 base64 內嵌在 template.html 裡**（`--leaf-img` 變數），不是外部連結——這是必要的，原因見「常見坑」。

換樹葉圖：
1. 準備透明 PNG（或改 `make-leaf-bg.py` 的來源路徑重新去背）
2. `python scripts/embed-leaf.py` 重新內嵌
3. 重跑 `check-orphans.py` + `export-png.py` 複驗

## 合規（保險／金融內容適用）

涉及保險或投資時：禁止「保證、穩賺、零風險、像定存」等詞；非保證利益必須標示；過往績效同句標註「過往不代表未來」。

## 常見坑

- **html2canvas 會靜默跳過本地圖片！** 用 `file://` 開 HTML 時，本地 `<img>`／CSS 背景圖會被視為跨來源、直接不畫（不報錯、只是圖不見）。所以**任何圖片素材都必須 base64 內嵌**。這條踩過：樹葉用外部 PNG 時，匯出圖完全沒有樹葉。改 data URI 後才正常。
- **務必保留完整 `<style>` 與 base64 區塊**：只抄卡片 HTML 會完全走版。
- **匯出前等字體**：Google Fonts 未載入完就出圖會退成系統字。命令列腳本已用 `--virtual-time-budget` 處理；瀏覽器匯出前確認頁面已顯示完成（約 2–3 秒）。
- **字數超量**：超過可用高度會被裁切，不是自動縮小。
- **單卡下載鈕**：`.btn-dl`、`.toolbar`、`.card-label`、`[data-noexport]` 不會畫進圖內。

## 檔案

- `assets/template.html` — 主模板：六種卡片類型 + 設定區 + base64 樹葉 + 瀏覽器匯出。
- `assets/leaf-bg.png` — 樹葉素材原始檔（可換）。
- `scripts/export-png.py` — headless Chrome 批次出 1080×1350 PNG，零依賴。
- `scripts/check-orphans.py` — 偵測「一個字一行」，有問題回傳 exit 1。
- `scripts/check-fit.py` — 量每張卡內容高度與上下留白，抓溢出裁切，有問題回傳 exit 1。
- `scripts/embed-leaf.py` — 把樹葉 PNG 內嵌成 base64。
- `scripts/make-leaf-bg.py` — 從棋盤格 JPG 去背產生透明 PNG。
- `examples/` — 示範輸入文章、示範成品 HTML 與六張 PNG。
