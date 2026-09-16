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
│  ├─ check-orphans.py   # 偵測「一個字一行」
│  ├─ check-fit.py       # 偵測內容溢出裁切（含垂直置中量測）
│  ├─ embed-leaf.py      # 把樹葉 PNG 內嵌成 base64
│  └─ make-leaf-bg.py    # 從棋盤格 JPG 去背成透明 PNG
└─ examples/
   ├─ demo.html          # 示範成品（Lester「人生選擇設計法」六卡）
   ├─ example-article.md # 示範輸入文章
   └─ *.png              # 六張 1080×1350 成品
```

## 六種卡片類型

1. **Hook 封面** — 大字鉤子，關鍵字變金色，配分隔線、箭頭、CTA 句
2. **Statement 宣言** — Kicker ＋ 引導句 ＋ 大字重點塊
3. **段落 ＋ 藥丸條** — 左對齊正文，下方藥丸型重點條（淺綠／米色交替）
4. **數字引號清單** — 圓形數字 badge ＋ 粗體引號句
5. **四欄概念格** — 數字、詞、線條 icon（SVG，不用 Emoji）
6. **Note box ＋ CTA** — 米色手寫感方框收尾，接 DM 行動呼籲

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
