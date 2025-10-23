# -*- coding: utf-8 -*-
"""
Genera altimetria.svg a partir de circuitoEsquema.xml (NS http://www.uniovi.es),
siguiendo la estructura del ejemplo 02030-SVG.py (clase Svg).

@version 1.0 22/Octubre/2025
@author: Marcelo Díez Domínguez UO293820
"""

import xml.etree.ElementTree as ET
from math import isclose

class Svg(object):

    def __init__(self):
        """
        Crea el elemento raíz, el espacio de nombres y la versión
        """
        self.raiz = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", version="1.1")
    
    def addRect(self, x, y, width, height, fill, strokeWidth, stroke):
        """
        Añade un elemento rect
        """
        ET.SubElement(self.raiz, 'rect',
                                    x=str(x), y=str(y), width=str(width), height=str(height),
                                    fill=fill, **{"strokeWidth": str(strokeWidth)}, stroke=stroke)
    
    def addCircle(self, cx, cy, r, fill):
        """
        Añade un elemento circle
        """
        ET.SubElement(self.raiz, 'circle',
                                    cx=str(cx), cy=str(cy), r=str(r), fill=fill)

    def addLine(self, x1, y1, x2, y2, stroke, strokeWidth):
        """
        Añade un elemento line
        """
        ET.SubElement(self.raiz,'line',
                                    x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2),
                                    stroke=stroke, **{"strokeWidth": str(strokeWidth)})
    
    def addPolyline(self, points, stroke, strokeWidth, fill):
        """
        Añade un elemento polyline
        """
        ET.SubElement(self.raiz, 'polyline',
                                    points=points, stroke=stroke,
                                    **{"strokeWidth": str(strokeWidth)}, fill=fill)
    
    def addText(self, texto, x, y, fontFamily, fontSize, style):
        """
        Añade un elemento texto
        """
        ET.SubElement(self.raiz, 'text',
                                    x=str(x), y=str(y),
                                    **{"fontFamily": fontFamily, "fontSize": str(fontSize), "style": style}).text=texto

    def escribir(self,nombreArchivoSVG):
        """
        Escribe el archivo SVG con declaración y codificación
        """
        arbol = ET.ElementTree(self.raiz)
        
        """
        Introduce indentacióon y saltos de línea para generar XML en modo texto
        """
        ET.indent(arbol)
        arbol.write(nombreArchivoSVG, encoding='utf-8', xml_declaration=True)


    def ver(self):
        """
        Muestra el archivo SVG. Se utiliza para depurar
        """
        print("\nElemento raiz = ", self.raiz.tag)
        if self.raiz.text != None:
            print("Contenido = " , self.raiz.text.strip('\n')) #strip() elimina los '\n' del string
        else:
            print("Contenido = " , self.raiz.text)

        print("Atributos = " , self.raiz.attrib)
        
        # Recorrido de los elementos del árbol
        for hijo in self.raiz.findall('.//'): # Expresión XPath
            print("\nElemento = " , hijo.tag)
            if hijo.text != None:
                print("Contenido = ", hijo.text.strip('\n')) #strip() elimina los '\n' del string
            else:
                print("Contenido = ", hijo.text)
            print("Atributos = ", hijo.attrib)


def obtenerTramos(archivoXML):
    """
    Devuelve lista de dicts: [{'dist': float, 'alt': float, 'sector': int}, ...]
    a partir de //trazado/tramo/(distancia, coordenadas/altitud, sector)
    """
    try:
        arbol = ET.parse(archivoXML)
    except IOError:
        print("No se encuentra el archivo ", archivoXML)
        return []
    except ET.ParseError:
        print("Error procesando el archivo XML ", archivoXML)
        return []

    ns = {'uniovi': 'http://www.uniovi.es'}
    raiz = arbol.getroot()

    tramos = []

    # Altitud y sector del Punto origen
    altitud_origen = raiz.find('.//uniovi:ubicacion/uniovi:origen/uniovi:altitud', ns)
    if altitud_origen is not None and altitud_origen.text:
        alt_origen = float(altitud_origen.text.strip().replace(",", "."))
    else:
        alt_origen = 0.0
    
    primer_sector_el = raiz.find('.//uniovi:trazado/uniovi:tramo[1]/uniovi:sector', ns)
    try:
        sector_origen = int(primer_sector_el.text.strip()) if (primer_sector_el is not None and primer_sector_el.text) else None
    except ValueError:
        sector_origen = None

    tramos.append({"dist": 0.0, "alt": alt_origen, "sector": sector_origen})

    # Altitudes y sectores del resto de puntos
    for tramo in raiz.findall('.//uniovi:trazado/uniovi:tramo', ns):
        distancia = tramo.find('uniovi:distancia', ns)
        dist_val = float(distancia.text.strip().replace(",", ".")) if (distancia is not None and distancia.text) else 0.0

        coordenadas = tramo.find('uniovi:coordenadas', ns)
        altitud = coordenadas.find('uniovi:altitud', ns) if coordenadas is not None else None
        alt_val  = float(altitud.text.strip().replace(",", ".")) if (altitud is not None and altitud.text) else 0.0

        sector = tramo.find('uniovi:sector', ns)
        try:
            sect_val = int(sector.text.strip()) if (sector is not None and sector.text) else None
        except ValueError:
            sect_val = None

        tramos.append({"dist": dist_val, "alt": alt_val, "sector": sect_val})

    return tramos

def generarAltimetria(archivoXML, nombreSVG, cerrar_polilinea=True):

    # 1) Datos
    tramos = obtenerTramos(archivoXML)
    if not tramos:
        print("No se han encontrado tramos en el XML.")
        return

    dists = [t["dist"] for t in tramos]
    alts  = [t["alt"]  for t in tramos]
    sects = [t["sector"] for t in tramos]

    # 2) Distancia acumulada (m)
    acum = []
    s = 0.0
    for d in dists:
        s += d
        acum.append(s)
    total = acum[-1] if acum else 0.0

    # 3) Rango altitudes
    max_alt = max(alts) if alts else 1.0
    if max_alt == 0.0:
        max_alt = 1.0  # evita división por cero

    # 4) Lienzo y márgenes (básico)
    W, H = 1000, 400
    ML, MR, MT, MB = 80, 40, 30, 60
    plot_w, plot_h = W - ML - MR, H - MT - MB

    # 5) Transformaciones a pantalla
    def fx(d_acum):
        return ML + (d_acum/total)*plot_w if total > 0 else ML

    def fy(alt):
        # 0m en la base, max_alt en la parte superior
        return MT + (max_alt - alt) / (max_alt - 0.0) * plot_h

    # 6) Puntos de la curva (cerrando con origen como punto final)
    x_vals = acum[:]
    y_vals = alts[:]
    if cerrar_polilinea:
        x_vals.append(total)
        y_vals.append(alts[0])

    pts = " ".join(f"{fx(x):.2f},{fy(y):.2f}" for x, y in zip(x_vals, y_vals))

    # 7) Preparar SVG
    nuevoSVG = Svg()
    # -> Fondo
    nuevoSVG.addRect('0', '0', str(W), str(H), '#ffffff', '0', 'none')
    # -> Título
    nuevoSVG.addText('Altimetría', str(W//2), '24', 'Verdana', '16', 'text-anchor: middle;')

    # 8) Referencias verticales
    y_eje_x = fy(0.0)          # eje X a 0 m
    y_top = fy(max_alt)        # parte superior (altitud máxima)
    
    # 9) Fondo rojo claro (área bajo la curva)
    pts_fill = " ".join([
        f"{ML:.2f},{y_eje_x:.2f}",         # base izquierda
        pts,                                # curva
        f"{(ML + plot_w):.2f},{y_eje_x:.2f}"  # base derecha
    ])
    nuevoSVG.addPolyline(pts_fill, 'none', '0', '#ffebee')  # rojo muy claro

    # 10) Polilínea roja del perfil
    nuevoSVG.addPolyline(pts, 'red', '2.5', 'none')

    # 11) Divisores de SECTOR (gris claro) + etiquetas centradas debajo del eje X
    color_sector = '#d0d0d0'
    sector_bounds = []
    last_sec = None
    for i, sec in enumerate(sects):
        if i == 0 or sec != last_sec:
            sector_bounds.append((fx(acum[i]), sec))
            last_sec = sec
    sector_bounds.append((ML + plot_w, last_sec))  # borde derecho

    # -> Líneas verticales completas
    for x, _sec in sector_bounds:
        nuevoSVG.addLine(f"{x:.2f}", f"{y_top:.2f}",
                            f"{x:.2f}", f"{y_eje_x:.2f}",
                            color_sector, '1')

    # -> Etiquetas centradas entre límites consecutivos (debajo del eje X)
    for (x1, sec_left), (x2, _sec_right) in zip(sector_bounds[:-1], sector_bounds[1:]):
        x_mid = (x1 + x2) / 2.0
        nuevoSVG.addText(f"S{sec_left}",
                            f"{x_mid:.2f}", f"{(y_eje_x + 18):.2f}",
                            'Verdana', '10', 'text-anchor: middle;')

    # 12) Marca única en eje Y para altitud máxima
    nuevoSVG.addLine(str(ML - 6), f"{y_top:.2f}", str(ML), f"{y_top:.2f}", '#000000', '1')
    nuevoSVG.addText(f"{max_alt:.0f}", str(ML - 10), f"{y_top + 4:.2f}",
                        'Verdana', '11', 'text-anchor: end;')
    
    # 13) Ejes
    # -> Eje X (0 m)
    nuevoSVG.addLine(str(ML), f"{y_eje_x:.2f}", str(ML + plot_w), f"{y_eje_x:.2f}", '#000000', '1.5')
    # -> Eje Y (0 → max_alt)
    nuevoSVG.addLine(str(ML), f"{y_eje_x:.2f}", str(ML), f"{y_top:.2f}", '#000000', '1.5')

    # 14) Guardar
    nuevoSVG.escribir(nombreSVG)
    print("Creado el archivo:", nombreSVG)


def main():
    archivoXML = "circuitoEsquema.xml"
    nombreSVG  = "altimetria.svg"

    generarAltimetria(archivoXML, nombreSVG, cerrar_polilinea=True)

if __name__ == "__main__":
    main()