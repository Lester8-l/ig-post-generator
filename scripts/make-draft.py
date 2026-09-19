#!/usr/bin/env python3
"""
把貼文 HTML 反推成「文字稿」，方便使用者逐版改字。
也是「先出文字稿 → 使用者改完 → 才生成 HTML」流程的產出格式。

Usage:
    python make-draft.py post.html                 # 輸出 post-文字稿.md
    python make-draft.py post.html --out draft.md
    python make-draft.py post.html --stdout

格式：
    ## 卡 03-titles · 數字引號清單
    - [li·52px] 1「99% 的人唔知道……」　（14 字，此框約 13 字/行）　⚠被硬斷（實際 2 行，標了 1 段）

    ｜ = 換行
    ⚠被硬斷 = 這行太長，瀏覽器自己折行了（實際行數 > 你標的段數）

為什麼用「實際渲染行數」而不是字數公式：
    flex 置中元素的寬度是依內容收縮的，用 clientWidth 推算字數上限會失準。
    直接量每個字的 rect、按 y 分組得到真實行數，才是可靠的判斷。
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
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
]

TEXT_SELECTOR = ",".join([
    ".kicker", ".hand-line", ".open-title", ".hook-title", ".hook-sub", ".hook-cta",
    ".statement-kicker", ".statement-lead", ".statement-body", ".para", ".mini-body",
    ".list-intro", ".big-2line", ".note-box", ".pill", ".pill-sm",
    ".quote-list li", ".cell-word", ".cell-desc", ".circled-text", ".sticky span",
])

LAYOUT_HINT = {
    "cover": "封面＋插畫", "hook": "大標封面", "statement": "宣言",
    "pills": "段落＋藥丸條", "grid2x2": "2×2 編號卡格", "annotate": "手繪圈選",
    "scribble": "亂線團＋反問", "pillrow": "藥丸橫排＋icon", "split": "左藥丸＋右插畫",
    "heroillo": "大標＋場景插畫", "numbered": "數字引號清單", "cta": "手寫方框＋CTA",
}

PROBE = r"""
(function(){
  var SEL = __SEL__;
  function cap(el){
    var cs = getComputedStyle(el);
    var fs = parseFloat(cs.fontSize) || 16;
    var ls = cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing) || 0;
    var w = el.clientWidth - (parseFloat(cs.paddingLeft) || 0) - (parseFloat(cs.paddingRight) || 0);
    if (w <= 0) w = el.clientWidth;
    return Math.max(1, Math.floor(w / (fs + ls)));
  }
  function renderedLines(el){
    var tf = getComputedStyle(el).transform;
    if (tf && tf !== 'none') {
      var mm = tf.match(/matrix\(([^)]+)\)/);
      if (!mm) return null;
      var v = mm[1].split(',').map(parseFloat);
      if (Math.abs(v[0]-1) > 0.001 || Math.abs(v[1]) > 0.001 ||
          Math.abs(v[2]) > 0.001 || Math.abs(v[3]-1) > 0.001) return null;
    }
    var w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT), tops = {}, node;
    while ((node = w.nextNode())) {
      // 數字 badge（.num）不是正文，排除，否則會被算成另一行
      if (node.parentElement && node.parentElement.closest && node.parentElement.closest('.num')) continue;
      for (var i = 0; i < node.nodeValue.length; i++) {
        if (!node.nodeValue[i].trim()) continue;
        var rg = document.createRange();
        rg.setStart(node, i); rg.setEnd(node, i + 1);
        var b = rg.getBoundingClientRect();
        if (!b.height) continue;
        tops[Math.round(b.top / 4) * 4] = 1;
      }
    }
    return Object.keys(tops).length || 1;
  }
  function run(){
    var out = [];
    document.querySelectorAll('.card').forEach(function(card){
      var items = [];
      card.querySelectorAll(SEL).forEach(function(el){
        var clone = el.cloneNode(true);
        clone.querySelectorAll('.num').forEach(function(n){ n.remove(); });
        var h = clone.innerHTML.replace(/<br\s*\/?>/gi, '｜');
        var tmp = document.createElement('div'); tmp.innerHTML = h;
        var text = (tmp.textContent || '').replace(/\s+/g, ' ').trim();
        if (!text) return;
        items.push({
          cls: el.className.split(' ')[0] || el.tagName.toLowerCase(),
          text: text,
          segs: text.split('｜').length,
          lines: renderedLines(el),
          cap: cap(el),
          fs: Math.round(parseFloat(getComputedStyle(el).fontSize))
        });
      });
      var lv = card.className.match(/leaves-(top|bottom)/);
      out.push({ file: card.dataset.filename, leaves: lv ? lv[1] : null, items: items });
    });
    var p = document.createElement('pre'); p.id = '__draft'; p.style.display = 'none';
    p.textContent = JSON.stringify(out);
    document.body.appendChild(p);
    document.title = 'DRAFT_OK';
  }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function(){ setTimeout(run, 1000); });
  else setTimeout(run, 2000);
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
    ap.add_argument("--out", default=None)
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--chrome", default=None)
    args = ap.parse_args()

    src = pathlib.Path(args.html).resolve()
    if not src.exists():
        raise SystemExit("檔案不存在：" + str(src))
    browser = find_browser(args.chrome)
    source = src.read_text(encoding="utf-8")

    html = source
    base = '<base href="' + src.parent.as_uri() + '/">'
    html = html.replace("<head>", "<head>\n" + base, 1) if "<head>" in html else base + html
    probe = PROBE.replace("__SEL__", json.dumps(TEXT_SELECTOR))
    html = html.replace("</body>", "<script>" + probe + "</script></body>", 1)

    tmp = src.parent / "_draft_probe.html"
    tmp.write_text(html, encoding="utf-8")
    try:
        r = subprocess.run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                            "--window-size=1200,2000", "--virtual-time-budget=18000",
                            "--dump-dom", tmp.as_uri()], capture_output=True, text=True)
        dom = r.stdout or ""
    finally:
        tmp.unlink(missing_ok=True)

    m = re.search(r'<pre id="__draft"[^>]*>(.*?)</pre>', dom, re.S)
    if not m:
        print("⚠ 取不到文字稿（頁面可能沒載入完）")
        sys.exit(2)
    cards = json.loads(html_mod.unescape(m.group(1)))

    handle = re.search(r"handle\s*:\s*'([^']*)'", source)
    kw = re.search(r"keywords\s*:\s*\[([^\]]*)\]", source)
    title = re.search(r"<title>(.*?)</title>", source, re.S)

    L = []
    L.append("# 貼文文字稿")
    L.append("")
    L.append("> **怎麼改**：直接改下面的文字，改完把整份丟回給我，我就用它生成正式 HTML。")
    L.append("> `｜` = 換行（要換行就在那裡加一個 ｜，要接回去就刪掉它）")
    L.append("> `（12 字，此框約 14 字/行）` = 這行幾個字 + 這個框一行大約吃得下幾個字")
    L.append("> **⚠被硬斷** = 這行太長、瀏覽器自己折行了 → 減字，或自己加 ｜ 控制斷點")
    L.append("> 想換版型：改下面的「版型」那行（菜單 A1–A12 見 SKILL.md）")
    L.append("")
    L.append("## 基本設定")
    if handle:
        L.append("- 帳號：" + handle.group(1))
    if kw:
        L.append("- 金色關鍵字：" + kw.group(1).strip())
    leaves_on = [c["file"] for c in cards if c["leaves"]]
    L.append("- 樹葉：" + ("、".join(leaves_on) if leaves_on else "無"))
    L.append("")
    L.append("---")
    L.append("")

    for c in cards:
        hint = ""
        for k in LAYOUT_HINT:
            if k in c["file"]:
                hint = LAYOUT_HINT[k]
                break
        head = "## 卡 " + c["file"] + (" · " + hint if hint else "")
        if c["leaves"]:
            head += "　🌿樹葉在" + ("頂" if c["leaves"] == "top" else "底")
        L.append(head)
        for it in c["items"]:
            segs = it["text"].split("｜")
            counts = "+".join(str(len(s.strip())) for s in segs)
            note = counts + " 字"
            if len(segs) == 1:
                note += "，此框約 " + str(it["cap"]) + " 字/行"
            flag = ""
            if it.get("lines") is not None and it["lines"] > it["segs"]:
                flag = "　⚠被硬斷（實際 " + str(it["lines"]) + " 行，你標了 " + str(it["segs"]) + " 段）"
            L.append("- [" + it["cls"] + "·" + str(it["fs"]) + "px] " + it["text"] + "　（" + note + "）" + flag)
        L.append("")

    out = "\n".join(L)
    if args.stdout:
        print(out)
        return
    dst = pathlib.Path(args.out) if args.out else src.parent / (src.stem + "-文字稿.md")
    dst.write_text(out, encoding="utf-8")
    print("文字稿已輸出：" + str(dst))
    print("共 " + str(len(cards)) + " 張卡")


if __name__ == "__main__":
    main()
