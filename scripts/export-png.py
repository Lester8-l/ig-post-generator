#!/usr/bin/env python3
"""
Batch export IG cards from a generated HTML deck to 1080x1350 PNGs.

Usage:
    python export-png.py <deck.html> [--out <dir>] [--chrome <chrome.exe>]

How it works:
    The deck HTML contains several <div class="card" data-filename="01-hook"> blocks.
    This script writes a temporary single-card page for each block (hiding the rest
    via CSS) and screenshots it with headless Chrome at 1080x1350 — the exact IG
    portrait size. Output PNGs are named after data-filename.

    Why not just use html2canvas in the browser?
    Both work. html2canvas needs a manual click and a network round-trip for the CDN;
    this script is for agents / CI, producing files directly on disk.

Requirements:
    Headless Chrome or Edge. Auto-detected in common locations; override with --chrome.
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys

CARD_RE = re.compile(r'data-filename="([^"]+)"')

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]


def find_browser(explicit=None):
    if explicit:
        return explicit
    for p in CHROME_CANDIDATES:
        if pathlib.Path(p).exists():
            return p
    for name in ("chrome", "google-chrome", "chromium", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    # agent-browser ships its own Chromium
    home = pathlib.Path.home() / ".agent-browser" / "browsers"
    if home.exists():
        for exe in home.glob("chrome-*/chrome.exe"):
            return str(exe)
    raise SystemExit("找不到 Chrome / Edge，請用 --chrome <path> 指定。")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--out", default=None, help="輸出目錄（預設為 deck 同層的 out/）")
    ap.add_argument("--chrome", default=None)
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1350)
    args = ap.parse_args()

    deck_path = pathlib.Path(args.deck).resolve()
    if not deck_path.exists():
        raise SystemExit(f"檔案不存在：{deck_path}")
    out_dir = pathlib.Path(args.out).resolve() if args.out else deck_path.parent / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = out_dir / "_tmp_pages"
    tmp_dir.mkdir(exist_ok=True)

    browser = find_browser(args.chrome)
    html = deck_path.read_text(encoding="utf-8")
    names = CARD_RE.findall(html)
    if not names:
        raise SystemExit("找不到任何 data-filename 卡片，請確認 deck HTML 結構。")

    # 臨時頁會換位置，用 <base> 把相對路徑（例如 leaf-bg.png）釘回原目錄
    base_tag = f'<base href="{deck_path.parent.as_uri()}/">'
    if "<head>" in html:
        html = html.replace("<head>", "<head>\n" + base_tag, 1)
    else:
        html = base_tag + html

    print(f"browser : {browser}")
    print(f"cards   : {len(names)} -> {names}")

    failures = []
    for i, name in enumerate(names, start=1):
        extra = f"""<style>
  body{{padding:0 !important;background:#FFFDF8 !important;}}
  .toolbar,.controls,.btn-dl,.btn-edit,.card-label,.ovf,[data-noexport]{{display:none !important;}}
  .deck{{gap:0 !important;max-width:none !important;margin:0 !important;}}
  .card-wrap:not(:nth-child({i})){{display:none !important;}}
  .card-wrap{{gap:0 !important;}}
</style>
</head>"""
        page = tmp_dir / f"{i:02d}.html"
        page.write_text(html.replace("</head>", extra, 1), encoding="utf-8")
        png = out_dir / f"{name}.png"
        cmd = [
            browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=1",
            f"--window-size={args.width},{args.height}",
            "--virtual-time-budget=10000",
            f"--screenshot={png}", page.as_uri(),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        ok = png.exists() and png.stat().st_size > 2000
        size_kb = png.stat().st_size // 1024 if png.exists() else 0
        print(f"  {'OK  ' if ok else 'FAIL'} {name}.png  {size_kb}KB")
        if not ok:
            failures.append(name)
            if r.stderr:
                print("       ", r.stderr.strip()[-200:])

    shutil.rmtree(tmp_dir, ignore_errors=True)
    print(f"\n完成：{len(names) - len(failures)}/{len(names)} 張 -> {out_dir}")
    if failures:
        print("失敗：", failures)
        sys.exit(1)


if __name__ == "__main__":
    main()
