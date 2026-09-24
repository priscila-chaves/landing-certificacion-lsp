#!/usr/bin/env python3
"""Build de la landing para Netlify.
Genera index.html (Costa Rica, raíz) y nicaragua/index.html (Nicaragua) desde
los archivos de Claude Design y adapta el runtime.
Los archivos fuente del repo quedan intactos (esto corre solo en el build).

Las dos páginas comparten assets/, vendor/, support.js, image-slot.js y el
estado de encuadres (image-slots.state.json) publicados en la RAÍZ del sitio,
por eso ambas páginas usan rutas absolutas (con "/" al inicio) para esos
recursos: una ruta relativa en nicaragua/index.html resolvería contra
/nicaragua/... y rompería las imágenes/scripts."""
import re, shutil, os, sys

SRC_CR = "Landing Certificacion LSP.dc.html"
SRC_NI = "Landing Certificacion LSP Nicaragua.dc.html"


def build_page(src, out_path, canonical, title, description, og_image):
    # Se lee el .dc.html fuente y SOLO se transforma la copia en memoria que
    # se escribe en out_path — el archivo fuente en el repo nunca se toca.
    html = open(src, encoding="utf-8").read()

    # Rutas absolutas para support.js/image-slot.js/assets: ambas páginas los
    # publican desde la raíz del sitio, así que "/ruta" funciona igual para
    # index.html como para nicaragua/index.html. (No-op si la fuente ya usa
    # rutas absolutas, como el archivo de Nicaragua.)
    html = html.replace('<script src="./support.js"></script>', '<script src="/support.js"></script>', 1)
    html = html.replace('<script src="./image-slot.js"></script>', '<script src="/image-slot.js"></script>', 1)
    html = re.sub(r'src="assets/', 'src="/assets/', html)

    meta = f'''<link rel="icon" href="/assets/hcr-logo.png">
<link rel="canonical" href="{canonical}">
<meta property="og:url" content="{canonical}">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:image" content="{og_image}">
<meta property="og:locale" content="es_LA">
'''
    anchor = '<script src="/support.js"></script>'
    assert anchor in html, f"ANCLA NO ENCONTRADA en {src}: el formato del archivo dc cambió"
    html = html.replace(anchor, meta + anchor, 1)
    html = html.replace("https://hcrlatam.com/businessteamcoaching", canonical)
    if os.path.dirname(out_path):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, "w", encoding="utf-8").write(html)


build_page(
    SRC_CR,
    "index.html",
    canonical="https://iris.organizacionespositivas.org/",
    title="Certificación Business &amp; Team Coaching con LEGO® Serious Play® | Costa Rica · Octubre 2026",
    description="Certifícate como Business &amp; Team Coach con la Metodología LEGO® Serious Play®. 3 días presenciales en Costa Rica, máximo 12 cupos, Primera Generación. Reserva con $570 USD antes del 15 de agosto.",
    og_image="https://iris.organizacionespositivas.org/assets/foto-respaldo.jpg",
)

# 1b) nicaragua/index.html (misma landing, fechas/precios/sede de Nicaragua)
build_page(
    SRC_NI,
    "nicaragua/index.html",
    canonical="https://iris.organizacionespositivas.org/nicaragua/",
    title="Certificación Business &amp; Team Coaching con LEGO® Serious Play® | Nicaragua · Diciembre 2026",
    description="Certifícate como Business &amp; Team Coach con la Metodología LEGO® Serious Play®. 3 días presenciales en Nicaragua, máximo 12 cupos. Reserva con $370 USD antes del 31 de octubre.",
    og_image="https://iris.organizacionespositivas.org/assets/foto-respaldo.jpg",
)

# 2) support.js: React/Babel desde vendor/ en vez de unpkg (si las versiones coinciden)
#    Ruta absoluta: support.js se sirve desde la raíz y lo cargan ambas páginas.
s = open("support.js", encoding="utf-8").read()
vendor_map = {
    "https://unpkg.com/react@18.3.1/umd/react.production.min.js": "/vendor/react.production.min.js",
    "https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js": "/vendor/react-dom.production.min.js",
    "https://unpkg.com/@babel/standalone@7.29.0/babel.min.js": "/vendor/babel.min.js",
}
for cdn, local in vendor_map.items():
    local_rel = local.lstrip("/")
    if cdn in s and os.path.exists(local_rel):
        s = s.replace(cdn, local)
leftover = re.findall(r'https://unpkg\.com/[^"\']+', s)
if leftover:
    print("AVISO: URLs de unpkg sin mapear (el sitio las usará online):", leftover)
open("support.js", "w", encoding="utf-8").write(s)

# 3) image-slot.js + estado de encuadres: Netlify no sirve dotfiles.
#    Ruta absoluta también: image-slot.js es compartido y el fetch() del
#    estado debe resolver igual desde / que desde /nicaragua/.
j = open("image-slot.js", encoding="utf-8").read()
open("image-slot.js", "w", encoding="utf-8").write(j.replace("'.image-slots.state.json'", "'/image-slots.state.json'"))
shutil.copy(".image-slots.state.json", "image-slots.state.json")

# 4) No publicar material crudo ni fuentes duplicadas
for p in ["uploads", "landing-certificacion-lsp.html", SRC_CR, SRC_NI, "github.md", "build.py"]:
    (shutil.rmtree if os.path.isdir(p) else os.remove)(p) if os.path.exists(p) else None

print("Build OK: index.html y nicaragua/index.html generados")
