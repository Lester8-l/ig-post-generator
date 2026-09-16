#!/usr/bin/env python3
"""
把 assets/leaf-bg.png 內嵌成 base64 data URI 寫進 template.html。

Usage:
    python embed-leaf.py                 # 用預設路徑
    python embed-leaf.py --png assets/leaf-bg.png --html assets/template.html

為什麼要內嵌：
    本機用 file:// 直接開啟 HTML 時，html2canvas 會把「本地圖片」判定為跨來源、
    靜默跳過不畫（不會報錯，只是圖不見了）。改成 data URI 就沒有來源問題，
    單檔 HTML 雙擊即可匯出完整成品。

換樹葉圖的流程：
    1. 換掉 assets/leaf-bg.png（用 make-leaf-bg.py 從照片去背，或自己準備透明 PNG）
    2. 執行這支腳本重新內嵌
    3. 跑 check-orphans.py / export-png.py 複驗
"""
import argparse
import base64
import pathlib
import re
import sys

BEGIN = "/* ==== LEAF-IMG:BEGIN（由 scripts/embed-leaf.py 產生，勿手改） ==== */"
END = "/* ==== LEAF-IMG:END ==== */"


def main():
    here = pathlib.Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", default=str(here / "assets" / "leaf-bg.png"))
    ap.add_argument("--html", default=str(here / "assets" / "template.html"))
    args = ap.parse_args()

    png = pathlib.Path(args.png)
    html_path = pathlib.Path(args.html)
    if not png.exists():
        sys.exit(f"找不到圖片：{png}")
    if not html_path.exists():
        sys.exit(f"找不到 HTML：{html_path}")

    b64 = base64.b64encode(png.read_bytes()).decode("ascii")
    block = f"""{BEGIN}
:root{{ --leaf-img:url("data:image/png;base64,{b64}"); }}
{END}"""

    html = html_path.read_text(encoding="utf-8")
    if BEGIN in html:
        html = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), block, html, flags=re.S)
    else:
        # 插在 </style> 之前，讓它排在最後、可覆蓋前面的宣告
        html = html.replace("</style>", block + "\n</style>", 1)

    html_path.write_text(html, encoding="utf-8")
    before = len(html) - len(block)
    print(f"已內嵌 {png.name}  {len(base64.b64decode(b64))/1024:.0f}KB → base64 {len(b64)/1024:.0f}KB")
    print(f"{html_path}  大小 {len(html)/1024:.0f}KB（原本 {before/1024:.0f}KB）")
    print("提醒：.leaves 的 background-image 要吃 var(--leaf-img) 才會用到內嵌圖。")


if __name__ == "__main__":
    main()
