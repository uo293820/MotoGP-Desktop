# -*- coding: utf-8 -*-
"""
Genera InfoCircuito.html a partir de circuitoEsquema.xml(NS http://www.uniovi.es).

@version 1.0 23/Octubre/2025
@author: Marcelo Díez Domínguez UO293820
"""

import xml.etree.ElementTree as ET
import html

class Html(object):

    def __init__(self, titulo_pagina):
        self.lines = []
        self._open_document(titulo_pagina)

    def _open_document(self, titulo_pagina):
        self.lines.append('<!DOCTYPE HTML>')
        self.lines.append('<html lang="es">')

        self.lines.append('<head>')
        self.lines.append('<meta charset="UTF-8" />')
        self.lines.append(f'<title>{html.escape(titulo_pagina)}</title>')
        self.lines.append('<meta name="viewport" content="width=device-width, initial-scale=1.0" />')
        self.lines.append('<link rel="stylesheet" type="text/css" href="estilo/estilo.css" />')
        self.lines.append('<link rel="stylesheet" href="estilo/layout.css" />')
        self.lines.append('<link rel="icon" type="image/png" href="multimedia/icon.png" />')
        self.lines.append('</head>')

        self.lines.append('<body>')

    def add_header(self):
        self.lines.append('<header>')
        self.lines.append('<h1>MotoGP Desktop</h1>')
        self.lines.append('</header>')

    def open_main(self):
        self.lines.append('<main>')

    def close_main(self):
        self.lines.append('</main>')

    def h2(self, text):
        self.lines.append(f'<h2>{html.escape(text)}</h2>')

    def h3(self, text):
        self.lines.append(f'<h3>{html.escape(text)}</h3>')

    def h4(self, text):
        self.lines.append(f'<h4>{html.escape(text)}</h4>')

    def list_kv(self, items):
        """
        items: [(label, value), ...] -> <ul><li>label: value</li>...</ul>
        """
        self.lines.append('<ul>')
        for label, value in items:
            self.lines.append(f'<li>{html.escape(label)}: {html.escape(value)}</li>')
        self.lines.append('</ul>')

    def table(self, caption, cols, rows):
        """
        cols: [("key","Cabecera"), ...]
        rows: [{"key": "valor", ...}, ...]
        """
        self.lines.append('<table>')
        self.lines.append(f'<caption>{html.escape(caption)}</caption>')
        self.lines.append('<thead>')
        self.lines.append('<tr>')
        for _k, head in cols:
            self.lines.append(f'<th scope="col">{html.escape(head)}</th>')
        self.lines.append('</tr>')
        self.lines.append('</thead>')
        self.lines.append('<tbody>')
        for row in rows:
            self.lines.append('<tr>')
            for k, _head in cols:
                self.lines.append(f'<td>{html.escape(str(row.get(k, "")))}</td>')
            self.lines.append('</tr>')
        self.lines.append('</tbody>')
        self.lines.append('</table>')

    def link_list(self, items):
        """items: [(texto, href), ...]"""
        self.lines.append('<ul>')
        for texto, href in items:
            self.lines.append(f'<li><a href="{html.escape(href)}" target="_blank" rel="noopener noreferrer">{html.escape(texto)}</a></li>')
        self.lines.append('</ul>')

    def write(self, filename):
        self.lines.append('</body>')
        self.lines.append('</html>')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.lines))


ns = {'u': 'http://www.uniovi.es'}

def _txt(el):
    return (el.text or "").strip() if el is not None else ""

def ftext(root, path):
    el = root.find(path, ns)
    return _txt(el)

def get_cabecera(root):
    return {
        "nombre": ftext(root, './/u:nombre'),
        "pais": ftext(root, './/u:pais'),
        "localidad": ftext(root, './/u:localidad'),
        "longitudCircuito": ftext(root, './/u:longitudCircuito'),
        "anchuraMedia": ftext(root, './/u:anchuraMedia'),
    }

def get_carrera(root):
    data = {
        "fecha":        ftext(root, './/u:carrera/u:fecha'),
        "horaEspaña":   ftext(root, './/u:carrera/u:horaEspaña'),
        "vueltas":      ftext(root, './/u:carrera/u:vueltas'),
        "patrocinador": ftext(root, './/u:carrera/u:patrocinador'),
        "vencedor":     ftext(root, './/u:carrera/u:resultado/u:vencedor'),
        "tiempo":       ftext(root, './/u:carrera/u:resultado/u:tiempo'),
    }
    clasif = []
    for pos in root.findall('.//u:carrera/u:clasificacionMundial/u:posicion', ns):
        num = (pos.get('numero') or '').strip()
        pil = ftext(pos, './u:piloto')
        clasif.append({"pos": num, "piloto": pil})
    data["clasificacion"] = clasif
    return data

def get_referencias(root):
    refs = []
    for r in root.findall('.//u:referencias/u:ref', ns):
        url = _txt(r)
        if url:
            refs.append((url, url))
    return refs

def get_media(root):
    fotos, videos = [], []
    for f in root.findall('.//u:media/u:fotos/u:foto', ns):
        desc = f.get('descripción', '') or 'Foto'
        url  = _txt(f)
        if url:
            fotos.append((f"{desc} — {url}", url))
    for v in root.findall('.//u:media/u:videos/u:video', ns):
        desc = v.get('descripción', '') or 'Vídeo'
        url  = _txt(v)
        if url:
            videos.append((f"{desc} — {url}", url))
    return fotos, videos


def generar_html(archivoXML, nombreHTML='InfoCircuito.html'):
    try:
        arbol = ET.parse(archivoXML)
    except IOError:
        print(f'No se encuentra el archivo: {archivoXML}')
        return
    except ET.ParseError:
        print(f'Error procesando el archivo XML: {archivoXML}')
        return

    root = arbol.getroot()

    # Extraer datos (omite <ubicacion>)
    cab = get_cabecera(root)
    car = get_carrera(root)
    refs = get_referencias(root)
    fotos, videos = get_media(root)

    nombre = cab.get('nombre', '').strip()
    titulo_pagina = f"MotoGP - Circuito{(' - ' + nombre) if nombre else ''}"

    # Construir HTML con la clase Html
    doc = Html(titulo_pagina)
    doc.add_header()
    doc.open_main()

    # Identificación
    doc.h2(nombre or "Circuito")
    doc.h3("Identificación")
    doc.list_kv([
        ("País",      cab.get("pais","")),
        ("Localidad", cab.get("localidad","")),
    ])

    # Características
    doc.h3("Características del circuito")
    doc.list_kv([
        ("Longitud del circuito", cab.get("longitudCircuito","")),
        ("Anchura media",         cab.get("anchuraMedia","")),
    ])

    # Carrera
    doc.h3("Carrera")
    doc.list_kv([
        ("Fecha",         car.get("fecha","")),
        ("Hora (España)", car.get("horaEspaña","")),
        ("Vueltas",       car.get("vueltas","")),
        ("Patrocinador",  car.get("patrocinador","")),
        ("Vencedor",      car.get("vencedor","")),
        ("Tiempo",        car.get("tiempo","")),
    ])

    # Clasificación
    if car.get("clasificacion"):
        doc.h3("Clasificación del Mundial")
        cols = [("pos", "Posición"), ("piloto", "Piloto")]
        doc.table("Clasificación del Mundial", cols, car["clasificacion"])

    # Referencias
    if refs:
        doc.h3("Referencias")
        doc.link_list(refs)

    # Media
    if fotos or videos:
        doc.h3("Multimedia")
        if fotos:
            doc.h4("Fotos")
            doc.link_list(fotos)
        if videos:
            doc.h4("Vídeos")
            doc.link_list(videos)

    # Cierre
    doc.close_main()
    doc.write(nombreHTML)
    print("Creado el archivo:", nombreHTML)


def main():
    generar_html("circuitoEsquema.xml", "InfoCircuito.html")

if __name__ == "__main__":
    main()
