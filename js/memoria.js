"use strict";

class Memoria {
    constructor() {

    }
    
    voltearCarta(carta) {
        carta.setAttribute("data-estado", "volteada")
    }
}