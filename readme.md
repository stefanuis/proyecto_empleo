##Fase 1 — Hoja de vida como wizard secuencial

Reemplazar el menú plano de "Mi Perfil" por un flujo guiado.

Datos Personales
Contacto
Perfil Profesional
Experiencia Laboral
Formación Académica
Cursos
Idiomas
Competencias
Referencias
Documentos

 Ruta única parametrizada (ej. /perfil/paso/<n>) que renderiza el formulario correspondiente
 Guardar en BD qué pasos completó cada usuario, para pintar la barra de progreso (● ● ● ○ ○ ○ ○ ○ ○ ○)
 Botones "Anterior" / "Guardar y continuar"
 Pantalla final al completar el paso 10: confirmación + accesos directos a "Ver mi hoja de vida" y "Ver vacantes abiertas"

##Fase 2 — Vista previa de hoja de vida (CV renderizado)
 Ruta /mi-hoja-de-vida que consulta todas las tablas del usuario (datos personales, listas de experiencia, formación, cursos, competencias, referencias, documentos)
 Plantilla mi_cv.html que renderiza todo en formato CV de lectura
 Botón "Descargar PDF" con WeasyPrint (o alternativa si falla la instalación en Windows)

###Fase 3 — Vacantes (lado candidato)
 Listado /vacantes: solo vacantes con estado='abierta', con filtro por área
 Detalle de vacante /vacantes/<id>
 Botón "Postularme" → valida que no se haya postulado ya a esa vacante (UNIQUE en BD + chequeo en la vista)
 (Opcional) bloquear postulación si el perfil está incompleto
 "Mis postulaciones": listado con JOIN entre tbl_postulacion y tbl_vacante, mostrando estado con color (postulado, en revisión, entrevista, rechazado, contratado)

####Fase 4 — Pulido (después de que el flujo básico funcione)
 Indicador de secciones completas/pendientes en el perfil del candidato
 Validación de perfil mínimo completo antes de dejar postularse