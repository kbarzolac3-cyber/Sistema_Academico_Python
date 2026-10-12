import views as sistema


def mostrar_lista(registros):
    # POLIMORFISMO: este mismo código muestra cualquiera de los tres modelos.
    if not registros:
        print('No hay registros.')
    for registro in registros:
        print(registro)


def mostrar_detalle(registro):
    if registro is None:
        print('No se encontró el registro.')
    else:
        print(registro)
        for campo, valor in registro.a_diccionario().items():
            print(f'  {campo}: {valor}')


def pedir_numero(mensaje):
    try:
        return int(input(mensaje))
    except ValueError:
        print('Debes escribir un número entero.')
        return None


def mostrar_resultado(resultado):
    exito, mensaje = resultado
    print(('OK: ' if exito else 'ERROR: ') + mensaje)


def pedir_campos(campos, actual=None):
    datos = {}
    for campo in campos:
        valor_anterior = getattr(actual, campo) if actual is not None else None
        aviso = f'{campo}'
        if actual is not None:
            aviso += f' [{valor_anterior}]'
        valor = input(aviso + ': ').strip()
        if actual is None or valor:
            datos[campo] = valor
    return datos


def menu_estudiantes():
    while True:
        print('\n--- ESTUDIANTES ---')
        print('1. Registrar  2. Ver todos  3. Buscar  4. Ver por ID')
        print('5. Actualizar  6. Eliminar  0. Volver')
        opcion = input('Opción: ').strip()
        if opcion == '0':
            return
        elif opcion == '1':
            datos = pedir_campos(('nombre', 'apellido', 'email', 'carnet', 'carrera'))
            mostrar_resultado(sistema.crear_estudiante(datos))
        elif opcion == '2':
            mostrar_lista(sistema.obtener_estudiantes())
        elif opcion == '3':
            mostrar_lista(sistema.buscar_estudiantes(input('Buscar: ')))
        elif opcion == '4':
            identificador = pedir_numero('ID: ')
            if identificador is not None:
                mostrar_detalle(sistema.obtener_estudiante(identificador))
        elif opcion == '5':
            identificador = pedir_numero('ID a actualizar: ')
            if identificador is not None:
                actual = sistema.obtener_estudiante(identificador)
                if actual is None:
                    print('No existe ese estudiante.')
                else:
                    print('Pulsa Enter para conservar el valor anterior.')
                    cambios = pedir_campos(('nombre', 'apellido', 'email', 'carnet', 'carrera'), actual)
                    mostrar_resultado(sistema.actualizar_estudiante(identificador, cambios))
        elif opcion == '6':
            identificador = pedir_numero('ID a eliminar: ')
            if identificador is not None and input('¿Confirmar? (si/no): ').lower() == 'si':
                mostrar_resultado(sistema.eliminar_estudiante(identificador))
        else:
            print('Opción no válida.')


def menu_materias():
    while True:
        print('\n--- MATERIAS ---')
        print('1. Registrar  2. Ver todas  3. Buscar  4. Ver por ID')
        print('5. Actualizar  6. Eliminar  0. Volver')
        opcion = input('Opción: ').strip()
        if opcion == '0':
            return
        elif opcion == '1':
            datos = pedir_campos(('nombre', 'codigo', 'creditos', 'cupos'))
            mostrar_resultado(sistema.crear_materia(datos))
        elif opcion == '2':
            mostrar_lista(sistema.obtener_materias())
        elif opcion == '3':
            mostrar_lista(sistema.buscar_materias(input('Buscar: ')))
        elif opcion == '4':
            identificador = pedir_numero('ID: ')
            if identificador is not None:
                mostrar_detalle(sistema.obtener_materia(identificador))
        elif opcion == '5':
            identificador = pedir_numero('ID a actualizar: ')
            if identificador is not None:
                actual = sistema.obtener_materia(identificador)
                if actual is None:
                    print('No existe esa materia.')
                else:
                    print('Pulsa Enter para conservar el valor anterior.')
                    cambios = pedir_campos(('nombre', 'codigo', 'creditos', 'cupos'), actual)
                    mostrar_resultado(sistema.actualizar_materia(identificador, cambios))
        elif opcion == '6':
            identificador = pedir_numero('ID a eliminar: ')
            if identificador is not None and input('¿Confirmar? (si/no): ').lower() == 'si':
                mostrar_resultado(sistema.eliminar_materia(identificador))
        else:
            print('Opción no válida.')


def menu_matriculas():
    while True:
        print('\n--- MATRÍCULAS ---')
        print('1. Matricular  2. Ver todas  3. Registrar nota')
        print('4. Ver certificado  5. Retirar matrícula  0. Volver')
        opcion = input('Opción: ').strip()
        if opcion == '0':
            return
        elif opcion == '1':
            print('Estudiantes:')
            mostrar_lista(sistema.obtener_estudiantes())
            print('Materias:')
            mostrar_lista(sistema.obtener_materias())
            datos = pedir_campos(('estudiante_id', 'materia_id', 'periodo'))
            mostrar_resultado(sistema.crear_matricula(datos))
        elif opcion == '2':
            mostrar_lista(sistema.obtener_matriculas())
        elif opcion == '3':
            identificador = pedir_numero('ID de matrícula: ')
            if identificador is not None:
                nota = input('Nota (0 a 20): ')
                mostrar_resultado(sistema.registrar_nota(identificador, nota))
        elif opcion == '4':
            identificador = pedir_numero('ID de matrícula: ')
            if identificador is not None:
                print(sistema.certificado(identificador) or 'No se encontró el certificado.')
        elif opcion == '5':
            identificador = pedir_numero('ID de matrícula a retirar: ')
            if identificador is not None and input('¿Confirmar? (si/no): ').lower() == 'si':
                mostrar_resultado(sistema.retirar_matricula(identificador))
        else:
            print('Opción no válida.')


def ver_resumen():
    estudiantes = sistema.obtener_estudiantes()
    matriculas = sistema.obtener_matriculas()
    # CONJUNTO para quitar carreras duplicadas; sorted() para ordenarlas.
    carreras = sorted({e.carrera for e in estudiantes if e.carrera})
    print('\n--- RESUMEN ---')
    print('Estudiantes registrados:', len(estudiantes))
    print('Carreras:', ', '.join(carreras) if carreras else 'Ninguna')
    print('Materias sin cupo:', len(sistema.materias_sin_cupo()))
    print('Matrículas aprobadas:', sum(m.esta_aprobada() for m in matriculas))
    identificador = pedir_numero('ID de estudiante para ver promedio (0 para omitir): ')
    if identificador:
        promedio = sistema.promedio_de_estudiante(identificador)
        print('Promedio:', f'{promedio:.2f}' if promedio is not None else 'Sin matrículas')


def main():
    while True:
        print('\n=================================')
        print('        SISTEMA ACADÉMICO')
        print('=================================')
        print('1. Estudiantes')
        print('2. Materias')
        print('3. Matrículas')
        print('4. Resumen')
        print('0. Salir')
        opcion = input('Seleccione una opción: ').strip()
        if opcion == '1':
            menu_estudiantes()
        elif opcion == '2':
            menu_materias()
        elif opcion == '3':
            menu_matriculas()
        elif opcion == '4':
            ver_resumen()
        elif opcion == '0':
            print('Hasta luego.')
            break
        else:
            print('Opción no válida.')


if __name__ == '__main__':
    main()
