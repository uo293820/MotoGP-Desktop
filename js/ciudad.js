"use strict";

class Ciudad {
  constructor(nombre, pais, gentilicio) {
    this.nombre = nombre;
    this.pais = pais;
    this.gentilicio = gentilicio;

    this.poblacion = 0;
    this.latitud = 0;
    this.longitud = 0;
  }

  setInfoSecundaria(poblacion, latitud, longitud) {
    this.poblacion = poblacion;
    this.latitud = latitud;
    this.longitud = longitud;
  }

  // Devuelve el nombre de la ciudad en forma de texto
  getNombre() {
    return `${this.nombre}`;
  }

  // Devuelve el nombre del país en forma de texto
  getPais() {
    return `${this.pais}`;
  }

  // Devuelve una cadena HTML5 con una lista no ordenada (gentilicio y población)
  getInfoSecundaria() {
    return `<ul><li>Gentilicio: ${this.gentilicio}</li><li>Población: ${this.poblacion} habitantes</li></ul>`;
  }

  // Escribe en el documento la información de las coordenadas con la alternativa de document.write()
  escribirCoordenadas() {
    //const mensaje = document.createElement("p");
    //mensaje.textContent = `Coordenadas: lat ${this.latitud}, lon ${this.longitud}`;
    //document.body.appendChild(mensaje);
    document.write(`Coordenadas: lat ${this.latitud}, lon ${this.longitud}`);
  }
}