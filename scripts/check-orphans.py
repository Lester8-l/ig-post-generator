#!/usr/bin/env python3
"""
檢查中文排版有沒有「一個字一行」（孤字）的情況。

Usage:
    python check-orphans.py deck.html
    python check-orphans.py deck.html --min-chars 2

原理：
    用 headless Chrome 開一個臨時頁，注入 JS 逐「字」量測 rect，
    依 y 座標把字分組成行；某一行只有 1 個字（且整段不只一行）就標記為孤字。
    JS 把結果寫進 DOM，再用 --dump-dom 讀回來解析。

退出碼：發現孤字 → 1；乾淨 → 0；量測失敗 → 2。可直接放進生成流程當檢查步驟。

為什麼不能只靠 CSS：
    `text-wrap: pretty` 對 CJK 的幫助有限，真正可靠的是控制每行字數 + 手動 <br>。
    這支腳本就是拿來驗證你有沒有做到（見 SKILL.md 的每行字數預算表）。
"""
import argparse
import html as html_mod
import json
import pathlib
import re
import shutil
import subprocess
import sys

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]

# 不計入字數的標點（只含標點的行不算孤字）
PUNCT = "。，、；：！？）」』】》…‧·,.!?;:)]}"

PROBE_TEMPLATE = r"""
(function(){
  var PUNCT_RE = new RegExp(__PUNCT_CLASS__, 'g');
  var MIN = __MIN__;
  function finish(payload){
    var pre = document.createElement('pre');
    pre.id = '__probe_report';
    pre.textContent = JSON.stringify(payload);
    pre.style.display = 'none';
    document.body.appendChild(pre);
    document.title = 'PROBE_DONE';
  }
  // 有旋轉／縮放的元素：每個字的 y 座標都不同，逐字分行的邏輯會誤判，直接跳過
  function isTransformed(el, stopAt){
    var n = el;
    while (n && n !== stopAt) {
      var tf = getComputedStyle(n).transform;
      if (tf && tf !== 'none') {
        var m = tf.match(/matrix\(([^)]+)\)/);
        if (m) {
          var v = m[1].split(',').map(parseFloat);
          // matrix(a,b,c,d,e,f)：a=1,b=0,c=0,d=1 才是無旋轉／縮放
          if (Math.abs(v[0] - 1) > 0.001 || Math.abs(v[1]) > 0.001 ||
              Math.abs(v[2]) > 0.001 || Math.abs(v[3] - 1) > 0.001) return true;
        } else {
          return true;  // matrix3d 或其他形式，保守跳過
        }
      }
      n = n.parentElement;
    }
    return false;
  }

  function run(){
    var report = [], skipped = 0;
    document.querySelectorAll('.card').forEach(function(card){
      var name = card.dataset.filename || 'card';
      var walker = document.createTreeWalker(card, NodeFilter.SHOW_TEXT);
      var node;
      while ((node = walker.nextNode())) {
        var t = node.textContent;
        if (!t || !t.trim()) continue;
        var el = node.parentElement;
        if (!el || el.closest('[data-noexport]')) continue;
        if (el.hasAttribute('data-orphan-skip')) { skipped++; continue; }
        var cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden') continue;
        if (isTransformed(el, card)) { skipped++; continue; }

        var keys = [], lines = {};
        for (var i = 0; i < t.length; i++) {
          if (!t[i].trim()) continue;
          var r = document.createRange();
          r.setStart(node, i); r.setEnd(node, i + 1);
          var rect = r.getBoundingClientRect();
          if (!rect.height) continue;
          var key = Math.round(rect.top / 4) * 4;
          if (!lines[key]) { lines[key] = { top: rect.top, chars: [] }; keys.push(key); }
          lines[key].chars.push(t[i]);
        }
        if (keys.length < 2) continue;
        keys.sort(function(a, b){ return lines[a].top - lines[b].top; });
        var rendered = keys.map(function(k){ return lines[k].chars.join(''); });
        var bad = [];
        rendered.forEach(function(line, idx){
          var core = line.replace(PUNCT_RE, '');
          if (core.length < MIN) bad.push({ line: idx + 1, text: line, count: core.length });
        });
        if (bad.length) {
          report.push({
            card: name,
            element: (el.className || el.tagName).toString(),
            text: t.trim().slice(0, 40),
            lines: rendered,
            bad: bad
          });
        }
      }
    });
    // 結構完整性：關鍵字上色（Range + extractContents）若位置算錯，
    // 會把整個子樹複製進 <em>（例如 <em><span class="pill">字</span></em> + 空 span）。
    // 這種破損畫面上幾乎看不出來，但會讓藥丸變窄、文字換行錯亂。
    var struct = { badWrap: [], empty: [] };
    document.querySelectorAll('.card .content em').forEach(function(em){
      var bad = em.querySelector(':scope > span, :scope > div, :scope > p, :scope > img, :scope > svg');
      if (bad) struct.badWrap.push((bad.className || bad.tagName) + ' ← ' + em.textContent.slice(0, 12));
    });
    // 只檢查「本來就該有文字」的類別，避免裝飾元素（.divider 等）誤判
    var NEEDS_TEXT = '.pill,.pill-sm,.para,.mini-body,.hook-title,.hook-sub,.hook-cta,'
                   + '.statement-kicker,.statement-lead,.statement-body,.quote-list li,'
                   + '.note-box,.cell-word,.cell-desc,.list-intro,.kicker,.hand-line,'
                   + '.open-title,.big-2line,.circled-text,.sticky span,.handle';
    document.querySelectorAll('.card .content ' + NEEDS_TEXT).forEach(function(el){
      if (el.querySelector('img, svg')) return;
      if (!el.textContent.trim()) struct.empty.push(el.className || el.tagName);
    });
    finish({ report: report, skipped: skipped, struct: struct });
  }
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(function(){ setTimeout(run, 1200); });
  } else {
    setTimeout(run, 2500);
  }
})();
"""


def find_browser(explicit=None):
    if explicit:
        return explicit
    for p in CHROME_CANDIDATES:
        if pathlib.Path(p).exists():
            return p
    for name in ("chrome", "google-chrome", "chromium", "msedge"):
        f = shutil.which(name)
        if f:
            return f
    home = pathlib.Path.home() / ".agent-browser" / "browsers"
    if home.exists():
        for exe in home.glob("chrome-*/chrome.exe"):
            return str(exe)
    raise SystemExit("找不到 Chrome / Edge，請用 --chrome <path> 指定。")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--min-chars", type=int, default=2,
                    help="一行少於幾個字就算孤字（預設 2，即只剩 1 個字）")
    ap.add_argument("--chrome", default=None)
    ap.add_argument("--wait", type=int, default=20000)
    args = ap.parse_args()

    src = pathlib.Path(args.html).resolve()
    if not src.exists():
        raise SystemExit(f"檔案不存在：{src}")
    browser = find_browser(args.chrome)

    html = src.read_text(encoding="utf-8")
    base_tag = f'<base href="{src.parent.as_uri()}/">'
    html = html.replace("<head>", "<head>\n" + base_tag, 1) if "<head>" in html else base_tag + html

    cls = "[" + "".join("\\" + c if c in "[]^\\-" else c for c in PUNCT) + "]"
    probe = (PROBE_TEMPLATE
             .replace("__PUNCT_CLASS__", json.dumps(cls))
             .replace("__MIN__", str(args.min_chars)))
    html = html.replace("</body>", "<script>" + probe + "</script></body>", 1)

    tmp = src.parent / "_orphan_probe.html"
    tmp.write_text(html, encoding="utf-8")
    try:
        cmd = [
            browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--window-size=1200,2000",
            f"--virtual-time-budget={args.wait}",
            "--dump-dom", tmp.as_uri(),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        dom = r.stdout or ""
    finally:
        tmp.unlink(missing_ok=True)

    m = re.search(r'<pre id="__probe_report"[^>]*>(.*?)</pre>', dom, re.S)
    if not m:
        print("⚠ 取不到偵測結果（頁面可能沒載入完）。輸出前 300 字：")
        print(dom[:300])
        sys.exit(2)

    raw = html_mod.unescape(m.group(1)).strip()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        print("⚠ 無法解析偵測結果：", raw[:200])
        sys.exit(2)
    report = payload.get("report", [])
    skipped = payload.get("skipped", 0)
    struct = payload.get("struct", {"badWrap": [], "empty": []})
    if skipped:
        print(f"（已跳過 {skipped} 個旋轉／標記元素，逐字分行對它們不適用）")

    if struct["badWrap"] or struct["empty"]:
        print("✗ 關鍵字上色破壞了 DOM 結構（畫面上不易察覺，但會讓排版走樣）：")
        for b in struct["badWrap"][:8]:
            print(f"    <em> 直接包住了元素：{b}")
        for e in struct["empty"][:8]:
            print(f"    空元素殘留（被掏空）：{e}")
        print("    成因通常是索引落點算錯、Range 跨出元素邊界。")
        sys.exit(1)

    if not report:
        print(f"✓ 沒有孤字。所有多行文字區塊每行都 ≥ {args.min_chars} 個字。")
        return

    print(f"✗ 發現 {len(report)} 處孤字（一行少於 {args.min_chars} 個字）：\n")
    for item in report:
        print(f"  卡片 {item['card']}  ·  {item['element']}")
        print(f"    原文：{item['text']}…")
        for b in item["bad"]:
            print(f"    → 第 {b['line']} 行只有 {b['count']} 個字：「{b['text']}」")
        print("    實際斷行：", " / ".join(item["lines"]))
        print()
    print("修法：手動 <br> 斷行、把該行字數減到容器放得下、或縮小字級（見 SKILL.md 每行字數預算表）。")
    sys.exit(1)


if __name__ == "__main__":
    main()
