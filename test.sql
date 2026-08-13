-- demogra01.vw_persona_completa source

CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `demogra01`.`vw_persona_completa` AS
select
    `p`.`id_persona` AS `id_persona`,
    `p`.`documento` AS `documento`,
    `p`.`nombres` AS `nombres`,
    `p`.`f_nacimiento` AS `f_nacimiento`,
    `p`.`f_ingreso` AS `f_ingreso`,
    `p`.`estado` AS `persona_activa`,
    `pe`.`sexo` AS `sexo`,
    `pe`.`raza` AS `raza`,
    `pe`.`estado_civil` AS `estado_civil`,
    `pe`.`edad` AS `edad`,
    `pe`.`escolaridad` AS `escolaridad`,
    `pe`.`fuma` AS `fuma`,
    `pe`.`licor` AS `licor`,
    `pe`.`SPA` AS `SPA`,
    `pe`.`movilidad` AS `movilidad`,
    `pe`.`ejercicio` AS `ejercicio`,
    `pe`.`discapacidad` AS `discapacidad`,
    `pe`.`cat_discapacidad` AS `cat_discapacidad`,
    `pe`.`cert_discapacidad` AS `cert_discapacidad`,
    `pe`.`victima_conflicto` AS `victima_conflicto`,
    `pe`.`mujer_victima` AS `mujer_victima`,
    `pe`.`telefono` AS `telefono`,
    `i`.`rango_edad` AS `rango_edad`,
    `i`.`rango_antiguedad` AS `rango_antiguedad`,
    `i`.`rango_ingresos` AS `rango_ingresos`,
    `i`.`ARL` AS `ARL`,
    `i`.`EPS` AS `EPS`,
    `i`.`AFP` AS `AFP`,
    `i`.`vinculacion` AS `vinculacion`,
    `l`.`antiguedad` AS `antiguedad`,
    `l`.`sede` AS `sede`,
    `l`.`ingresos` AS `ingresos`,
    `l`.`ocupacion` AS `ocupacion`,
    `l`.`area_trabajo` AS `area_trabajo`,
    `l`.`turno` AS `turno`,
    `r`.`lug_residencia` AS `lug_residencia`,
    `r`.`dir_residencia` AS `dir_residencia`,
    `r`.`estrato` AS `estrato`,
    `h`.`cab_familia` AS `cab_familia`,
    `h`.`num_hijos` AS `num_hijos`,
    `h`.`personas_hogar` AS `personas_hogar`,
    `h`.`personas_discapacidad` AS `personas_discapacidad`,
    `h`.`tipo_vivienda` AS `tipo_vivienda`,
    `h`.`caract_vivienda` AS `caract_vivienda`,
    `h`.`zona_vivienda` AS `zona_vivienda`,
    `h`.`otras_personas_cargo` AS `otras_personas_cargo`,
    `c`.`nombre_contacto` AS `nombre_contacto`,
    `c`.`tel_contacto` AS `tel_contacto`,
    `c`.`parentesco` AS `parentesco`
from
    ((((((`demogra01`.`tbl_persona` `p`
left join `demogra01`.`tbl_personal` `pe` on
    (`p`.`id_persona` = `pe`.`id_persona` and `pe`.`activo` = 1))
left join `demogra01`.`tbl_laboral` `l` on
    (`p`.`id_persona` = `l`.`id_persona` and `l`.`activo` = 1))
left join `demogra01`.`tbl_residencia` `r` on
    (`p`.`id_persona` = `r`.`id_persona` and `r`.`activo` = 1))
left join `demogra01`.`tbl_hogar` `h` on
    (`p`.`id_persona` = `h`.`id_persona` and `h`.`activo` = 1))
left join `demogra01`.`tbl_contacto` `c` on
    (`p`.`id_persona` = `c`.`id_persona` and `c`.`activo` = 1))
left join `demogra01`.`tbl_institucional` `i` on
    (`p`.`id_persona` = `i`.`id_persona` and `i`.`activo` = 1));