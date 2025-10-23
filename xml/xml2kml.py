# -*- coding: utf-8 -*-
"""
Genera circuito.kml a partir de circuitoEsquema.xml (NS http://www.uniovi.es),
siguiendo la estructura del ejemplo 02020-KML.py (clase Kml).

@version 1.0 22/Octubre/2025
@author: Marcelo Díez Domínguez UO293820
"""

import xml.etree.ElementTree as ET

class Kml(object):

    def __init__(self):
        """
        Crea el elemento raíz y el espacio de nombres
        """
        self.raiz = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        self.doc = ET.SubElement(self.raiz, 'Document')

    def addPlacemark(self, nombre, descripcion, lon, lat, alt, modoAltitud="absolute"):
        """
        Añade un elemento <Placemark> con puntos <Point>
        """
        pm = ET.SubElement(self.doc, 'Placemark')
        ET.SubElement(pm, 'name').text = '\n' + nombre + '\n'
        ET.SubElement(pm, 'description').text = '\n' + descripcion + '\n'
        punto = ET.SubElement(pm, 'Point')
        ET.SubElement(punto, 'coordinates').text = '\n{},{},{}\n'.format(lon, lat, alt)
        ET.SubElement(punto, 'altitudeMode').text = '\n' + modoAltitud + '\n'

    """
    Añadir un elemento <PlaceMark> con puntos <Point>
    """
    def addLineString(self, nombre, extrude, tesela, listaCoordenadas, modoAltitud, color, ancho):
        """
        Añadir un elemento <PlaceMark> con puntos <Point>
        """
        ET.SubElement(self.doc, 'name').text = '\n' + nombre + '\n'
        pm = ET.SubElement(self.doc, 'Placemark')
        ls = ET.SubElement(pm, 'LineString')
        ET.SubElement(ls, 'extrude').text = '\n' + extrude + '\n'
        ET.SubElement(ls, 'tessellation').text = '\n' + tesela + '\n'
        ET.SubElement(ls, 'coordinates').text = '\n' + listaCoordenadas + '\n'
        ET.SubElement(ls, 'altitudeMode').text = '\n' + modoAltitud + '\n'

        estilo = ET.SubElement(pm, 'Style')
        linea = ET.SubElement(estilo, 'LineStyle')
        ET.SubElement(linea, 'color').text = '\n' + color + '\n'
        ET.SubElement(linea, 'width').text = '\n' + ancho + '\n'

    def escribir(self,nombreArchivoKML):
        """
        Escribe el archivo KML con declaración y codificación
        """
        arbol = ET.ElementTree(self.raiz)

        """
        Introduce indentacióon y saltos de línea
        para generar XML en modo texto
        """
        ET.indent(arbol)
        arbol.write(nombreArchivoKML, encoding='utf-8', xml_declaration=True)

    """
    Mostrar el archivo .KML (para depurar)
    """
    def ver(self):
        print("\nElemento raiz =", self.raiz.tag)

        if self.raiz.text != None:
            print("Contenido = "    , self.raiz.text.strip('\n')) #strip() elimina los '\n' del string
        else:
            print("Contenido = "    , self.raiz.text)

        print("Atributos = "    , self.raiz.attrib)

        for hijo in self.raiz.findall('.//'): # Expresión XPath
            print("\nElemento = " , hijo.tag)
            if hijo.text != None:
                print("Contenido = ", hijo.text.strip('\n')) #strip() elimina los '\n' del string
            else:
                print("Contenido = ", hijo.text)
            print("Atributos = ", hijo.attrib)
    

    def ver(self):
        """
        Muestra el archivo KML. Se utiliza para depurar
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


def obtenerCoordenadas(archivoXML):
    """
    Extrae las coordenadas de cada <tramo>/<coordenadas> y devuelve una lista
    de strings 'lon,lat,alt' en formato KML
    """
    try:
        arbol = ET.parse(archivoXML)
    except IOError:
        print("No se encuentra el archivo ", archivoXML)
        return[]
    except ET.ParseError:
        print("Error procesando el archivo XML ", archivoXML)
        return[]
    
    ns = {'uniovi': 'http://www.uniovi.es'}
    raiz = arbol.getroot()

    coordenadas = []

    # Recorrer cada <tramo> en orden
    for tramo in raiz.findall('.//uniovi:tramo', ns):
        coordenada = tramo.find('uniovi:coordenadas', ns)
        if coordenada is not None:
            longitud = coordenada.find('uniovi:longitud', ns)
            latitud = coordenada.find('uniovi:latitud', ns)
            altitud = coordenada.find('uniovi:altitud', ns)

            lon_val = (longitud.text.strip() if longitud is not None and longitud.text else "0")
            lat_val = (latitud.text.strip() if latitud is not None and latitud.text else "0")
            alt_val = (altitud.text.strip() if altitud is not None and altitud.text else "0")

            coordenadas.append(f"{lon_val},{lat_val},{alt_val}")
    return coordenadas

def obtenerOrigen(archivoXML):
    """
    Devuelve (lon, lat, alt) del <ubicacion>/<origen>, o None si no hay datos.
    """
    try:
        arbol = ET.parse(archivoXML)
    except IOError:
        print("No se encuentra el archivo ", archivoXML)
        return[]
    except ET.ParseError:
        print("Error procesando el archivo XML ", archivoXML)
        return[]

    ns = {'uniovi': 'http://www.uniovi.es'}
    raiz = arbol.getroot()

    longitud = raiz.find('.//uniovi:ubicacion/uniovi:origen/uniovi:longitud', ns)
    latitud = raiz.find('.//uniovi:ubicacion/uniovi:origen/uniovi:latitud', ns)
    altitud = raiz.find('.//uniovi:ubicacion/uniovi:origen/uniovi:altitud', ns)

    if longitud is None or latitud is None or longitud.text is None or latitud.text is None:
        return None
    
    lon_val = longitud.text.strip().replace(",", ".")
    lat_val = latitud.text.strip().replace(",", ".")
    alt_val = (altitud.text.strip().replace(",", ".") if (altitud is not None and altitud.text) else "0")

    return (f"{lon_val},{lat_val},{alt_val}")


def main():
    archivoXML = "circuitoEsquema.xml"
    nombreKML  = "circuito.kml"

    # 1) Coordenadas de la polilínea (cada coordenada: "lon,lat,alt")
    coordenadas = obtenerCoordenadas(archivoXML)
    if not coordenadas:
        print("No se encontraron coordenadas en el XML.")
        return

    # 2) Punto de origen ("lon,lat,alt")
    origen = obtenerOrigen(archivoXML)
    if not origen:
        print("No se encontró punto de origen en el XML.")
        return

    # 3) Construir la polilinea cerrada: origen + coordenadas + origen
    vertices = [origen] + coordenadas + [origen]
    cadena = "\n".join(vertices)

    # 4) Crear el KML
    kml = Kml()

    # Marcador del origen (desglosamos lon,lat,alt para el <Point>)
    try:
        lon, lat, alt = origen.split(",")
    except ValueError:
        print("Formato inesperado en el origen; se esperaba 'lon,lat,alt'")
        return
    
    kml.addPlacemark("Origen", "Punto de partida del circuito", lon, lat, alt, modoAltitud="absolute")
    
    # 5) Línea del trazado (circuito cerrado)
    kml.addLineString(
        nombre="Trazado del circuito",
        extrude="1",
        tesela="1",
        listaCoordenadas=cadena,                  
        modoAltitud="absolute",
        color="#ff0000ff", # AABBGGRR (rojo opaco)
        ancho="5"
    )

    # 6) Guardar
    kml.escribir(nombreKML)
    print("Creado el archivo:", nombreKML)

if __name__ == "__main__":
    main()
