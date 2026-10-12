# Sistema Académico en Python

Proyecto de consola que aplica MVC, herencia, polimorfismo, colecciones y archivos JSON.

## Cómo ejecutarlo

1. Abre la carpeta `Sistema_Academico` en Visual Studio Code.
2. Abre la terminal.
3. Ejecuta `python main.py` (o `py main.py` en algunos equipos Windows).
4. Empieza por registrar un estudiante y una materia antes de matricular.

## Archivos

- `models.py`: clases y reglas propias de cada objeto.
- `views.py`: operaciones y validaciones; no usa `print` ni `input`.
- `main.py`: menús y entrada/salida de consola.
- `shared/json_manager.py`: única parte que lee y escribe archivos JSON.
- `data/`: almacena las listas de registros.

## Prueba manual sugerida

1. Registra un estudiante con carnet `EST2026001`.
2. Registra una materia con código `MAT101`, 4 créditos y 30 cupos.
3. Matricula al estudiante en la materia para el periodo `2026-1`.
4. Comprueba que la materia ahora tenga 29 cupos.
5. Registra la nota `16.5` y consulta el certificado.
6. Intenta matricular de nuevo al mismo estudiante en esa materia y periodo: debe rechazarlo.
7. Retira la matrícula y comprueba que el cupo vuelve a 30.

Nota: al crear la matrícula, la nota inicia en 0 hasta que se registra. En esta versión el estado se calcula siempre a partir de la nota.
