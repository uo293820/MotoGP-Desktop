# -*- coding: utf-8 -*-
"""
Genera InfoCircuito.html a partir de circuitoEsquema.xml(NS http://www.uniovi.es).

@version 1.0 23/Octubre/2025
@author: Marcelo Díez Domínguez UO293820
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import re

class Html:
    def __init__(self, lang, titulo, css_href, icon_href, nombreCircuito):
        self.html = ET.Element("html", lang=lang)
        
        self.head = ET.SubElement(self.html, "head")
        ET.SubElement(self.head, "meta", charset="UTF-8")
        ET.SubElement(self.head, "title").text = titulo + " - " + nombreCircuito
        ET.SubElement(self.head, "meta", name="description", content="Informe HTML generado desde circuitoEsquema.xml")
        ET.SubElement(self.head, "meta", name="viewport", content="width=device-width, initial-scale=1.0")
        ET.SubElement(self.head, "link", rel="stylesheet", type="text/css", href=css_href)
        ET.SubElement(self.head, "link", rel="icon", type="image/png", href=icon_href)

        # <body>
        self.body = ET.SubElement(self.html, "body")
        self.header = ET.SubElement(self.body, "header")
        self.main = ET.SubElement(self.body, "main")
        # Encabezado principal
        h1 = ET.SubElement(self.header, "h1")
        h1.text = titulo

    # ---------- Constructores de bloques ----------

    def add_section(self):
        """
        Añade un elemento <section>.
        """
        section = ET.SubElement(self.main, "section")
        return section

    def add_h2(self, parent, title_text):
        """
        Añade un elemento <h2> dentro del elemento 'parent' y lo devuelve.
        """
        h2 = ET.SubElement(parent, "h2")
        h2.text = title_text
        return h2

    def add_h3(self, parent, title_text):
        """
        Añade un elemento <h3> dentro del elemento 'parent' y lo devuelve.
        """
        h3 = ET.SubElement(parent, "h3")
        h3.text = title_text
        return h3

    def add_paragraph(self, parent, text):
        """
        Añade un elemento <p> dentro del elemento 'parent' y lo devuelve.
        """
        p = ET.SubElement(parent, "p")
        p.text = text
        return p

    def add_unordered_list(self, parent):
        """
        Añade un elemento <ul> dentro del elemento 'parent' y lo devuelve.
        """
        ul = ET.SubElement(parent, "ul")
        return ul

    def add_li_label_value(self, ul, label, value):
        """
        Añade un elemento <li> al elemento <ul> especificado con los valores 'label' y 'value'
        Formato: <li>label: values</li>
        """
        li = ET.SubElement(ul, "li")
        li.text = f"{label}: {value}"
        return li

    def add_table(self, parent, caption_text, columns):
        """
        Crea una tabla accesible con <caption>, <thead> y <tbody>.
        headers: lista de textos de encabezado de columna.
        Devuelve (table, tbody)
        """
        table = ET.SubElement(parent, "table")
        caption = ET.SubElement(table, "caption")
        caption.text = caption_text

        thead = ET.SubElement(table, "thead")
        trh = ET.SubElement(thead, "tr")

        col_ids = []
        for col in columns:
            cid, label = (col["id"], col["label"]) if isinstance(col, dict) else col
            th = ET.SubElement(trh, "th", scope="col", id=cid)
            th.text = label
            col_ids.append(cid)

        tbody = ET.SubElement(table, "tbody")
        return table, tbody, col_ids

    def add_table_row_with_headers(self, tbody, values, col_ids):
        """
        Añade una fila <tr> en <tbody>. Cada valor se coloca en un <td>
        con el atributo headers apuntando al ID de su columna.
        - values: lista/tupla de strings (mismo orden que col_ids)
        - col_ids: lista de ids 'th-...' devuelta por add_table_with_col_headers
        """
        tr = ET.SubElement(tbody, "tr")
        for value, cid in zip(values, col_ids):
            td = ET.SubElement(tr, "td", headers=cid)
            td.text = value
        return tr

    def add_aside(self):
        """
        Añade un elemento <aside> y lo devuelve.
        """
        aside = ET.SubElement(self.main, "aside")
        return aside

    def add_link_item(self, ul, href):
        """
        Añade un elemento <li><a href="...">text</a></li> y lo devuelve.
        """
        li = ET.SubElement(ul, "li")
        a_attrs = {"href": href}
        a = ET.SubElement(li, "a", **a_attrs)
        a.text = href
        return li
    
    def add_picture(self, parent, sources, img_src, img_alt=""):
        """
        Crea <picture> con múltiples <source media srcset> y un <img> de respaldo.
        sources: lista de dicts con claves: {"media": "...","srcset":"..."}
        """
        picture = ET.SubElement(parent, "picture")
        for s in sources:
            ET.SubElement(picture, "source", media=s["media"], srcset=s["srcset"])
        ET.SubElement(picture, "img", src=img_src, alt=img_alt)
        return picture

    def add_picture_simple(self, parent, src, alt=""):
        """
        Crea <picture> con solo <img> (cuando no hay variantes responsive).
        """
        picture = ET.SubElement(parent, "picture")
        ET.SubElement(picture, "img", src=src, alt=alt)
        return picture

    def add_video(self, parent, sources, controls=True, preload="auto"):
        """
        Crea <video> con múltiples <source>.
        sources: lista de (src, mime) como ('multimedia/file.mp4','video/mp4')
        """
        attrs = {}
        if controls:
            attrs["controls"] = ""
        if preload:
            attrs["preload"] = preload
        video = ET.SubElement(parent, "video", **attrs)
        for src, mime in sources:
            ET.SubElement(video, "source", src=src, type=mime)
        return video


    # ---------- Salida ----------

    def _serialize(self):
        """
        Serializa el árbol HTML como string, añadiendo el DOCTYPE manualmente.
        """
        tree = ET.ElementTree(self.html)
        # 'indent' mejora la legibilidad (si está disponible en tu versión de Python)
        try:
            ET.indent(tree)  # Python 3.9+
        except Exception:
            pass
        html_str = ET.tostring(self.html, encoding="unicode", method="html")
        return "<!DOCTYPE html>\n" + html_str

    def write(self, filename):
        Path(filename).write_text(self._serialize(), encoding="utf-8")

# ---------- Lógica para conversión de formatos ----------

def iso8601_to_str(iso_str):
    """
    Convierte una duración ISO-8601 (p.ej. 'PT40M42.854S') a string.
    Formato: 'HH horas, MM minutos y SS segundos'.
    """
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?", iso_str or "")
    if not m:
        return iso_str

    h = int(m.group(1) or 0)
    mi = int(m.group(2) or 0)
    s_raw = m.group(3) or "0"

    try:
        s_val = float(s_raw)
        s_txt = f"{s_val:.3f}".rstrip("0").rstrip(".")
    except ValueError:
        s_txt = s_raw

    return f"{h:02d} horas, {mi:02d} minutos y {s_txt} segundos"

# ---------- Lógica de extracción y generación ----------

def generar_html(archivo_xml="circuitoEsquema.xml", archivo_html="InfoCircuito.html"):
    """
    Lee 'archivo_xml' (namespace http://www.uniovi.es) y genera 'archivo_html'.
    Se usan expresiones XPath y se excluyen:
      - ubicación/origen
      - trazado/tramo
    """
    # Cargar XML
    try:
        tree = ET.parse(archivo_xml)
    except FileNotFoundError:
        raise SystemExit(f"No se encuentra el archivo: {archivo_xml}")
    except ET.ParseError as e:
        raise SystemExit(f"Error de sintaxis en el XML: {e}")

    root = tree.getroot()
    ns = {"u": "http://www.uniovi.es"}  # namespace del documento

    # ---------- XPaths (solo lo que el XML proporcione) ----------
    # Identificación del circuito
    nombre = root.findtext(".//u:nombre", default="", namespaces=ns)
    pais = root.findtext(".//u:pais", default="", namespaces=ns)
    localidad = root.findtext(".//u:localidad", default="", namespaces=ns)

    # Medidas ( con atributo unidades )
    long_elem = root.find(".//u:longitudCircuito", ns)
    anch_elem = root.find(".//u:anchuraMedia", ns)

    longitud = (long_elem.text or "").strip() if long_elem is not None else ""
    long_uni = long_elem.get("unidades", "") if long_elem is not None else ""

    anchura = (anch_elem.text or "").strip() if anch_elem is not None else ""
    anch_uni = anch_elem.get("unidades", "") if anch_elem is not None else ""

    # Información de carrera
    fecha = root.findtext(".//u:carrera/u:fecha", default="", namespaces=ns)
    hora_es = root.findtext(".//u:carrera/u:horaEspaña", default="", namespaces=ns)
    vueltas = root.findtext(".//u:carrera/u:vueltas", default="", namespaces=ns)
    patrocinador = root.findtext(".//u:carrera/u:patrocinador", default="", namespaces=ns)

    vencedor = root.findtext(".//u:carrera/u:resultado/u:vencedor", default="", namespaces=ns)
    tiempo = root.findtext(".//u:carrera/u:resultado/u:tiempo", default="", namespaces=ns)

    # Clasificación mundial (posiciones)
    posiciones = []
    for pos in root.findall(".//u:carrera/u:clasificacionMundial/u:posicion", ns):
        numero = (pos.get("numero") or "").strip()
        piloto = pos.findtext("u:piloto", default="", namespaces=ns)
        if numero or piloto:
            posiciones.append((numero, piloto))
    
    # Referencias
    refs = [n.text.strip() for n in root.findall(".//u:referencias/u:ref", ns) if (n.text or "").strip()]
    if not refs:
        refs = [n.text.strip() for n in root.findall(".//referencias/ref") if (n.text or "").strip()]

    # Fotos
    from pathlib import PurePosixPath
    # Buscar cualquier <foto> (con namespace o sin él)
    candidatos_foto = root.findall(".//u:foto", ns) or root.findall(".//foto")

    # Agrupamos por base (sin sufijo -movil/-tablet y sin extensión)
    # fotos_por_base[base_key] = {"movil": "...", "tablet": "...", "desktop": "...", "alt": "..."}
    fotos_por_base = {}

    for f in candidatos_foto:
        ruta_raw = (f.text or "").strip()
        if not ruta_raw:
            continue

        # alt desde el atributo (soportamos con y sin tilde)
        alt = f.get("descripción") or f.get("descripcion") or ""

        # Como en el ejemplo de vídeo: anteponemos "../" directamente
        # (si en el XML ya viene "multimedia/...", quedará "../multimedia/...")
        src = f"../{ruta_raw}"

        p = PurePosixPath(src)
        stem = p.stem                 # nombre sin extensión
        parent = p.parent

        # Detectar variante por sufijo
        if stem.endswith("-movil"):
            base_stem = stem[:-6]     # quita '-movil'
            variante = "movil"
        elif stem.endswith("-tablet"):
            base_stem = stem[:-7]     # quita '-tablet'
            variante = "tablet"
        else:
            base_stem = stem          # desktop (sin sufijo)
            variante = "desktop"

        # Clave base (manteniendo la carpeta) sin sufijo ni extensión
        base_key = str(parent / base_stem)

        entry = fotos_por_base.setdefault(
            base_key, {"movil": None, "tablet": None, "desktop": None, "alt": ""}
        )
        entry[variante] = str(p)
        if alt and not entry["alt"]:
            entry["alt"] = alt

    # Videos
    videos_por_stem = {}  # stem -> [{"src":..., "mime":..., "desc":...}, ...]
    # 1) Buscar cualquier <video> en el documento (primero con namespace, si no, sin él)
    candidatos = root.findall(".//u:video", ns) or root.findall(".//video")
    for v in candidatos:
        ruta_raw = (v.text or "").strip()
        if not ruta_raw:
            continue
        desc = v.get("descripción") or ""
        src = f"../{ruta_raw}"
        p = PurePosixPath(src)
        ext = p.suffix.lower()
        if ext == ".mp4":
            mime = "video/mp4"
        elif ext == ".webm":
            mime = "video/webm"
        else:
            continue
        stem = str(p.with_suffix(""))  # nombre sin extensión, para agrupar mp4+webm
        videos_por_stem.setdefault(stem, []).append({
            "src": str(p),
            "mime": mime,
            "desc": desc
        })


    # ---------- Construcción del HTML ----------
    doc = Html(lang="es",
                titulo="MotoGP Desktop",
                css_href="../estilo/estilo.css",
                icon_href="../multimedia/icon.png",
                nombreCircuito=nombre)

    # Sección: Datos del circuito
    sec_datos = doc.add_section()
    doc.add_h2(sec_datos, "Datos del circuito")

    ul = doc.add_unordered_list(sec_datos)

    if nombre:
        doc.add_li_label_value(ul, "Nombre", nombre)
    if pais:
        doc.add_li_label_value(ul, "País", pais)
    if localidad:
        doc.add_li_label_value(ul, "Localidad", localidad)
    if longitud:
        doc.add_li_label_value(ul, "Longitud del circuito", f"{longitud} {long_uni}".strip())
    if anchura:
        doc.add_li_label_value(ul, "Anchura media", f"{anchura} {anch_uni}".strip())

    # Sección: Carrera (ul + sub-ul en Resultado)
    sec_carrera = doc.add_section()
    doc.add_h2(sec_carrera, "Carrera")

    ul_car = doc.add_unordered_list(sec_carrera)

    if fecha:
        doc.add_li_label_value(ul_car, "Fecha", fecha)

    if hora_es:
        doc.add_li_label_value(ul_car, "Hora (España)", hora_es)

    if vueltas:
        doc.add_li_label_value(ul_car, "Vueltas", vueltas)

    if patrocinador:
        doc.add_li_label_value(ul_car, "Patrocinador", patrocinador)

    # Sublista para Resultado
    if vencedor or tiempo:
        # Crea el <li> "Resultado:" sin valor
        li_res = ET.SubElement(ul_car, "li")
        li_res.text = "Resultado:"  # sin valor aquí

        # sublista dentro de Resultado
        sub = doc.add_unordered_list(li_res)

        if vencedor:
            doc.add_li_label_value(sub, "Vencedor", vencedor)

        if tiempo:
            tiempo_fmt = iso8601_to_str(tiempo)  # típico en carreras
            doc.add_li_label_value(sub, "Tiempo", tiempo_fmt)

    # Sección: Clasificación mundial
    if posiciones:
        doc.add_h3(sec_carrera, "Clasificación mundial")

        cols = [
            ("th-posicion", "Posición"),
            ("th-piloto",   "Piloto"),
        ]
        table, tbody, col_ids = doc.add_table(
            parent=sec_carrera,
            caption_text="Clasificación mundial al finalizar la carrera",
            columns=cols
        )
        for pos_num, pil in posiciones:
            doc.add_table_row_with_headers(tbody, [pos_num, pil], col_ids)

    # Sección Media
    if fotos_por_base or videos_por_stem:
        sec_media = doc.add_section()
        doc.add_h2(sec_media, "Media")

        if fotos_por_base:
            doc.add_h3(sec_media, "Imágenes")
            for base_key, datos in sorted(fotos_por_base.items(), key=lambda kv: kv[0]):
                movil = datos["movil"]
                tablet = datos["tablet"]
                desktop = datos["desktop"]
                alt = datos["alt"] or ""  # evita None

                # Construimos la lista de <source> SOLO con lo que exista en el XML
                sources = []
                if movil:
                    sources.append({"media": "(max-width: 465px)", "srcset": movil})
                if tablet:
                    sources.append({"media": "(max-width: 799px)", "srcset": tablet})
                if desktop:
                    sources.append({"media": "(min-width: 800px)", "srcset": desktop})

                # Fallback del <img>: preferimos desktop, luego tablet, luego móvil
                img_src = desktop or tablet or movil
                if not img_src:
                    # Si no hay ninguna ruta válida, no renderizamos esta entrada
                    continue

                if sources:
                    # Hay al menos una variante: <picture> con <source> + <img>
                    doc.add_picture(sec_media, sources=sources, img_src=img_src, img_alt=alt)
                else:
                    # Solo una imagen sin variantes: <picture><img .../></picture>
                    doc.add_picture_simple(sec_media, src=img_src, alt=alt)

        # ----- Vídeos -----
        if videos_por_stem:
            doc.add_h3(sec_media, "Vídeos")
            for stem, fuentes in sorted(videos_por_stem.items(), key=lambda kv: kv[0]):
                # Ordena para mostrar MP4 primero (opcional pero habitual)
                fuentes_ordenadas = sorted(
                    fuentes,
                    key=lambda x: 0 if x["mime"] == "video/mp4" else 1
                )
                sources = [(f["src"], f["mime"]) for f in fuentes_ordenadas]

                # Si hay descripción en alguna fuente, úsala como pie de figura
                # (tomanos la primera no vacía)
                desc = next((f["desc"] for f in fuentes_ordenadas if f.get("desc")), "")

                if desc:
                    # <figure> envolviendo el vídeo + <figcaption>
                    fig = ET.SubElement(sec_media, "figure")
                    doc.add_video(fig, sources=sources, controls=True, preload="auto")
                    cap = ET.SubElement(fig, "figcaption"); cap.text = desc
                else:
                    # Sin descripción: solo el vídeo
                    doc.add_video(sec_media, sources=sources, controls=True, preload="auto")
    
    # Sección (aside) referencias
    if refs:
        aside = doc.add_aside()
        doc.add_h2(aside, "Referencias")
        ul_refs = doc.add_unordered_list(aside)
        for url in refs:
            doc.add_link_item(ul_refs, href=url)

    # Guardar
    doc.write(archivo_html)
    print(f"Archivo HTML generado: {archivo_html}")

def main():
    archivoXML = "circuitoEsquema.xml"
    nombreHTML  = "InfoCircuito.html"

    generar_html(archivoXML, nombreHTML)

if __name__ == "__main__":
    main()
