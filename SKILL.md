---
name: ig-post-generator
description: 把一篇文章轉成 Instagram 圖文輪播（HTML 排版 + 一鍵出 1080×1350 PNG）。內建 12 款版型菜單、線稿插畫與裝飾元件，每次可挑不同組合避免長得一樣。當用戶說「幫我出 IG 貼文」「把這篇文章變成 IG 圖」「做一個 IG carousel」「IG post 圖」「輪播圖」時使用。
agent_created: true
---

# IG Post Generator · Lester Liang 版

用 HTML 排版製作 Instagram 貼文圖（1080×1350 直度輪播卡）。色調字體取自 lesterliang.com（森林綠 × 暖金 × 米白）＋ 療癒系字體，插畫一律手繪感線稿 SVG。

## 觸發條件

用戶說「幫我出 IG 貼文」「把這篇文章變成 IG 圖」「做一個 IG carousel」「IG post」等，並提供文章／主題／草稿時使用。只給主題也可以，這時由你先把主題寫成短文再拆卡。

## 工作流程

1. **讀輸入**：完整文章、幾段想法、或只有一個主題。
2. **拆卡 + 選版**（關鍵步驟，見下節）：拆成 6–8 張，每張指定一款版型，**不要連續兩張用同一款**。
3. **生成 HTML**：複製 `assets/template.html` 的完整結構與 CSS（連 `<style>`、base64 素材、SVG 元件一起），只替換每張卡 `.content` 內的文字。
4. **改設定區**：`handle` 一定要改成這次要發的帳號；`leaves` 決定樹葉要不要顯示。
5. **跑檢查**（三支都要跑，幾秒鐘）：
   ```
   python scripts/check-orphans.py <deck.html>          # 一個字一行
   python scripts/check-fit.py <deck.html>              # 內容裝不下被裁切
   python scripts/export-png.py <deck.html> --out out/  # 出圖
   ```
   留白低於 50px 就減字或降字級；有孤字就手動 `<br>` 重排。修好再交付。
6. **交付**：`present_files` 同時給 HTML（可預覽、可微調）與 PNG（可直接發）。
   口頭提醒一句：「想改字就開 HTML 按 ✎ 編輯文字，改太多會跳紅色警示。」

## 版型菜單（12 款，每次挑選組合）

| 代號 | 版型 | 什麼時候用 | 參考圖 |
|---|---|---|---|
| A1 | **大標封面** `.hook-title` | 永遠的第一張。大字鉤子 + 短線 + 副句 + 手繪箭頭 + 行動句 | 圖7 |
| A2 | **手寫開場 + 報名頁** `.open-title` + `.cta-pill` | 服務／活動介紹、報名頁。手寫提問 → 大字標題 → 條列 → 藥丸 CTA（對話 icon + 閃爍） | 圖1 |
| A3 | **宣言** `.statement-*` | 一句核心主張。小標 + 手寫引導 + 大字重點 | — |
| A4 | **段落 + 藥丸條** `.pill` | 解釋一段概念，把重點抽成藥丸條 | — |
| A5 | **2×2 編號卡格** `.grid2x2` | 四個並列的自問／檢查點。編號 → 大字 → 說明 → 右下線稿 icon | 圖2 |
| A6 | **手繪圈選** `.circled` | 先鋪陳，再用粗箭頭 + 圈選 + 手寫字點出結論 | 圖3 |
| A7 | **亂線團 + 反問** `.illo-scribble` | 把「心裡一團亂」具象化，再給轉折句 | 圖4 |
| A8 | **藥丸橫排 + icon** `.pill-row` + `.icon-row` | 列出一組動作／成本，用 icon 具象。可搭植物線稿 + 便利貼 | 圖5 |
| A9 | **左藥丸 + 右插畫** `.split` | 左邊列一組東西，右邊用插畫說明關係 | 圖6 |
| A10 | **大標 + 場景插畫** `.illo-scene` | 情緒張力最強的一張。超大標 + 場景線稿，可開右上 logo | 圖7 |
| A11 | **數字引號清單** `.quote-list` | 幾句心聲，編號 + 引號呈現 | 圖4 |
| A12 | **手寫方框 + CTA** `.note-box` | 最後一張。一句總結 + 手寫方框 + 行動呼籲 | 圖1、圖5 |

### 選版規則

- **開場**：A1（想要更強的情緒時用 A10）。**收尾**：A12。
- **中間 4–6 張**：從 A2–A9、A11 挑，**同款不連續**，8 張內也不要重複超過兩次。
- **節奏**：文字重的卡（A4、A5、A8）之間穿插留白多的卡（A3、A7、A11），閱讀才不會累。
- **裝飾不要每張都塞**：樹葉建議只用封面 + 收尾；植物線稿、便利貼、色塊挑 1–2 張放就好。

## 設定區（每次生成只改這裡）

```js
window.IG_CONFIG = {
  handle   : 'lesterleung_07',   // IG 帳號，不用加 @
  keywords : ['真正的方向', '盤點', '90 天'],   // 金色強調的關鍵字
  leaves   : true,               // 樹葉總開關
  logo     : false               // 右上角 logo（A10 有放）
};
```

**`keywords` 很重要**：它決定哪些字是金色。匯出前會自動重套一次，
所以用戶自己改過文字之後，金色強調還是會補回來（不用手動加 `<em>`）。
每篇挑 3–6 個，用文章裡真實出現的詞，別太泛（「選擇」這種高頻詞會整片金）。

## 交付後用戶要自己微調：生成時要配合的三件事

輸出的 HTML 是設計給非工程師改的。為了讓用戶改得動，**生成時要遵守**：

1. **文字保持純文字**：金色強調交給 `keywords` 自動上色即可，不必手寫 `<em>`
   （要手寫也行，匯出前會被重新套用，不會重複）。
2. **每張卡的文字都在 `.content` 裡**，不要動 class 與結構。用戶改字時只要搜尋
   `data-filename` 找到那張卡，改裡面的字就好。
3. **卡片開頭保留代號註解**（`A5 · 2×2 編號卡格`），用戶才知道自己在改哪一張。

用戶有三個改字入口（模板已內建，交付時提醒他）：

| 入口 | 怎麼用 |
|---|---|
| **✎ 編輯文字**（推薦） | 按鈕按下去，直接點卡片上的字改，所見即所得；改完再按一次關閉 |
| 帳號／關鍵字欄位 | 換帳號、改金色關鍵字，即時生效 |
| 直接改 HTML | 搜尋 `data-filename`，改 `.content` 裡的文字 |

**超量警示**：編輯模式下如果內容超出卡片，會跳出紅色「⚠ 內容超出，匯出會被裁掉，請減字」。
這是因為卡片的 `overflow:hidden` 會靜默裁切，畫面上看不出來。看到警示就是該減字了。
（警示只在網頁上出現，匯出時會自動隱藏，不會畫進圖。）

樹葉是**逐卡選配**，在 `.card` 上加 class：

```html
<div class="card leaves-top">     樹葉在頂（封面用）
<div class="card leaves-bottom">  樹葉鏡像到底（收尾用）
<div class="card">                乾淨版
```

## 線稿插畫（純 SVG，禁止 Emoji）

全部用 stroke 線條，筆觸色吃 `--illo`（預設 `--gold-soft`），要整組換色改 `:root` 兩行就好。

| 類別 | class | 現有圖形 |
|---|---|---|
| 小 icon | `.illo-icon` | 對話泡泡＋人、雙泡泡、手寫筆、放大鏡、書本＋勾、燈泡、筆電＋叉、文件複製、對話泡泡三點、閃爍 |
| 手繪箭頭 | `.illo-arrow` / `.illo-bold` | 下箭頭（封面、CTA）、斜箭頭（指向圈選處） |
| 亂線團 | `.illo-scribble` | 糾結線團 |
| 植物線稿 | `.illo-botanical` | 枝葉 sprig（放左下角） |
| 場景插畫 | `.illo-scene` | 三人會議（桌 + 筆電 + 站立比劃） |
| 人物插畫 | `.illo-split` | 兩人對話 + 對話框 |
| 裝飾形狀 | `.blob` / `.blob-outline` | 有機色塊（不規則圓角） |
| 便利貼 | `.sticky` | 米色紙 + 膠帶，rotate(-6deg)，手寫字 |

**畫新 icon 的規格**：`viewBox="0 0 64 64"`、`fill:none`、`stroke-width:2`、`stroke-linecap:round`、只用線條（不要填色塊；閃爍星可填 `--gold`）。場景插畫用寬視野（如 `0 0 360 150`），人物**頭與肩要留 4–6px 空隙**，否則頭會疊在肩膀上。

## 字體：三層分工

| 角色 | 字體 | 用在哪 | 變數 |
|---|---|---|---|
| 標題（硬） | Noto Serif TC 700 | 大標、重點句、引號清單、CTA | `--font-title` |
| 正文（柔） | **LXGW WenKai TC** 霞鶩文楷 | 段落、藥丸條、卡片格說明 | `--font-soft` |
| 手寫（點綴） | **Iansui** 芫荽 | note-box、kicker、hand-line、圈選文字、便利貼 | `--font-hand` |
| 英文數字 | Cormorant Garamond | 數字 badge、頁尾帳號 | `--font-en` |

手寫體只用於點綴——一句話、一個標籤、一個方框。整張都用手寫體會顯得隨便、也傷可讀性。

## 排版：避免「一個字一行」與「內容被裁切」

內容區淨寬 = 1080 − 2×56 − 2×90 = **788px**，中文一字約 1em：

| 元素 | 字級 | 淨文字寬 | 建議每行字數 |
|---|---|---|---|
| Hook 大標 | 88px | 788 | **≤ 8** |
| 重點句 statement-body | 56px | 788 | ≤ 12 |
| CTA／引號清單 | 52px | 788／696※ | ≤ 12 |
| 正文、小標 | 48px | 788 | ≤ 14 |
| note-box（字距 .08em） | 48px | 656 | ≤ 11 |
| 藥丸條 pill | 44px | 708 | ≤ 14 |
| 卡片格說明 cell-desc | 33px | 300 | ≤ 9（要手動 `<br>`） |

※ 引號清單每項有 64px 數字 badge + 36px 間距，可用文字寬只有 696px。

可用高度 1078px（1350 − 外框 56×2 − 內距 80×2）。手動 `<br>` 是主要斷行手段，`text-wrap:pretty` 只是保險。

## 色票 tokens（來源 lesterliang.com，勿改色值）

```
--warm-white #FFFDF8  --cream #FAF9F7   --paper #F4F0E6   --gray #EBE8E0
--forest #2E5E4E      --forest-deep #234839  --forest-soft #3D6B58  --forest-tint #E7EFEB
--gold #B8893B        --gold-soft #C9A464    --ink-soft #6B6256     --sage #A8BFB2
--charcoal #14201B    --on-forest #F7F5F0    --line rgba(20,32,27,.10)
--line-warm #E8DFD0（IG 卡片專用暖色框線，網站無此 token）
--illo / --illo-strong（插畫筆觸色，對應 gold-soft / gold）
```

網站另有 dark theme（`--cream:#1A1E1C`、`--forest:#7FB39E`、`--gold:#D4A869`）與圓角規範（`--radius-card:18px`、`--radius-pill:999px`）。要確認最新色值：

```bash
python ~/.workbuddy/skills/html-render-verify/scripts/extract-tokens.py https://www.lesterliang.com/
```

## 樹葉素材

`assets/leaf-bg.png`（1280×1150、透明、134KB）由 `scripts/make-leaf-bg.py` 去背而來（同時清掉右下浮水印），**base64 內嵌在 template.html 的 `--leaf-img`**。

換圖：換掉 PNG → `python scripts/embed-leaf.py` 重新內嵌 → 重跑三支檢查。

## 合規（保險／金融內容適用）

涉及保險或投資時：禁止「保證、穩賺、零風險、像定存」等詞；非保證利益必須標示；過往績效同句標註「過往不代表未來」。

## 常見坑

- **html2canvas 會靜默跳過本地圖片！** `file://` 下本地 `<img>`／CSS 背景圖被視為跨來源，直接不畫、不報錯。**素材一律 base64 內嵌**。判斷法：比對「headless 直接截圖」與「html2canvas 匯出」的檔案大小（377KB vs 143KB 就是圖沒進去）。
- **html2canvas 不支援 `background-clip:text`**：漸層文字會畫成色塊或消失 → **不要用漸層文字**，改用 `<em>` 單色強調。
- **務必保留完整 `<style>` 與 base64 區塊**：只抄卡片 HTML 會完全走版。
- **匯出前等字體**：Google Fonts 未載入完就出圖會退成系統字。命令列已用 `--virtual-time-budget`；瀏覽器匯出前確認畫面已顯示完成。
- **字數超量**：超過可用高度會被 `overflow:hidden` 靜默裁切，不是自動縮小。
- **檢查工具會跳過旋轉元素**：`.sticky` 這類 `transform` 過的區塊，逐字分行不適用（已自動跳過並回報數量），不受孤字規則約束。

## 檔案

- `assets/template.html` — 主模板：12 款版型 + 設定區 + base64 樹葉 + 全部 SVG 元件 + 瀏覽器匯出。
- `assets/leaf-bg.png` — 樹葉素材原始檔（可換）。
- `scripts/export-png.py` — headless Chrome 批次出 1080×1350 PNG，零依賴。
- `scripts/check-orphans.py` — 偵測「一個字一行」（會跳過旋轉元素），有問題 exit 1。
- `scripts/check-fit.py` — 量每張卡內容高度與上下留白，抓溢出裁切，有問題 exit 1。
- `scripts/embed-leaf.py` — 把樹葉 PNG 內嵌成 base64。
- `scripts/make-leaf-bg.py` — 從棋盤格 JPG 去背產生透明 PNG。
- `examples/` — 示範成品 HTML（12 款版型總覽）+ 12 張 PNG + 範例文章。
