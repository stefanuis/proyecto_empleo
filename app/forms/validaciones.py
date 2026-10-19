
from datetime import date, datetime


def fila_vacia(entry, campos):
    valores = []

    for campo in campos:

        valor = getattr(
            entry,
            campo
        ).data

        valores.append(valor)

    return all(
        valor in (None, "")
        for valor in valores
    )

def validar_personal(entry):

    errores = []

    if not entry.nombres.data:
        errores.append(
            "El nombre es obligatorio."
        )

    if not entry.apellidos.data:
        errores.append(
            "Los apellidos son obligatorios."
        )

    if not entry.telefono.data:
        errores.append(
            "El teléfono es obligatorio."
        )

    if not entry.tipo_doc.data:
        errores.append(
            "El tipo de documento es obligatorio."
        )
    if not entry.num_doc.data:
        errores.append(
            "El número de documento es obligatorio."
        )
    if not entry.fecha_exp_doc.data:
        errores.append(
           "La fecha de expedición es obligatoria."
        )
    if not entry.fecha_nacimiento.data:
            errores.append(
            "La fecha de nacimiento es obligatoria."
        )
    if not entry.genero.data:
            errores.append(
            "El género es obligatorio."
        )
    return errores

    
def validar_academica(entry):

        errores= []
        
        if not entry.nivel.data:
            errores.append("El nivel académico es obligatorio.")

        if not entry.estado.data:
            errores.append("El estado académico es obligatorio.")

        if not entry.titulo.data:
            errores.append("El título es obligatorio.")

        if not entry.institucion.data:
            errores.append("La institución es obligatoria.")

        if entry.estado.data == "finalizado":
            hoy = date.today()
            campo_mes = entry.mes_finalizacion
            campo_anno = entry.anno_finalizacion
            mes_raw = (campo_mes.raw_data or [""])[0].strip()
            anno_raw = (campo_anno.raw_data or [""])[0].strip()
            mes = campo_mes.data
            anno = campo_anno.data
            mes_valido = isinstance(mes, int) and 1 <= mes <= 12
            anno_valido = (
                isinstance(anno, int)
                and len(anno_raw) == 4
                and anno_raw.isdigit()
                and 1950 <= anno <= hoy.year
            )

            if not mes_raw:
                campo_mes.errors = [
                    *campo_mes.errors,
                    "El mes de finalización es obligatorio.",
                ]
            elif not mes_valido:
                campo_mes.errors = [
                    *campo_mes.errors,
                    "El mes debe ser un número entre 1 y 12.",
                ]

            if not anno_raw:
                campo_anno.errors = [
                    *campo_anno.errors,
                    "El año de finalización es obligatorio.",
                ]
            elif not anno_valido:
                campo_anno.errors = [
                    *campo_anno.errors,
                    f"El año debe estar entre 1950 y {hoy.year}.",
                ]

            if (
                mes_valido
                and anno_valido
                and anno == hoy.year
                and mes > hoy.month
            ):
                campo_mes.errors = [
                    *campo_mes.errors,
                    "La fecha de finalización no puede ser futura.",
                ]

        return errores       
        
            
def a_fecha(valor):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    return None


def rangos_se_cruzan(inicio_a, fin_a, inicio_b, fin_b):
    inicio_a = a_fecha(inicio_a)
    fin_a = a_fecha(fin_a)
    inicio_b = a_fecha(inicio_b)
    fin_b = a_fecha(fin_b)
    return bool(
        inicio_a
        and fin_a
        and inicio_b
        and fin_b
        and inicio_a <= fin_b
        and inicio_b <= fin_a
    )


def _fecha_minima_por_edad(fecha_nacimiento, edad):
    try:
        return fecha_nacimiento.replace(year=fecha_nacimiento.year + edad)
    except ValueError:
        return fecha_nacimiento.replace(
            year=fecha_nacimiento.year + edad,
            day=28,
        )


def validar_experiencia(
    entry,
    fecha_nacimiento=None,
    validar_rango_fechas=True,
    hoy=None,
):
    errores = []
    hoy = hoy or date.today()
    fecha_ingreso = a_fecha(entry.fecha_ingreso.data)
    fecha_salida = a_fecha(entry.fecha_salida.data)
    nacimiento = a_fecha(fecha_nacimiento)

    if not entry.entidad.data:
        errores.append("El nombre de la entidad/empresa es obligatorio.")

    if not entry.area.data:
        errores.append("El área de trabajo es obligatoria.")

    if not entry.cargo.data:
        errores.append("El cargo es obligatorio.")

    if not fecha_ingreso:
        errores.append("La fecha de ingreso es obligatoria.")

    if validar_rango_fechas:
        if fecha_ingreso:
            if fecha_ingreso < date(1950, 1, 1):
                errores.append("La fecha de ingreso debe ser desde 1950.")
            if fecha_ingreso > hoy:
                errores.append("La fecha de ingreso no puede ser futura.")
            if nacimiento:
                edad_minima = _fecha_minima_por_edad(nacimiento, 14)
                if fecha_ingreso < edad_minima:
                    errores.append(
                        "La fecha de ingreso no puede ser anterior a los 14 años."
                    )

        if fecha_salida:
            if fecha_salida > hoy:
                errores.append("La fecha de salida no puede ser futura.")
            if fecha_ingreso and fecha_salida < fecha_ingreso:
                errores.append(
                    "La fecha de salida no puede ser anterior al ingreso."
                )

    if not entry.actual.data:
        if not entry.motivo.data:
            errores.append("El motivo de salida es obligatorio.")

        if not fecha_salida:
            errores.append("La fecha de salida es obligatoria.")

    return errores
     

def validar_cursos(entry):


        errores= []

        if not entry.nombre.data:
            errores.append(
                "El nombre del curso es obligatorio."
            )

        if not entry.institucion.data:
            errores.append(
                "La institución es obligatoria."
            )

        return errores     
def validar_referencias(entry):
    
        
        errores= []

        if not entry.nombres.data:
            errores.append(
                "El nombre de la referencia es obligatorio."
            )

        if not entry.apellidos.data:
            errores.append(
                "Los apellidos de la referencia son obligatorios."
            )

        if not entry.empresa.data:
            errores.append(
                "La empresa es obligatoria."
            )

        if not entry.autoriza.data:
                errores.append(
                    "La autorización es obligatoria."    
                )
        return errores     
    
def validar_referencias_personales(entry):

    errores = []

    if not entry.nombres.data:
        errores.append(
            "El nombre de la referencia personal es obligatorio."
        )

    if not entry.apellidos.data:
        errores.append(
            "Los apellidos de la referencia personal son obligatorios."
        )

    if not entry.parentesco.data:
        errores.append(
            "El parentesco es obligatorio."
        )

    if not entry.telefono.data:
        errores.append(
            "El teléfono de la referencia personal es obligatorio."
        )

    return errores

def validar_discapacidades(entry):
        errores= []

        if not entry.categoria.data:
            errores.append(
                "La categoría de discapacidad es obligatoria."
            )
        return errores   
