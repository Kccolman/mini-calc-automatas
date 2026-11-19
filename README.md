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

## Repositorio del equipo

1. Una persona del equipo crea el repositorio en GitHub e invita a los demás integrantes.
2. Suban el contenido de esta carpeta al repositorio. Cada integrante puede
   trabajar en su propia rama y aportar una mejora o prueba identificable.
3. Antes de hacer su commit, cada integrante debe comprobar que Git use el nombre
   y un correo vinculados a su cuenta de GitHub. Una vez integradas las ramas,
   revisen que el historial muestre al menos un commit de cada integrante.
4. Incorporen el enlace del repositorio al informe y completen la portada antes
   de exportar el PDF para el Aula Virtual.

Temas para distribuir el trabajo entre los seis integrantes: tabla del AFD,
reconocimiento de tokens, transformación de la gramática, parser de expresiones,
mensajes de error y pruebas con archivos.
