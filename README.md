# Mini-Calc

Trabajo práctico final de Teoría de Autómatas. El programa lee un archivo `.calc`,
muestra sus tokens y comprueba que el programa cumple la gramática. Reconoce
asignaciones, sentencias `print` y expresiones con operadores binarios.
La instrucción `print` se valida durante el análisis sintáctico.

## Ejecutar en Windows

Abrí en VS Code la carpeta donde está `minicalc.py` y ejecutá los comandos
desde la terminal integrada. Se requiere Python 3.8 o posterior.

```powershell
py -3 minicalc.py ejemplos/ejemplo.calc
py -3 minicalc.py ejemplos/error_lexico.calc
py -3 minicalc.py ejemplos/error_punto_y_coma.calc
py -3 minicalc.py ejemplos/error_parentesis.calc
py -3 -m unittest -v
```

En Linux o macOS, podés usar `python3` en lugar de `py -3`. Guardá los archivos
fuente como UTF-8. El código de salida es 0 cuando el análisis termina con éxito,
1 ante un error del lenguaje o de capacidad recursiva, y 2 si falla la lectura
del archivo o se invoca incorrectamente el programa.

## Archivos

- `minicalc.py` contiene el AFD, el lexer, el parser y el punto de entrada.
- `test_minicalc.py` contiene las pruebas automatizadas.
- `ejemplos/` contiene un programa válido y tres archivos con errores.

