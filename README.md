# IG Post Generator · Lester Liang 版

把一篇文章，變成可以發 Instagram 的圖文輪播 —— 用 HTML 排版，一鍵出 1080×1350 PNG。

這是 [Claude Code](https://claude.com/claude-code) / WorkBuddy 的 **Skill**：給它一篇你的文章，它會拆卡、套版、生成 HTML，你在瀏覽器打開就能下載圖片。

> Repo：https://github.com/Lester8-l/ig-post-generator

- **版型骨架** 參考 `cathy.simplebusiness` 的文字卡風格：大字襯線標題、細邊框、藥丸 highlight、圓形數字 badge、四欄概念格。
- **色調字體** 取自 [lesterliang.com](https://www.lesterliang.com/)：森林綠 × 暖金 × 米白，Noto Serif TC ＋ Cormorant Garamond。

## 快速開始

**1. 裝 skill**

```bash
# 直接 clone 到 skills 目錄（推薦）
git clone https://github.com/Lester8-l/ig-post-generator.git ~/.workbuddy/skills/ig-post-generator

# macOS / Linux 舊路徑（Claude Code）
git clone https://github.com/Lester8-l/ig-post-generator.git ~/.claude/skills/ig-post-generator

# 不想用 git 就手動複製資料夾
Copy-Item -Recurse ig-post-generator "$env:USERPROFILE\.workbuddy\skills\ig-post-generator"
```

之後想更新：`cd ~/.workbuddy/skills/ig-post-generator && git pull`

**2. 用**

在對話裡說：

> 幫我把這篇文章做成 IG 貼文圖：（貼上文章）

**3. 出圖**

生成的 HTML 有兩種出圖方式：

| 方式 | 做法 | 適合 |
|---|---|---|
| 瀏覽器 | 打開 HTML → 點「下載此卡」或右上「下載全部」 | 手動微調後匯出 |
| 命令列 | `python scripts/export-png.py deck.html --out out/` | 批次、可重複、交給 agent |

兩者都輸出 1080×1350 PNG，檔名取自每張卡的 `data-filename`（如 `01-hook.png`）。

## 目錄結構

```
ig-post-skill/
├─ SKILL.md              # skill 定義：觸發詞、工作流程、版型規則、色票 token
├─ README.md
├─ assets/
│  ├─ template.html      # 主模板：六種卡片類型 + 設定區 + 內嵌樹葉 + 匯出功能
│  └─ leaf-bg.png        # 樹葉素材（1280×1150 透明 PNG，可換）
├─ scripts/
│  ├─ export-png.py      # headless Chrome 批次出圖（零依賴）
│  ├─ make-draft.py      # 成品 HTML 反推成文字稿
│  ├─ check-orphans.py   # 偵測「一個字一行」＋結構完整性
│  ├─ check-fit.py       # 偵測內容溢出裁切（含垂直置中量測）
│  ├─ embed-leaf.py      # 把樹葉 PNG 內嵌成 base64
│  └─ make-leaf-bg.py    # 從棋盤格 JPG 去背成透明 PNG
└─ examples/
   ├─ demo.html          # 示範成品（Lester「人生選擇設計法」六卡）
   ├─ example-article.md # 示範輸入文章
   └─ *.png              # 六張 1080×1350 成品
```

## 流程：先出文字稿，你改完我才開工

```
你給文章
   ↓
① 我出「文字稿」──────→ 你直接改字（改完丟回來）
   ↓
② 我照你改好的稿生成 HTML → 出圖 → 交付
```

**為什麼要分兩段**：文字改起來快，圖改起來慢。先在文字稿上定稿，比事後改 12 張圖省事。

文字稿長這樣（`｜` = 換行，方括號是元素類型）：

```markdown
## 卡 03-titles · 數字引號清單
- 版型：A11
- [li] 「99% 的人唔知道……」
- [li] 「你一定要……」
- [mini-body] 呢啲就係新時代嘅精神大力丸。
```

改稿時你會看到每行幾個字、這個框一行吃得下幾個字；出現 **⚠被硬斷** 就是太長了。

想把做好的貼文反推成文字稿（要再改一輪時）：

```bash
python scripts/make-draft.py post.html     # → post-文字稿.md
```

## 12 款版型菜單

每次生成從中挑 6–8 款組合，**同款不連續**，所以每篇貼文長得都不一樣。

| 代號 | 版型 | 用途 |
|---|---|---|
| A1 | 大標封面 | 開場。大字鉤子 + 短線 + 副句 + 手繪箭頭 |
| A2 | 手寫開場 + 報名頁 | 服務介紹。手寫提問 → 大字標題 → 藥丸 CTA |
| A3 | 宣言 | 一句核心主張 |
| A4 | 段落 + 藥丸條 | 解釋概念，重點抽成藥丸 |
| A5 | 2×2 編號卡格 | 四個並列的檢查點 + 線稿 icon |
| A6 | 手繪圈選 | 鋪陳後用箭頭 + 圈選點出結論 |
| A7 | 亂線團 + 反問 | 把「心裡一團亂」具象化 |
| A8 | 藥丸橫排 + icon | 一組動作／成本，可搭植物線稿 + 便利貼 |
| A9 | 左藥丸 + 右插畫 | 左列東西、右用插畫說明關係 |
| A10 | 大標 + 場景插畫 | 情緒最強的一張，可開右上 logo |
| A11 | 數字引號清單 | 幾句心聲，編號 + 引號 |
| A12 | 手寫方框 + CTA | 收尾。手寫方框 + 行動呼籲 |

**建議節奏**：開場 A1（或 A10）→ 中間 4–6 張混搭（文字重的卡之間穿插留白多的卡）→ 收尾 A12。樹葉只用封面 + 收尾，裝飾別每張都塞。

## 線稿插畫庫（純 SVG，不用 Emoji）

| 類別 | 內容 |
|---|---|
| 小 icon | 對話泡泡＋人、雙泡泡、手寫筆、放大鏡、書本＋勾、燈泡、筆電＋叉、文件複製、對話泡泡三點、閃爍 |
| 手繪箭頭 | 下箭頭（封面／CTA）、斜箭頭（指向圈選處） |
| 其他線稿 | 亂線團、植物枝葉、三人會議場景、兩人對話插畫 |
| 裝飾 | 有機色塊（`.blob`）、便利貼（`.sticky`，含膠帶、rotate -6°） |

筆觸色吃 `--illo`（預設 gold-soft），改 `:root` 兩行就能整組換色。畫新 icon 的規格：`viewBox="0 0 64 64"`、`fill:none`、`stroke-width:2`、只用線條。

底部帳號不再是硬寫死的字串，改 `IG_CONFIG` 一行即可（見下）。樹葉背景是**選配**，封面 + 收尾各一張最耐看。

## 設定（每次生成只改這裡）

模板 `<body>` 開頭：

```js
window.IG_CONFIG = {
  handle : 'lesterleung_07',   // IG 帳號，不用加 @，換帳號只改這行
  leaves : true                // 樹葉背景總開關：false = 全部卡片都不顯示
};
```

要「只有某幾張卡有樹葉」，在個別 `.card` 加 class：

```html
<div class="card leaves-top"    data-filename="01-hook">   <!-- 樹葉在頂 -->
<div class="card leaves-bottom" data-filename="06-cta">    <!-- 樹葉在底 -->
<div class="card"               data-filename="03-pills">   <!-- 乾淨版 -->
```

## 字體：三層分工

| 角色 | 字體 | 用在哪 |
|---|---|---|
| 標題 | Noto Serif TC 700 | 大標、重點句、CTA |
| 正文 | **LXGW WenKai TC** 霞鶩文楷 | 段落、藥丸條（療癒感主要來源） |
| 手寫點綴 | **Iansui** 芫荽 | note-box、小標 |
| 英文數字 | Cormorant Garamond | 數字 badge、頁尾帳號 |

手寫體只用於點綴——一句話、一個標籤、一個方框。整張卡都用手寫體會顯得隨便、也傷可讀性。

## 拿到 HTML 後想自己微調？

輸出的 HTML 是設計給非工程師改的，有三個入口：

| 入口 | 怎麼用 |
|---|---|
| **✎ 編輯文字**（推薦） | 按鈕按下去，直接點卡片上的字改，所見即所得；改完再按一次關閉 |
| 帳號／關鍵字欄位 | 換 IG 帳號、改金色關鍵字，即時生效 |
| 直接改 HTML | 搜尋 `data-filename` 找到該張卡，改 `.content` 裡的文字，不用動 class |

兩個貼心設計：

- **關鍵字自動上色**：金色強調寫在 `IG_CONFIG.keywords`，匯出前會自動重套一次。
  所以你把句子改掉、甚至整句重寫，金色強調還是會自己補回來，不用手動加標籤。
- **超量警示**：編輯模式下若內容超出卡片，會跳出紅色「⚠ 內容超出，匯出會被裁掉，請減字」。
  卡片是 `overflow:hidden`，超出會被靜默裁掉、畫面上看不出來 —— 有這個警示才不會白做。
  （警示只在網頁上出現，匯出時自動隱藏。）

## 排版：避免「一個字一行」

內容區淨寬 788px，中文一字約 1em，所以每行字數有上限：

| 元素 | 字級 | 建議每行字數 |
|---|---|---|
| Hook 大標 | 88px | ≤ 8 |
| 重點句 | 56px | ≤ 12 |
| CTA／引號清單 | 52px | ≤ 12 |
| 正文、小標 | 48px | ≤ 14 |
| note-box（手寫） | 48px | ≤ 11 |
| 藥丸條 | 44px | ≤ 14 |

手動 `<br>` 斷行是主要手段（`text-wrap:pretty` 對中文幫助有限）。兩支檢查都要跑：

```bash
python scripts/check-orphans.py deck.html   # 一個字一行
python scripts/check-fit.py deck.html       # 內容裝不下被裁切
```

`check-fit.py` 會列出每張卡的內容高度與上下留白。**留白低於 50px 就該減字或降一級字級。**

## 自訂

改 `assets/template.html` 最上方的 `:root` 區塊即可整套換色 —— 所有卡片都吃同一組 token，不會有零散樣式。變數名稱沿用 [lesterliang.com](https://www.lesterliang.com/) 的命名（`--forest`、`--paper`、`--gold`…），要換成自己的色值，改數值就好、不用改名字。

```css
:root{
  --forest:#2E5E4E;      /* 主色：badge、icon */
  --forest-deep:#234839; /* 標題 */
  --gold:#B8893B;        /* 關鍵字、分隔線 */
  --paper:#F4F0E6;       /* 米色面塊 */
  --ink-soft:#6B6256;    /* 正文 */
  --line-warm:#E8DFD0;   /* IG 卡片專用暖色框線 */
}
```

要去別的網站抓色票／字體，用姊妹 skill `html-render-verify` 的 `extract-tokens.py`：

```bash
python extract-tokens.py https://example.com
```

## 換樹葉素材

1. 換掉 `assets/leaf-bg.png`（透明 PNG），或用 `scripts/make-leaf-bg.py` 從帶棋盤格的圖去背
2. `python scripts/embed-leaf.py` 重新內嵌進 template.html
3. 重跑 `check-orphans.py` + `export-png.py` 複驗

> 為什麼要內嵌：用 `file://` 開 HTML 時，html2canvas 會把**本地圖片判定為跨來源、靜默跳過不畫**（不報錯，只是圖憑空消失）。base64 data URI 沒有這個問題。


## 合規

若內容涉及保險／投資，沿用 Lester 的禁止詞庫規則：不寫「保證、穩賺、零風險、像定存」；非保證利益須標示；過往績效同句註明「過往不代表未來」。這條同時寫在 `SKILL.md` 裡，agent 生成時會自查。

## 注意

- 字體與 html2canvas 走 CDN，**首次開啟請聯網**，等字體載入完成（約 2–3 秒）再匯出，否則會退成系統字。
- `scripts/export-png.py` 需要本機有 Chrome 或 Edge；沒有的話用瀏覽器手動匯出。
- 圖片素材一律 base64 內嵌（原因見「換樹葉素材」），所以 template.html 約 195KB 是正常的。
