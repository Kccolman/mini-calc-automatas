import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from minicalc import ErrorMiniCalc, Lexer, Parser


RAIZ = Path(__file__).resolve().parent


def analizar(texto):
    return Parser(list(Lexer().analizar(texto))).programa()


class PruebasMiniCalc(unittest.TestCase):
    def test_ejemplo_completo(self):
        texto = (RAIZ / "ejemplos/ejemplo.calc").read_text(encoding="utf-8")
        programa = analizar(texto)
        self.assertEqual(len(programa), 3)
        self.assertEqual(programa[2], ("print", ("ID", "y")))

    def test_precedencia(self):
        self.assertEqual(
            analizar("print 10 + 5 * 2;")[0][1],
            ("+", ("NUM", "10"), ("*", ("NUM", "5"), ("NUM", "2"))),
        )

    def test_parentesis(self):
        self.assertEqual(
            analizar("print (x - 4) / 2;")[0][1],
            ("/", ("-", ("ID", "x"), ("NUM", "4")), ("NUM", "2")),
        )

    def test_asociatividad_izquierda(self):
        self.assertEqual(
            analizar("print 10 - 4 - 2;")[0][1],
            ("-", ("-", ("NUM", "10"), ("NUM", "4")), ("NUM", "2")),
        )
        self.assertEqual(
            analizar("print 16 / 4 / 2;")[0][1],
            ("/", ("/", ("NUM", "16"), ("NUM", "4")), ("NUM", "2")),
        )

    def test_token_palabra_reservada_y_posiciones(self):
        tokens = list(Lexer().analizar("p = 0;\n\tprint p;"))
        self.assertEqual(
            [(t.tipo, t.lexema, t.linea, t.columna) for t in tokens],
            [
                ("ID", "p", 1, 1), ("OP_ASSIGN", "=", 1, 3),
                ("NUM", "0", 1, 5), ("PUNCT_SEMI", ";", 1, 6),
                ("KW_PRINT", "print", 2, 2), ("ID", "p", 2, 8),
                ("PUNCT_SEMI", ";", 2, 9), ("EOF", "", 2, 10),
            ],
        )

    def test_programa_vacio(self):
        self.assertEqual(analizar(" \n\t"), [])

    def test_caracteres_invalidos(self):
        for caracter in "@$Á":
            with self.subTest(caracter=caracter):
                with self.assertRaisesRegex(ErrorMiniCalc, "Línea 2, Columna 9.*léxico"):
                    analizar(f"x = 10;\nprint x {caracter} 2;")

    def test_palabras_invalidas(self):
        for palabra in ("ab", "pr", "pri", "prin", "printx"):
            with self.subTest(palabra=palabra):
                with self.assertRaisesRegex(ErrorMiniCalc, "Línea 1, Columna 1.*léxico"):
                    analizar(f"{palabra} = 2;")

    def test_falta_punto_y_coma(self):
        with self.assertRaisesRegex(ErrorMiniCalc, "Línea 2, Columna 1.*';'"):
            analizar("x = 10\nprint x;")
        with self.assertRaisesRegex(ErrorMiniCalc, "Línea 1, Columna 7.*fin del archivo"):
            analizar("x = 10")

    def test_falta_parentesis(self):
        with self.assertRaisesRegex(ErrorMiniCalc, "Línea 1, Columna 13.*'\\)'"):
            analizar("print (2 + 3;")

    def test_resto_del_programa_y_factor_invalido(self):
        for texto, columna in (("x=2; 3;", 6), ("print 2 + ;", 11), ("print -2;", 7)):
            with self.subTest(texto=texto):
                with self.assertRaisesRegex(ErrorMiniCalc, f"Línea 1, Columna {columna}.*sintáctico"):
                    analizar(texto)

    def test_consola_y_archivos(self):
        casos = [
            ("ejemplo.calc", 0, "", True),
            ("error_lexico.calc", 1, "Línea 2, Columna 9", False),
            ("error_punto_y_coma.calc", 1, "Línea 2, Columna 1", True),
            ("error_parentesis.calc", 1, "Línea 1, Columna 13", True),
        ]
        for archivo, codigo, error, pasa_al_parser in casos:
            with self.subTest(archivo=archivo):
                salida = self.ejecutar(RAIZ / "ejemplos" / archivo)
                self.assertEqual(salida.returncode, codigo)
                self.assertIn(error, salida.stderr)
                self.assertEqual("INICIO DE ANÁLISIS SINTÁCTICO" in salida.stdout, pasa_al_parser)
                self.assertEqual("finalizó exitosamente" in salida.stdout, codigo == 0)

    def test_fin_de_linea_windows(self):
        with tempfile.TemporaryDirectory() as directorio:
            archivo = Path(directorio) / "windows.calc"
            archivo.write_bytes(b"x=2;\r\nprint x;\r\n")
            salida = self.ejecutar(archivo)
            self.assertEqual(salida.returncode, 0)
            self.assertIn('<KW_PRINT, "print", 2, 1>', salida.stdout)

    @staticmethod
    def ejecutar(archivo):
        return subprocess.run(
            [sys.executable, str(RAIZ / "minicalc.py"), str(archivo)],
            capture_output=True, encoding="utf-8", check=False,
        )


if __name__ == "__main__":
    unittest.main()
