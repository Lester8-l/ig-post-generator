#!/usr/bin/env python3
"""
檢查每張卡的內容有沒有「裝不下」（被 overflow:hidden 靜默裁切），
以及垂直置中是否平衡。

Usage:
    python check-fit.py deck.html
    python check-fit.py deck.html --height 1350 --pad 56 --vpad 80

原理：
    headless Chrome 開臨時頁，注入 JS 量每張卡 .content 內所有子元素的
    getBoundingClientRect()，算出內容上下留白與實際高度，用 --dump-dom 讀回。

    為什麼不能只看圖？「視覺上偏高／偏低」很容易誤判，實際量測才準。
    另外溢出裁切在畫面上常常看不出來（切掉的可能是最後一行的下緣），
    用數字檢查才可靠。

退出碼：任何一張溢出 → 1；正常 → 0。
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

PROBE = r"""
(function(){
  var CARD_H = __CARD_H__;
  function finish(p){ var e=document.createElement('pre'); e.id='__fit'; e.textContent=JSON.stringify(p); e.style.display='none'; document.body.appendChild(e); }
  function run(){
    var rows=[];
    document.querySelectorAll('.card').forEach(function(c){
      var ct=c.querySelector('.content');
      if(!ct) return;
      var cardBox=c.getBoundingClientRect();
      var kids=[...ct.children].filter(function(k){ return k.offsetParent!==null || k.getClientRects().length; });
      if(!kids.length) return;
      var top=Math.min.apply(null,kids.map(function(k){return k.getBoundingClientRect().top;}));
      var bot=Math.max.apply(null,kids.map(function(k){return k.getBoundingClientRect().bottom;}));
      rows.push({
        f: c.dataset.filename || 'card',
        top: Math.round(top-cardBox.top),
        bot: Math.round(bot-cardBox.top),
        h: Math.round(bot-top),
        overflow: Math.round(bot-(cardBox.top+CARD_H))
      });
    });
    finish(rows);
  }
  if(document.fonts&&document.fonts.ready){ document.fonts.ready.then(function(){setTimeout(run,1200);}); }
  else { setTimeout(run,2500); }
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
    ap.add_argument("--height", type=int, default=1350)
    ap.add_argument("--pad", type=int, default=56, help="卡片外框內縮（.content 的 inset）")
    ap.add_argument("--vpad", type=int, default=80, help=".content 的上下內距")
    ap.add_argument("--chrome", default=None)
    ap.add_argument("--wait", type=int, default=18000)
    args = ap.parse_args()

    src = pathlib.Path(args.html).resolve()
    if not src.exists():
        raise SystemExit(f"檔案不存在：{src}")
    browser = find_browser(args.chrome)

    html = src.read_text(encoding="utf-8")
    base_tag = f'<base href="{src.parent.as_uri()}/">'
    html = html.replace("<head>", "<head>\n" + base_tag, 1) if "<head>" in html else base_tag + html
    probe = PROBE.replace("__CARD_H__", str(args.height))
    html = html.replace("</body>", "<script>" + probe + "</script></body>", 1)

    tmp = src.parent / "_fit_probe.html"
    tmp.write_text(html, encoding="utf-8")
    try:
        r = subprocess.run([
            browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--window-size=1200,2000", f"--virtual-time-budget={args.wait}",
            "--dump-dom", tmp.as_uri(),
        ], capture_output=True, text=True)
        dom = r.stdout or ""
    finally:
        tmp.unlink(missing_ok=True)

    m = re.search(r'<pre id="__fit"[^>]*>(.*?)</pre>', dom, re.S)
    if not m:
        print("⚠ 取不到量測結果（頁面可能沒載入完）")
        sys.exit(2)
    rows = json.loads(html_mod.unescape(m.group(1)))

    usable = args.height - 2 * args.pad - 2 * args.vpad
    print(f"可用內容高度 {usable}px（卡 {args.height} − 外框 {args.pad}×2 − 內距 {args.vpad}×2）\n")
    print(f"{'卡片':<22}{'內容高':>7}{'上留白':>8}{'下留白':>8}{'狀態':>10}")
    print("-" * 58)
    bad = []
    for r in rows:
        top_gap = r["top"] - (args.pad + args.vpad)
        bot_gap = (args.height - args.pad - args.vpad) - r["bot"]
        if r["overflow"] > 0 or top_gap < -2 or bot_gap < -2:
            status = "✗ 溢出"
            bad.append(r["f"])
        elif abs(top_gap - bot_gap) > 40:
            status = "△ 偏"
        else:
            status = "✓"
        print(f"{r['f']:<22}{r['h']:>7}{top_gap:>8}{bot_gap:>8}{status:>10}")
    print()
    if bad:
        print(f"✗ {len(bad)} 張溢出，會被你 overflow:hidden 裁掉：{bad}")
        print("  修法：減字、拆成兩張卡、或把該卡字級降一級。")
        sys.exit(1)
    print("✓ 全部裝得下，沒有裁切。")
    print("提示：上／下留白差距 ≤40px 屬正常（末行 line-height 的視覺補償）。")


if __name__ == "__main__":
    main()
