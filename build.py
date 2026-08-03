#!/usr/bin/env python3
"""Build de la landing para Netlify.
Genera index.html desde el archivo de Claude Design y adapta el runtime.
Los archivos fuente del repo quedan intactos (esto corre solo en el build)."""
import re, shutil, os, sys

SRC = "Landing Certificacion LSP.dc.html"

# 1) index.html = diseño + metas para previews (WhatsApp/Meta) + favicon
html = open(SRC, encoding="utf-8").read()
META = '''<link rel="icon" href="assets/hcr-logo.png">
<title>Certificación Business &amp; Team Coaching con LEGO® Serious Play® | Costa Rica · Octubre 2026</title>
<meta name="description" content="Certifícate como Business &amp; Team Coach con la Metodología LEGO® Serious Play®. 3 días presenciales en Costa Rica, máximo 12 cupos, Primera Generación. Reserva con $570 USD antes del 15 de agosto.">
<meta property="og:title" content="Certificación Business &amp; Team Coaching con LEGO® Serious Play® | Costa Rica · Octubre 2026">
<meta property="og:description" content="3 días presenciales en Costa Rica, máximo 12 cupos, Primera Generación. Reserva con $570 USD antes del 15 de agosto.">
<meta property="og:type" content="website">
<meta property="og:image" content="https://iris.organizacionespositivas.org/assets/foto-respaldo.jpg">
<meta property="og:locale" content="es_LA">
'''
anchor = '<script src="./support.js"></script>'
assert anchor in html, "ANCLA NO ENCONTRADA: el formato del archivo dc cambió"
open("index.html", "w", encoding="utf-8").write(html.replace(anchor, META + anchor, 1))

# 2) support.js: React/Babel desde vendor/ en vez de unpkg (si las versiones coinciden)
s = open("support.js", encoding="utf-8").read()
vendor_map = {
    "https://unpkg.com/react@18.3.1/umd/react.production.min.js": "vendor/react.production.min.js",
    "https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js": "vendor/react-dom.production.min.js",
    "https://unpkg.com/@babel/standalone@7.29.0/babel.min.js": "vendor/babel.min.js",
}
for cdn, local in vendor_map.items():
    if cdn in s and os.path.exists(local):
        s = s.replace(cdn, local)
leftover = re.findall(r'https://unpkg\.com/[^"\']+', s)
if leftover:
    print("AVISO: URLs de unpkg sin mapear (el sitio las usará online):", leftover)
open("support.js", "w", encoding="utf-8").write(s)

# 3) image-slot.js + estado de encuadres: Netlify no sirve dotfiles
j = open("image-slot.js", encoding="utf-8").read()
open("image-slot.js", "w", encoding="utf-8").write(j.replace("'.image-slots.state.json'", "'image-slots.state.json'"))
shutil.copy(".image-slots.state.json", "image-slots.state.json")

# 4) No publicar material crudo ni fuentes duplicadas
for p in ["uploads", "landing-certificacion-lsp.html", SRC, "github.md", "build.py"]:
    (shutil.rmtree if os.path.isdir(p) else os.remove)(p) if os.path.exists(p) else None

print("Build OK: index.html generado")
