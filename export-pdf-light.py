#!/usr/bin/env python3
"""
export-pdf-light.py — Exporta una versión liviana del portfolio (portfolio-light.pdf).

Usa las copias comprimidas de images-light/ (los originales en images/ no se tocan).
Uso:
    python3 tools/make-light-images.py 110 66   # (re)genera images-light/ — DPI y calidad JPEG (< 2 MB)
    python3 export-pdf-light.py
"""
import importlib.util, re
from pathlib import Path

base = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("export_pdf", base / "export-pdf.py")
ep = importlib.util.module_from_spec(spec); spec.loader.exec_module(ep)

HQ_URL = "https://github.com/misaaaaaa/portfolio-anid-2027/raw/main/portfolio.pdf"
HQ_LINK = (f'<p style="margin-top:0.12in"><a href="{HQ_URL}" class="url" '
           f'style="text-decoration:underline">Versión en alta calidad (PDF) ↗</a></p>')

_orig_embed = ep.embed_images
def embed_light(html, base_dir):
    # ./images/foo.png → ./images-light/foo.jpg
    html = re.sub(r"(\./)?images/([^\"')&]+?)\.(jpe?g|png)", r"./images-light/\2.jpg", html)
    # Portada: enlace a la versión en alta calidad alojada en GitHub
    cover_url = '<p><a href="https://misaa.cc" class="url">https://misaa.cc</a></p>'
    assert cover_url in html, "no se encontró el enlace de la portada"
    html = html.replace(cover_url, cover_url + HQ_LINK, 1)
    return _orig_embed(html, base_dir)
ep.embed_images = embed_light

# Reutiliza main() de export-pdf.py cambiando sólo el nombre de salida
src = Path(base / "export-pdf.py").read_text()
main_src = src[src.index("def main():"):src.index('if __name__')].replace('"portfolio.pdf"', '"portfolio-light.pdf"')
exec(main_src, ep.__dict__)

if __name__ == "__main__":
    import os, shutil, subprocess
    os.chdir(base)
    ep.main()
    # Compactación sin pérdida (object streams + flate nivel 9); no toca las imágenes
    if shutil.which("qpdf"):
        subprocess.run(["qpdf", "--object-streams=generate", "--recompress-flate",
                        "--compression-level=9", "--replace-input", "portfolio-light.pdf"], check=True)
    print(f"✓ portfolio-light.pdf: {os.path.getsize('portfolio-light.pdf')/1e6:.2f} MB")
