"""Analizador léxico y sintáctico de Mini-Calc."""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


SIMBOLOS = {
    "=": "OP_ASSIGN",
    "+": "OP_ADD",
    "-": "OP_SUB",
    "*": "OP_MUL",
    "/": "OP_DIV",
    "(": "PUNCT_LPAREN",
    ")": "PUNCT_RPAREN",
    ";": "PUNCT_SEMI",
}

INICIALES = {
    "p": "P",
    "letra": "ID",
    "digito": "NUM",
    "blanco": "BLANCO",
    **SIMBOLOS,
}

# Cualquier transición sin entrada en la tabla llega a MUERTO.
TRANSICIONES = {
    "INICIO": INICIALES,
    "P": {"r": "PR", "letra": "PALABRA_INVALIDA"},
    "PR": {"i": "PRI", "letra": "PALABRA_INVALIDA"},
    "PRI": {"n": "PRIN", "letra": "PALABRA_INVALIDA"},
    "PRIN": {"t": "PRINT", "letra": "PALABRA_INVALIDA"},
    "PRINT": {"letra": "PALABRA_INVALIDA"},
    "ID": {"letra": "PALABRA_INVALIDA"},
    "PALABRA_INVALIDA": {"letra": "PALABRA_INVALIDA"},
    "NUM": {"digito": "NUM"},
    "BLANCO": {"blanco": "BLANCO"},
}

ACEPTACION = {
    "P": "ID",
    "ID": "ID",
    "PRINT": "KW_PRINT",
    "NUM": "NUM",
    "BLANCO": "BLANCO",
    **{tipo: tipo for tipo in SIMBOLOS.values()},
}


@dataclass(frozen=True)
class Token:
    tipo: str
    lexema: str
    linea: int
    columna: int

    def __str__(self):
        literal = json.dumps(self.lexema, ensure_ascii=False)
        return f"<{self.tipo}, {literal}, {self.linea}, {self.columna}>"


class ErrorMiniCalc(Exception):
    def __init__(self, linea, columna, detalle):
        super().__init__(f"Error [Línea {linea}, Columna {columna}]: {detalle}")


def clase_caracter(caracter):
    if "a" <= caracter <= "z":
        return "letra"
    if "0" <= caracter <= "9":
        return "digito"
    if caracter in " \t\n":
        return "blanco"
    return caracter


def transicion(estado, caracter):
    destinos = TRANSICIONES.get(estado, {})
    return destinos.get(caracter) or destinos.get(clase_caracter(caracter), "MUERTO")


class Lexer:
    def analizar(self, fuente):
        indice = 0
        linea = columna = 1
        while indice < len(fuente):
            inicio = indice
            linea_inicio, columna_inicio = linea, columna
            estado = "INICIO"
            while indice < len(fuente):
                caracter = fuente[indice]
                siguiente = transicion(estado, caracter)
                if siguiente == "MUERTO":
                    break
                estado = siguiente
                indice += 1
                if caracter == "\n":
                    linea += 1
                    columna = 1
                else:
                    columna += 1

            lexema = fuente[inicio:indice]
            tipo = ACEPTACION.get(estado)
            if tipo is None:
                if estado == "INICIO":
                    detalle = f"Error léxico. Carácter no permitido {fuente[indice]!r}."
                else:
                    detalle = f"Error léxico. Palabra no reconocida {lexema!r}."
                raise ErrorMiniCalc(linea_inicio, columna_inicio, detalle)
            if tipo != "BLANCO":
                yield Token(tipo, lexema, linea_inicio, columna_inicio)

        yield Token("EOF", "", linea, columna)


class Parser:
    def __init__(self, tokens):
        self.tokens = iter(tokens)
        self.actual = next(self.tokens)

    def avanzar(self):
        token = self.actual
        self.actual = next(self.tokens)
        return token

    def error(self, esperado):
        token = self.actual
        encontrado = "el fin del archivo" if token.tipo == "EOF" else repr(token.lexema)
        raise ErrorMiniCalc(
            token.linea, token.columna,
            f"Error sintáctico. Se esperaba {esperado} y se encontró {encontrado}.",
        )

    def exigir(self, tipo, esperado):
        if self.actual.tipo != tipo:
            self.error(esperado)
        return self.avanzar()

    def programa(self):
        sentencias = self.lista_sentencias()
        if self.actual.tipo != "EOF":
            self.error("el fin del archivo")
        return sentencias

    def lista_sentencias(self):
        sentencias = []
        while self.actual.tipo in ("ID", "KW_PRINT"):
            sentencias.append(self.sentencia())
        return sentencias

    def sentencia(self):
        if self.actual.tipo == "ID":
            nombre = self.avanzar().lexema
            self.exigir("OP_ASSIGN", "'='")
            nodo = ("asignar", nombre, self.expresion())
        else:
            self.exigir("KW_PRINT", "'print'")
            nodo = ("print", self.expresion())
        self.exigir("PUNCT_SEMI", "';'")
        return nodo

    def expresion(self):
        return self.cola_expresion(self.termino())

    def cola_expresion(self, izquierda):
        while self.actual.tipo in ("OP_ADD", "OP_SUB"):
            operador = self.avanzar().lexema
            izquierda = (operador, izquierda, self.termino())
        return izquierda

    def termino(self):
        return self.cola_termino(self.factor())

    def cola_termino(self, izquierda):
        while self.actual.tipo in ("OP_MUL", "OP_DIV"):
            operador = self.avanzar().lexema
            izquierda = (operador, izquierda, self.factor())
        return izquierda

    def factor(self):
        if self.actual.tipo == "PUNCT_LPAREN":
            self.avanzar()
            nodo = self.expresion()
            self.exigir("PUNCT_RPAREN", "')'")
            return nodo
        if self.actual.tipo in ("ID", "NUM"):
            token = self.avanzar()
            return (token.tipo, token.lexema)
        self.error("una variable, un número o '('")


def main():
    argumentos = argparse.ArgumentParser(description=__doc__)
    argumentos.add_argument("archivo", type=Path, help="archivo fuente .calc en UTF-8")
    ruta = argumentos.parse_args().archivo
    try:
        # El modo texto normaliza CRLF, CR y LF para contar las líneas.
        fuente = ruta.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"Error al leer {ruta}: {error}", file=sys.stderr)
        return 2

    try:
        print("=== INICIO DE ANÁLISIS LÉXICO ===", flush=True)
        tokens = []
        for token in Lexer().analizar(fuente):
            tokens.append(token)
            if token.tipo != "EOF":
                print(token, flush=True)
        print("=== INICIO DE ANÁLISIS SINTÁCTICO ===", flush=True)
        parser = Parser(tokens)
        try:
            parser.programa()
        except RecursionError:
            token = parser.actual
            raise ErrorMiniCalc(
                token.linea, token.columna,
                "El anidamiento supera la capacidad de análisis recursivo."
            ) from None
    except ErrorMiniCalc as error:
        print(error, file=sys.stderr)
        return 1

    print("El análisis sintáctico finalizó exitosamente sin errores.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
