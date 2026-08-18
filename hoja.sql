-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: hojas
-- ------------------------------------------------------
-- Server version	5.5.5-10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `tbl_competencias`
--

DROP TABLE IF EXISTS `tbl_competencias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_competencias` (
  `id_usuario` int(11) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `competencia` varchar(150) DEFAULT NULL,
  `nivel` varchar(50) DEFAULT NULL,
  `experiencia` int(11) DEFAULT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_competencias`
--

LOCK TABLES `tbl_competencias` WRITE;
/*!40000 ALTER TABLE `tbl_competencias` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_competencias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_contacto`
--

DROP TABLE IF EXISTS `tbl_contacto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_contacto` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `nombre` varchar(100) DEFAULT NULL,
  `apellido` varchar(100) DEFAULT NULL,
  `parentesco` varchar(20) DEFAULT NULL,
  `tel` varchar(20) DEFAULT NULL,
  `num_residencia` varchar(50) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `fk_contacto_usuario` (`id_usuario`),
  CONSTRAINT `fk_contacto_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `tbl_usuario` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_contacto`
--

LOCK TABLES `tbl_contacto` WRITE;
/*!40000 ALTER TABLE `tbl_contacto` DISABLE KEYS */;
INSERT INTO `tbl_contacto` VALUES (2,45,'enidia','lopez','madre','323123','231231|',NULL);
/*!40000 ALTER TABLE `tbl_contacto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_cursos`
--

DROP TABLE IF EXISTS `tbl_cursos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_cursos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `nombre` varchar(150) DEFAULT NULL,
  `institucion` varchar(150) DEFAULT NULL,
  `area` varchar(150) DEFAULT NULL,
  `horas` int(11) DEFAULT NULL,
  `fecha_realizacion` datetime DEFAULT NULL,
  `certificado` tinyint(4) DEFAULT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_cursos`
--

LOCK TABLES `tbl_cursos` WRITE;
/*!40000 ALTER TABLE `tbl_cursos` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_cursos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_docs`
--

DROP TABLE IF EXISTS `tbl_docs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_docs` (
  `id_usuario` int(11) DEFAULT NULL,
  `id_documento` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) DEFAULT NULL,
  `ruta` varchar(254) DEFAULT NULL,
  `tipo` varchar(50) DEFAULT NULL,
  `actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id_documento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_docs`
--

LOCK TABLES `tbl_docs` WRITE;
/*!40000 ALTER TABLE `tbl_docs` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_docs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_experiencia`
--

DROP TABLE IF EXISTS `tbl_experiencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_experiencia` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `entidad` varchar(100) DEFAULT NULL,
  `area` varchar(100) DEFAULT NULL,
  `cargo` varchar(100) DEFAULT NULL,
  `actual` tinyint(1) DEFAULT NULL,
  `motivo` varchar(100) DEFAULT NULL,
  `otro` varchar(250) DEFAULT NULL,
  `fecha_ingreso` datetime DEFAULT NULL,
  `fecha_salida` datetime DEFAULT NULL,
  `pais` varchar(50) DEFAULT NULL,
  `departamento` varchar(50) DEFAULT NULL,
  `municipio` varchar(50) DEFAULT NULL,
  `funciones_realizadas` varchar(500) DEFAULT NULL,
  `ruta_soporte` varchar(240) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `fk_experiencia_usuario` (`id_usuario`),
  CONSTRAINT `fk_experiencia_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `tbl_usuario` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_experiencia`
--

LOCK TABLES `tbl_experiencia` WRITE;
/*!40000 ALTER TABLE `tbl_experiencia` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_experiencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_info_academica`
--

DROP TABLE IF EXISTS `tbl_info_academica`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_info_academica` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `tipo` varchar(30) DEFAULT NULL,
  `nivel` varchar(100) DEFAULT NULL,
  `estado` varchar(30) DEFAULT NULL,
  `periodos_cursados` int(11) DEFAULT NULL,
  `area` varchar(30) DEFAULT NULL,
  `titulo` varchar(100) DEFAULT NULL,
  `institucion` varchar(100) DEFAULT NULL,
  `pais_institucion` varchar(50) DEFAULT NULL,
  `convalidacion` tinyint(1) DEFAULT NULL,
  `mes_finalizacion` int(11) DEFAULT NULL,
  `anno_finalizacion` int(11) DEFAULT NULL,
  `ruta_soporte` varchar(240) DEFAULT NULL,
  `intensidad_horaria` int(11) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `fk_info_academica_usuario` (`id_usuario`),
  CONSTRAINT `fk_info_academica_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `tbl_usuario` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_info_academica`
--

LOCK TABLES `tbl_info_academica` WRITE;
/*!40000 ALTER TABLE `tbl_info_academica` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_info_academica` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_info_discapacidades`
--

DROP TABLE IF EXISTS `tbl_info_discapacidades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_info_discapacidades` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `descripcion` varchar(250) DEFAULT NULL,
  `ruta_certificado` varchar(240) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `fk_info_discapacidad_usuario` (`id_usuario`),
  CONSTRAINT `fk_info_discapacidad_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `tbl_usuario` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_info_discapacidades`
--

LOCK TABLES `tbl_info_discapacidades` WRITE;
/*!40000 ALTER TABLE `tbl_info_discapacidades` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_info_discapacidades` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_info_familiar`
--

DROP TABLE IF EXISTS `tbl_info_familiar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_info_familiar` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `personas_casa` int(11) NOT NULL,
  `dependen_eco` int(11) DEFAULT NULL,
  `fecha_realizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_info_familiar_usuario` (`id_usuario`),
  KEY `fk_info_familiar_contacto` (`personas_casa`),
  CONSTRAINT `fk_info_familiar_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `tbl_usuario` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_info_familiar`
--

LOCK TABLES `tbl_info_familiar` WRITE;
/*!40000 ALTER TABLE `tbl_info_familiar` DISABLE KEYS */;
INSERT INTO `tbl_info_familiar` VALUES (2,45,2,4,NULL);
/*!40000 ALTER TABLE `tbl_info_familiar` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_info_personal`
--

DROP TABLE IF EXISTS `tbl_info_personal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_info_personal` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `nombres` varchar(100) DEFAULT NULL,
  `apellidos` varchar(100) DEFAULT NULL,
  `tipo_doc` varchar(10) DEFAULT NULL,
  `num_doc` varchar(30) DEFAULT NULL,
  `fecha_exp_doc` datetime DEFAULT NULL,
  `fecha_nacimiento` datetime DEFAULT NULL,
  `genero` varchar(20) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `num_cel` varchar(20) DEFAULT NULL,
  `num_cel_dos` varchar(20) DEFAULT NULL,
  `grupo_etnico` varchar(100) DEFAULT NULL,
  `pais` varchar(50) DEFAULT NULL,
  `departamento` varchar(50) DEFAULT NULL,
  `municipio` varchar(50) DEFAULT NULL,
  `barrio` varchar(50) DEFAULT NULL,
  `direccion` varchar(100) DEFAULT NULL,
  `nacionalidad` varchar(50) DEFAULT NULL,
  `vive_rural` varchar(10) DEFAULT NULL,
  `estado_civil` varchar(20) DEFAULT NULL,
  `personas_cargo` int(11) DEFAULT NULL,
  `ultima_actualizacion` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `ruta_foto_perfil` varchar(240) DEFAULT NULL,
  `ruta_foto_doc` varchar(240) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_info_personal_usuario` (`id_usuario`),
  CONSTRAINT `fk_info_personal_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `tbl_usuario` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_info_personal`
--

LOCK TABLES `tbl_info_personal` WRITE;
/*!40000 ALTER TABLE `tbl_info_personal` DISABLE KEYS */;
INSERT INTO `tbl_info_personal` VALUES (2,43,'victor ','Mejia','CC','10171','2026-02-04 00:00:00',NULL,'','','','','',NULL,'','','','','','','',NULL,'2026-08-03 10:16:54',NULL,NULL),(3,45,'stefany','lopez correa','CC','1007546692','2020-08-14 00:00:00','2002-07-27 00:00:00','Femenino','stefanuis09@gmail.com','3017326482','33242343','Otro',NULL,'antioquia','turbo','pueblo nievo','cra49#54a-16','colombiana','SI','Casado',2,NULL,NULL,NULL);
/*!40000 ALTER TABLE `tbl_info_personal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_otros_docs`
--

DROP TABLE IF EXISTS `tbl_otros_docs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_otros_docs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `nombre` varchar(100) DEFAULT NULL,
  `ruta_soporte` varchar(240) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `fk_otros_docs_usuario` (`id_usuario`),
  CONSTRAINT `fk_otros_docs_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `tbl_usuario` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_otros_docs`
--

LOCK TABLES `tbl_otros_docs` WRITE;
/*!40000 ALTER TABLE `tbl_otros_docs` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_otros_docs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_postulacion`
--

DROP TABLE IF EXISTS `tbl_postulacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_postulacion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `id_vacante` int(11) NOT NULL,
  `estado` varchar(30) DEFAULT 'postulado',
  `notas_reclutador` text DEFAULT NULL,
  `fecha_postulacion` datetime DEFAULT current_timestamp(),
  `fecha_actualizacion` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_usuario_vacante` (`id_usuario`,`id_vacante`),
  KEY `fk_postulacion_usuario` (`id_usuario`),
  KEY `fk_postulacion_vacante` (`id_vacante`),
  CONSTRAINT `fk_postulacion_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `tbl_usuario` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_postulacion_vacante` FOREIGN KEY (`id_vacante`) REFERENCES `tbl_vacante` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_postulacion`
--

LOCK TABLES `tbl_postulacion` WRITE;
/*!40000 ALTER TABLE `tbl_postulacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_postulacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_referencias`
--

DROP TABLE IF EXISTS `tbl_referencias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_referencias` (
  `id_usuario` int(11) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombres` varchar(100) DEFAULT NULL,
  `apellidos` varchar(100) DEFAULT NULL,
  `parentesco` varchar(30) DEFAULT NULL,
  `empresa` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `ciudad` varchar(30) DEFAULT NULL,
  `autoriza` varchar(10) DEFAULT NULL,
  `actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_referencias`
--

LOCK TABLES `tbl_referencias` WRITE;
/*!40000 ALTER TABLE `tbl_referencias` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_referencias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_usuario`
--

DROP TABLE IF EXISTS `tbl_usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_usuario` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombres` varchar(100) DEFAULT NULL,
  `apellidos` varchar(100) DEFAULT NULL,
  `correo` varchar(150) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `clave_hash` varchar(255) NOT NULL,
  `esta_activa` tinyint(1) DEFAULT 1,
  `esta_verificada` tinyint(1) DEFAULT 0,
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp(),
  `fecha_actualizacion` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `ultimo_login` datetime DEFAULT NULL,
  `rol` varchar(50) DEFAULT NULL,
  `token` varchar(255) DEFAULT NULL,
  `token_envio` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `correo` (`correo`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_usuario`
--

LOCK TABLES `tbl_usuario` WRITE;
/*!40000 ALTER TABLE `tbl_usuario` DISABLE KEYS */;
INSERT INTO `tbl_usuario` VALUES (3,'Admin','Principal','admin@clipan.com','3001234567','scrypt:32768:8:1$hO3hMXZ9ANMsIcgB$212a8e7fe9f859d9d525824e663344dde6f83b5e13cf3445a5766405590a1f016d44fd30260a84db3cba8058b1851a92f87a1e93444aacbb53d0f0bcd401c225',1,1,'2026-06-12 15:28:33','2026-08-06 09:32:57','2026-08-06 09:32:57','admin',NULL,NULL),(23,'Guilermo','Velez','guilleve17@gmail.com','3117210687','scrypt:32768:8:1$BoMuMZfXTXiNogiu$d68e630182d46dc8f7d0643182221f13e1e57e92047d95efd707533ebf064add725ca85d6e651f4b8258a770dbc1d3adb355a9f72796874b585d3ae2ab59b378',0,0,'2026-06-25 15:09:20','2026-06-25 15:09:20',NULL,'usuario','XUVJCMlnjHOmkTfQTObxo6nKNderFVblj4VPsbgDUYY','2026-06-25 15:09:20'),(36,'Test','Demo','duvan.graciano@clinicapanamericana.co','3128041111','scrypt:32768:8:1$QgdrXM75CiEbN1lT$f850cf932a73a5fa964eeeb082c40277341222e60953839c544e4d51dbddd006de8c2c669a619ca56e0bcc765a85aba65938d0c9f71fe2b8409ccb2b76402f6e',1,1,'2026-06-26 10:08:35','2026-06-26 10:10:11','2026-06-26 15:10:11','usuario',NULL,NULL),(37,'JUAN','ZULETA','jzuleta21@hotmail.com','3104672972','scrypt:32768:8:1$XNZRA89YY2aakDXj$42d97d6fcd28ab813d7db8e1d298c0c71e663d613a6da46e89d5b30f8d4aacadb669f332cac45e65d5febd94c249f7866066e0a776f3fbce49091b2da65ac7e0',1,1,'2026-06-26 10:08:38','2026-06-26 10:09:01','2026-06-26 15:09:01','usuario',NULL,NULL),(41,'paola','sierra','paola15flower@gmail.com','3052206689','scrypt:32768:8:1$vOQeSCNzUMJLNs2P$522c4a105c58083485bdb4f9bc523c4cef7ee50d28fbc9c7d776f74a3844eb0dd7d37951d42e601a6353f9eeb59750035f0bf1328c5667cf0ceece858a214903',0,0,'2026-07-09 08:58:14','2026-07-09 08:58:14',NULL,'usuario','2EiVfTJR5GF8TodJcwYhHV4x-XuRt_410XV2SQjnSXI','2026-07-09 08:58:14'),(42,'LUZ STELLA','MOSQUERA RENTERIA','LUCESMR@GMAIL.COM','3148810418','scrypt:32768:8:1$Bij9eQdD1Qo8lcTR$99317cb984e423f3a6d9a22ced7549d6158dbf9ac3d37394397f9bd00fdd2e8879066d9ce82c106ed8bfc544b7aa248c511971a3ee8afb8610b336c494a445c5',1,1,'2026-07-09 09:10:13','2026-07-09 09:21:16','2026-07-09 09:21:16','usuario',NULL,NULL),(43,'Victor Armando','Mejia Betancur','victormejiabetancur@gmail.com','3147085505','scrypt:32768:8:1$JyvcI5EcqMSIFf03$effe1cdaed36dd03c042334d1874a8bae8bbc3f4c125646a08d4e7deeb5cbc6900f3ff5b867adffdf975d6dee9791ad2ea08a6514cf931b6dc05911effd3dea2',1,1,'2026-08-03 10:08:00','2026-08-03 10:09:50','2026-08-03 10:09:50','usuario',NULL,NULL),(44,'stefany','lopez','stefanuis09@gmail.com','3017326382','scrypt:32768:8:1$5NVrYxdfewud7u9n$9dd705d43615a73ec728808c0ebb156f9359b6fee8b6c84204780de62bc854496378e42a6e250c12be3beb5192287a4006c756cd71a7b79bb784416636db769e',1,1,'2026-08-04 07:36:23','2026-08-06 16:30:22','2026-08-06 16:30:22','usuario',NULL,NULL),(45,'Laura','Gómez','laura.gomez@ejemplo.com','3009876543','scrypt:32768:8:1$HhpoEU3SHH1aYmVc$9c25fa3c1969fa95fdc60633b454c828d2a00fd1ccbeea389b6bb0ec51c40b060427f00c275eb7d1b4dd39f2746d197866f2dd0aa4e19be5df728ef528230e92',1,1,'2026-08-15 17:21:52','2026-08-18 00:11:02','2026-08-18 00:11:02','usuario',NULL,NULL),(46,'maria sanchez','lopez correa','rosilareina0@gmail.com','311 724842','scrypt:32768:8:1$s3856vbVv3Qrh92n$ae6c9164529f67a82a64c516344a93c7a705b70372ee584a6943bf27cfd948ea7d25e2dd74251744d7347c027831f05600fac52b05446ab7b179311042012826',0,0,'2026-08-15 12:31:49','2026-08-15 12:31:49',NULL,'usuario','anpZ88YnA0hjCaaDZ_QungWVP9swH3SzRKq1cz3Ep-w','2026-08-15 12:31:49');
/*!40000 ALTER TABLE `tbl_usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_vacante`
--

DROP TABLE IF EXISTS `tbl_vacante`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_vacante` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `titulo` varchar(150) NOT NULL,
  `area` varchar(100) DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  `requisitos` text DEFAULT NULL,
  `salario` varchar(50) DEFAULT NULL,
  `tipo_contrato` varchar(50) DEFAULT 'Término fijo 6 meses',
  `sede` varchar(100) DEFAULT NULL,
  `estado` varchar(20) DEFAULT 'abierta',
  `fecha_publicacion` datetime DEFAULT current_timestamp(),
  `fecha_cierre` datetime DEFAULT NULL,
  `id_usuario_creador` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_vacante_admin` (`id_usuario_creador`),
  CONSTRAINT `fk_vacante_admin` FOREIGN KEY (`id_usuario_creador`) REFERENCES `tbl_usuario` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_vacante`
--

LOCK TABLES `tbl_vacante` WRITE;
/*!40000 ALTER TABLE `tbl_vacante` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_vacante` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'hojas'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-18  4:26:02
