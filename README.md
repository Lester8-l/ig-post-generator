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
│  └─ template.html      # 主模板：六種卡片類型 + 內建匯出功能
├─ scripts/
│  └─ export-png.py      # headless Chrome 批次出圖（零依賴）
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

底部 `@lesterliang` 帳號字串在每張卡的 `.handle`，全域替換即可。

## 合規

若內容涉及保險／投資，沿用 Lester 的禁止詞庫規則：不寫「保證、穩賺、零風險、像定存」；非保證利益須標示；過往績效同句註明「過往不代表未來」。這條同時寫在 `SKILL.md` 裡，agent 生成時會自查。

## 注意

- 字體與 html2canvas 走 CDN，**首次開啟請聯網**，等字體載入完成（約 2–3 秒）再匯出，否則會退成系統襯線字。
- `scripts/export-png.py` 需要本機有 Chrome 或 Edge；沒有的話用瀏覽器手動匯出。
