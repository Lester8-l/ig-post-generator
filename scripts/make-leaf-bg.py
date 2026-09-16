"""把 JPG 上的棋盤格假透明去掉，做成真正帶 alpha 的 PNG 樹葉素材。"""
from PIL import Image

SRC = r"C:\Users\Jason\.workbuddy\clipboard-images\clipboard-2026-09-16T15-07-33-669Z-c2341be6.jpg"
OUT = r"C:\Users\Jason\WorkBuddy\2026-09-16-22-23-52\ig-post-skill\assets\leaf-bg.png"
PREVIEW = r"C:\Users\Jason\WorkBuddy\2026-09-16-22-23-52\ig-post-skill\_leaf-preview.png"

T0, T1 = 5.0, 16.0  # greenness 低於 T0 視為背景，高於 T1 完全不透明

im = Image.open(SRC).convert("RGB")
w, h = im.size
px = im.load()

out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
op = out.load()

kept = 0
for y in range(h):
    for x in range(w):
        r, g, b = px[x, y]
        green = g - max(r, b)
        if green <= T0:
            continue  # 背景（含白色浮水印）直接透明
        a = 255.0 if green >= T1 else 255.0 * (green - T0) / (T1 - T0)
        op[x, y] = (r, g, b, int(a))
        kept += 1

print(f"原始 {w}x{h}，保留像素 {kept/(w*h)*100:.1f}%")

# 背景不需要 1920 那麼大，縮到 1280 寬再存，省體積
if w > 1280:
    nh = round(h * 1280 / w)
    out = out.resize((1280, nh), Image.LANCZOS)
    print(f"縮放至 1280x{nh}")

out.save(OUT, optimize=True)
import os
print(f"輸出 {OUT}  {os.path.getsize(OUT)/1024:.0f}KB")

# 預覽：疊在奶油色卡底上
bg = Image.new("RGB", out.size, (250, 249, 247))
bg.paste(out, (0, 0), out)
bg.save(PREVIEW)
print("預覽已存", PREVIEW)
