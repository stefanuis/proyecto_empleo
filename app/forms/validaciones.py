
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
    if not entry.email.data:
            errores.append(
            "El correo es obligatorio."
        )
   

    return errores

    
def validar_contacto(entry):

    errores = []

    if not entry.nombres.data:
        errores.append(
            "El nombre del contacto es obligatorio."
        )

    if not entry.apellidos.data:
        errores.append(
            "Los apellidos del contacto son obligatorios."
        )

    if not entry.parentesco.data:
        errores.append(
            "El parentesco es obligatorio."
        )

    if not entry.tel.data:
            errores.append(
                "El teléfono es obligatorio."


            )
    return errores


def validar_familiar(entry):

    errores = []

    if not entry.personas_casa.data:
        errores.append(
            "El número de personas en casa es obligatorio."
        )

    if not entry.dependen_eco.data:
        errores.append(
            "El número de dependientes económicos es obligatorio."
        )

    return errores
     
     
def validar_academica(entry):

        errores= []
        
        if not entry.nivel.data:
            errores.append(
                "El nivel académico es obligatorio."
            )

        if not entry.estado.data:
            errores.append(
                "El estado académico es obligatorio."
            )

        if not entry.titulo.data:
            errores.append(
                "El título es obligatorio."
            )

        if not entry.institucion.data:
                errores.append(
                    "La institución es obligatoria."
                )
        if not entry.mes_finalizacion.data:
                errores.append(
                  "El mes de finalización es obligatorio."
                )
        if not entry.anno_finalizacion.data:
                errores.append(
                "El año de finalización es obligatorio."
                )

        return errores       
        
            
def validar_experiencia(entry):
        errores= []
        
        if not entry.entidad.data:
            errores.append(
                "El nombre de la entidad/empresa es obligatorio."
            )

        if not entry.area.data:
            errores.append(
                "El área de trabajo es obligatoria."
            )

        if not entry.cargo.data:
            errores.append(
                "El cargo es obligatorio."
            )

        if not entry.motivo.data:
                errores.append(
                    "El motivo de salida es obligatorio."
                )
        if not entry.fecha_ingreso.data:
                errores.append(
                  "La fecha de ingreso es obligatoria."
                )
        if not entry.fecha_salida .data:
                errores.append(
                "La fecha de salida es obligatoria."
                )

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
def validar_competencias(entry):

        errores= []

        if not entry.competencia.data:
            errores.append(
                "La competencia es obligatoria."
            )

        if not entry.nivel .data:
            errores.append(
                "El nivel es obligatorio."
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
    

def validar_discapacidades(entry):
        errores= []

        if not entry.categoria.data:
            errores.append(
                "La categoría de discapacidad es obligatoria."
            )
        return errores   

