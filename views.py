from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON

# Solo los gestores leen y escriben archivos.
gestor_estudiantes = GestorJSON('estudiantes.json')
gestor_materias = GestorJSON('materias.json')
gestor_matriculas = GestorJSON('matriculas.json')


def leer_objetos(gestor, clase):
    return [clase.desde_diccionario(dato) for dato in gestor.leer()]


def obtener_por_id(gestor, clase, identificador):
    for objeto in leer_objetos(gestor, clase):
        if objeto.id == identificador:
            return objeto
    return None


def buscar(gestor, clase, texto, campos):
    # TUPLA de campos: son nombres fijos que no necesitamos cambiar.
    texto = str(texto).strip().lower()
    if not texto:
        return []
    encontrados = []
    for objeto in leer_objetos(gestor, clase):
        if any(texto in str(getattr(objeto, campo)).lower() for campo in campos):
            encontrados.append(objeto)
    return encontrados


def siguiente_id(gestor):
    return max((dato['id'] for dato in gestor.leer()), default=0) + 1


def guardar_nuevo(gestor, objeto):
    registros = gestor.leer()
    registros.append(objeto.a_diccionario())  # LISTA: permite añadir nuevos registros.
    return gestor.guardar(registros)


def reemplazar(gestor, objeto):
    registros = gestor.leer()
    for posicion, dato in enumerate(registros):
        if dato['id'] == objeto.id:
            registros[posicion] = objeto.a_diccionario()
            return gestor.guardar(registros)
    return False


def eliminar(gestor, identificador):
    registros = gestor.leer()
    nuevos = [dato for dato in registros if dato['id'] != identificador]
    if len(nuevos) == len(registros):
        return False
    return gestor.guardar(nuevos)


def ids_registrados(gestor):
    # CONJUNTO: permite saber si un id existe sin recorrer la lista manualmente.
    return {dato['id'] for dato in gestor.leer()}


def indice_por_id(gestor, clase):
    # DICCIONARIO índice: acceso directo a objetos mediante su id.
    return {objeto.id: objeto for objeto in leer_objetos(gestor, clase)}


def es_email_valido(email):
    partes = email.split('@')
    return (len(partes) == 2 and bool(partes[0]) and '.' in partes[1]
            and not partes[1].startswith('.') and not partes[1].endswith('.'))


# ESTUDIANTES

def obtener_estudiantes():
    return leer_objetos(gestor_estudiantes, Estudiante)


def obtener_estudiante(identificador):
    return obtener_por_id(gestor_estudiantes, Estudiante, identificador)


def buscar_estudiantes(termino):
    return buscar(gestor_estudiantes, Estudiante, termino,
                  ('nombre', 'apellido', 'email', 'carnet', 'carrera'))


def validar_estudiante(datos, excepto_id=None):
    for campo in ('nombre', 'apellido', 'email', 'carnet'):
        if not str(datos.get(campo, '')).strip():
            return f'El campo {campo} es obligatorio.'
    email = str(datos['email']).strip().lower()
    carnet = str(datos['carnet']).strip().upper()
    if not es_email_valido(email):
        return 'El correo no es válido.'
    # CONJUNTOS: evitan carnets y correos repetidos.
    otros = [e for e in obtener_estudiantes() if e.id != excepto_id]
    carnets = {e.carnet.upper() for e in otros}
    emails = {e.email.lower() for e in otros}
    if carnet in carnets:
        return 'El carnet ya está registrado.'
    if email in emails:
        return 'El correo ya está registrado.'
    return None


def crear_estudiante(datos):
    error = validar_estudiante(datos)
    if error:
        return False, error  # TUPLA (éxito, mensaje).
    objeto = Estudiante(siguiente_id(gestor_estudiantes),
                        str(datos['nombre']).strip().title(),
                        str(datos['apellido']).strip().title(),
                        str(datos['email']).strip().lower(),
                        str(datos['carnet']).strip().upper(),
                        str(datos.get('carrera', '')).strip().title())
    if not guardar_nuevo(gestor_estudiantes, objeto):
        return False, 'No se pudo guardar.'
    return True, f'Estudiante registrado: {objeto.etiqueta()}'


def actualizar_estudiante(identificador, cambios):
    objeto = obtener_estudiante(identificador)
    if objeto is None:
        return False, 'El estudiante no existe.'
    datos = objeto.a_diccionario()
    for campo in ('nombre', 'apellido', 'email', 'carnet', 'carrera'):
        if campo in cambios:
            datos[campo] = cambios[campo]
    error = validar_estudiante(datos, identificador)
    if error:
        return False, error
    nuevo = Estudiante(identificador, str(datos['nombre']).strip().title(),
                       str(datos['apellido']).strip().title(),
                       str(datos['email']).strip().lower(),
                       str(datos['carnet']).strip().upper(),
                       str(datos['carrera']).strip().title())
    if not reemplazar(gestor_estudiantes, nuevo):
        return False, 'No se pudo actualizar.'
    return True, 'Estudiante actualizado.'


def eliminar_estudiante(identificador):
    if identificador not in ids_registrados(gestor_estudiantes):
        return False, 'El estudiante no existe.'
    if any(m.estudiante_id == identificador for m in obtener_matriculas()):
        return False, 'No se puede eliminar: tiene matrículas. Retíralas primero.'
    return (True, 'Estudiante eliminado.') if eliminar(gestor_estudiantes, identificador) else (False, 'No se pudo eliminar.')


# MATERIAS

def obtener_materias():
    return leer_objetos(gestor_materias, Materia)


def obtener_materia(identificador):
    return obtener_por_id(gestor_materias, Materia, identificador)


def buscar_materias(termino):
    return buscar(gestor_materias, Materia, termino, ('nombre', 'codigo'))


def validar_materia(datos, excepto_id=None):
    if not str(datos.get('nombre', '')).strip() or not str(datos.get('codigo', '')).strip():
        return 'Nombre y código son obligatorios.'
    try:
        creditos = int(datos['creditos'])
        cupos = int(datos['cupos'])
    except (KeyError, TypeError, ValueError):
        return 'Créditos y cupos deben ser números enteros.'
    if not 1 <= creditos <= 10:
        return 'Los créditos deben estar entre 1 y 10.'
    if not 0 <= cupos <= Materia.CUPOS_MAXIMOS:
        return f'Los cupos deben estar entre 0 y {Materia.CUPOS_MAXIMOS}.'
    # CONJUNTO: un código no se puede repetir.
    codigos = {m.codigo.upper() for m in obtener_materias() if m.id != excepto_id}
    if str(datos['codigo']).strip().upper() in codigos:
        return 'Ese código ya existe.'
    return None


def crear_materia(datos):
    error = validar_materia(datos)
    if error:
        return False, error
    objeto = Materia(siguiente_id(gestor_materias), str(datos['nombre']).strip(),
                     str(datos['codigo']).strip().upper(),
                     int(datos['creditos']), int(datos['cupos']))
    if not guardar_nuevo(gestor_materias, objeto):
        return False, 'No se pudo guardar.'
    return True, f'Materia registrada: {objeto.etiqueta()}'


def actualizar_materia(identificador, cambios):
    objeto = obtener_materia(identificador)
    if objeto is None:
        return False, 'La materia no existe.'
    datos = objeto.a_diccionario()
    for campo in ('nombre', 'codigo', 'creditos', 'cupos'):
        if campo in cambios:
            datos[campo] = cambios[campo]
    error = validar_materia(datos, identificador)
    if error:
        return False, error
    matriculados = sum(m.materia_id == identificador for m in obtener_matriculas())
    if int(datos['cupos']) > Materia.CUPOS_MAXIMOS - matriculados:
        return False, 'Los cupos libres más los matriculados no pueden superar el máximo.'
    nuevo = Materia(identificador, str(datos['nombre']).strip(),
                    str(datos['codigo']).strip().upper(), int(datos['creditos']), int(datos['cupos']))
    if not reemplazar(gestor_materias, nuevo):
        return False, 'No se pudo actualizar.'
    return True, 'Materia actualizada.'


def eliminar_materia(identificador):
    if identificador not in ids_registrados(gestor_materias):
        return False, 'La materia no existe.'
    if any(m.materia_id == identificador for m in obtener_matriculas()):
        return False, 'No se puede eliminar: tiene matrículas. Retíralas primero.'
    return (True, 'Materia eliminada.') if eliminar(gestor_materias, identificador) else (False, 'No se pudo eliminar.')


def materias_sin_cupo():
    return [materia for materia in obtener_materias() if not materia.hay_cupo()]


# MATRÍCULAS

def obtener_matriculas():
    return leer_objetos(gestor_matriculas, Matricula)


def obtener_matricula(identificador):
    return obtener_por_id(gestor_matriculas, Matricula, identificador)


def crear_matricula(datos):
    try:
        estudiante_id = int(datos['estudiante_id'])
        materia_id = int(datos['materia_id'])
        periodo = str(datos['periodo']).strip()
        nota = float(datos.get('nota', 0))
    except (KeyError, ValueError, TypeError):
        return False, 'Datos de matrícula incorrectos.'
    if estudiante_id not in ids_registrados(gestor_estudiantes):
        return False, 'El estudiante no existe.'
    materia = obtener_materia(materia_id)
    if materia is None:
        return False, 'La materia no existe.'
    if not periodo:
        return False, 'El periodo es obligatorio.'
    if not materia.hay_cupo():
        return False, 'La materia no tiene cupos disponibles.'
    if not Materia.es_nota_valida(nota):
        return False, 'La nota debe estar entre 0 y 20.'
    for matricula in obtener_matriculas():
        if (matricula.estudiante_id == estudiante_id and matricula.materia_id == materia_id
                and matricula.periodo.lower() == periodo.lower()):
            return False, 'El estudiante ya está matriculado en esa materia y periodo.'
    objeto = Matricula(siguiente_id(gestor_matriculas), estudiante_id, materia_id, periodo, nota)
    materia.ocupar_cupo()
    if not reemplazar(gestor_materias, materia):
        return False, 'No se pudo actualizar el cupo.'
    if not guardar_nuevo(gestor_matriculas, objeto):
        materia.liberar_cupo()
        reemplazar(gestor_materias, materia)
        return False, 'No se pudo registrar la matrícula.'
    return True, f'Matrícula #{objeto.id} registrada.'


def registrar_nota(identificador, nota):
    matricula = obtener_matricula(identificador)
    if matricula is None:
        return False, 'La matrícula no existe.'
    if not Materia.es_nota_valida(nota):
        return False, 'La nota debe estar entre 0 y 20.'
    matricula.nota = float(nota)
    if not reemplazar(gestor_matriculas, matricula):
        return False, 'No se pudo guardar la nota.'
    return True, f'Nota registrada. Estado: {matricula.estado()}.'


def retirar_matricula(identificador):
    matricula = obtener_matricula(identificador)
    if matricula is None:
        return False, 'La matrícula no existe.'
    materia = obtener_materia(matricula.materia_id)
    if not eliminar(gestor_matriculas, identificador):
        return False, 'No se pudo retirar la matrícula.'
    if materia is not None:
        materia.liberar_cupo()
        if not reemplazar(gestor_materias, materia):
            guardar_nuevo(gestor_matriculas, matricula)
            return False, 'No se pudo devolver el cupo.'
    return True, 'Matrícula retirada y cupo liberado.'


def certificado(identificador):
    matricula = obtener_matricula(identificador)
    if matricula is None:
        return None
    # DICCIONARIOS ÍNDICE {id: objeto}: unen tres archivos por su identificador.
    estudiantes = indice_por_id(gestor_estudiantes, Estudiante)
    materias = indice_por_id(gestor_materias, Materia)
    estudiante = estudiantes.get(matricula.estudiante_id)
    materia = materias.get(matricula.materia_id)
    if estudiante is None or materia is None:
        return None
    return (f'CERTIFICADO #{matricula.id}  periodo: {matricula.periodo}\n'
            f'Estudiante: {estudiante.nombre_completo()} ({estudiante.carnet})\n'
            f'Materia: {materia.nombre} ({materia.codigo}) - {materia.creditos} créditos\n'
            f'Fecha: {matricula.fecha}\n'
            f'Nota: {matricula.nota:g}\nEstado: {matricula.estado()}')


def matriculas_por_estudiante():
    # DICCIONARIO DE LISTAS: cada estudiante puede tener varias matrículas.
    grupos = {}
    for matricula in obtener_matriculas():
        grupos.setdefault(matricula.estudiante_id, []).append(matricula)
    return grupos


def promedio_de_estudiante(identificador):
    matriculas = matriculas_por_estudiante().get(identificador, [])
    if not matriculas:
        return None
    return sum(m.nota for m in matriculas) / len(matriculas)
