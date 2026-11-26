#!/usr/bin/env python3
"""Genera copias livianas de las imágenes en images-light/ (los originales no se tocan).
Cada imagen se redimensiona para cubrir su caja en la página a DPI objetivo y se guarda como JPEG."""
import sys, json
from pathlib import Path
from PIL import Image, ImageOps

DPI = float(sys.argv[1]) if len(sys.argv) > 1 else 150
Q = int(sys.argv[2]) if len(sys.argv) > 2 else 80
SCALE = DPI / 96.0  # px CSS -> px reales

# Tamaño máximo (px CSS) en que aparece cada imagen en el PDF (medido con paged.js)
BOXES = json.loads((Path(__file__).parent / "image-boxes.json").read_text())
# object-position vertical distinto de 50% (ver style.css .pos-top)
POS_Y = {"aprox-piscina.jpg": 0.28}

src, dst = Path("images"), Path("images-light")
dst.mkdir(exist_ok=True)
total = 0
for name, (bw, bh) in BOXES.items():
    im = ImageOps.exif_transpose(Image.open(src / name)).convert("RGB")
    # Recorta a la zona visible (object-fit: cover) — no cambia lo que se ve en la página
    W, H = im.size
    box_ar = bw / bh
    if W / H > box_ar:
        cw = round(H * box_ar); x0 = (W - cw) // 2
        im = im.crop((x0, 0, x0 + cw, H))
    else:
        ch = round(W / box_ar); y0 = round((H - ch) * POS_Y.get(name, 0.5))
        im = im.crop((0, y0, W, y0 + ch))
    w, h = im.size
    s = min(1.0, max(bw * SCALE / w, bh * SCALE / h))  # cubrir la caja (object-fit: cover)
    if s < 1.0:
        im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    out = dst / (Path(name).stem + ".jpg")
    im.save(out, "JPEG", quality=Q, optimize=True, progressive=True, subsampling="4:2:0")
    total += out.stat().st_size
    print(f"{name:24} {W}x{H} -> {im.size[0]}x{im.size[1]}  {out.stat().st_size//1024} KB")
print(f"TOTAL {total/1024/1024:.2f} MB  (dpi={DPI}, q={Q})")
