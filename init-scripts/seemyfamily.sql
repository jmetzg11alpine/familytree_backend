-- MySQL dump 10.13  Distrib 8.0.32, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: seemyfamily
-- ------------------------------------------------------
-- Server version	8.0.35-0ubuntu0.23.04.1

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
-- Table structure for table `history`
--

DROP TABLE IF EXISTS `history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `username` varchar(100) DEFAULT NULL,
  `action` varchar(100) DEFAULT NULL,
  `recipient` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_history_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `history`
--

LOCK TABLES `history` WRITE;
/*!40000 ALTER TABLE `history` DISABLE KEYS */;
INSERT INTO `history` VALUES (1,'2024-01-18 04:16:44','Jesse Metzger','Project Started','General');
/*!40000 ALTER TABLE `history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `person`
--

DROP TABLE IF EXISTS `person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `person` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` date DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `x` int DEFAULT NULL,
  `y` int DEFAULT NULL,
  `birth` date DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `parents` varchar(40) DEFAULT NULL,
  `spouse` varchar(40) DEFAULT NULL,
  `siblings` varchar(40) DEFAULT NULL,
  `children` varchar(40) DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `lng` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ix_person_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `person`
--

LOCK TABLES `person` WRITE;
/*!40000 ALTER TABLE `person` DISABLE KEYS */;
INSERT INTO `person` VALUES (1,'2024-01-18','Jesse Metzger',20,21,'1989-01-17','Nashville ,TN','3,5','2','4',NULL,36.16,-86.78),(2,'2024-01-18','Ellina Metzger',21,21,'1991-05-05','Nashville, TN','7,8','1','6',NULL,36.16,-86.78),(3,'2024-01-18','Helen Metzger',18,19,'1959-01-01','San Diego, CA',NULL,'5',NULL,'1,4',32.83,-116.76),(4,'2024-01-18','Jennifer Metzger',16,21,'1991-11-15','Las Vegas, NV','3,5',NULL,'1',NULL,36.17,-115.13),(5,'2024-01-18','James Metzger',17,19,'1957-04-01','San Diego, CA',NULL,'3',NULL,'1,4',32.83,-116.76),(6,'2024-01-18','Polina Volkova',25,21,'1996-01-16','Moscow, Russia','7,8',NULL,'2',NULL,55.75,37.61),(7,'2024-01-18','Anna Volkova',24,19,'1968-10-12','Moscow, Russia',NULL,'8',NULL,'2,6',55.75,37.61),(8,'2024-01-18','Yuriy Volkov',23,19,'1966-08-18','Moscow, Russia',NULL,'7',NULL,'2,6',55.75,37.61),(9,'2024-01-18','Mioyko Jones',19,17,'1910-02-02','San Diego',NULL,'10',NULL,'3',32.74,-116.99),(10,'2024-01-18','Howard Jones',20,17,'1910-04-04','San Diego',NULL,'9',NULL,'3',32.74,-116.99),(11,'2024-01-18','Дядя Гений',28,19,NULL,'Grodno, Belarus',NULL,'12','7','13,14',53.66,23.82),(12,'2024-01-18','Тетя Людмила',29,19,NULL,'Grodno, Belarus',NULL,'11',NULL,'13,14',53.66,23.82),(13,'2024-01-18','Julia',28,21,NULL,'Minsk, Belarus','11,12',NULL,'14',NULL,53.9,27.55),(14,'2024-01-18','Karina',30,21,NULL,'Krakow, Poland','11,12','15','13','16',50.06,19.94),(15,'2024-01-18','Sabastian',31,21,NULL,'Krakow, Poland',NULL,'14',NULL,'16',50.06,19.94),(16,'2024-01-18','Yanik',30,22,NULL,'Krakow, Poland',NULL,NULL,NULL,NULL,50.06,19.94),(17,'2024-01-18','James Metzger sr',16,17,NULL,NULL,NULL,'17',NULL,NULL,NULL,NULL),(18,'2024-01-18','Grandma Metzger',15,17,NULL,NULL,NULL,'17',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `person` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `photo`
--

DROP TABLE IF EXISTS `photo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `photo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `person_id` int DEFAULT NULL,
  `profile_photo` tinyint(1) DEFAULT NULL,
  `path` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_photo_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `photo`
--

LOCK TABLES `photo` WRITE;
/*!40000 ALTER TABLE `photo` DISABLE KEYS */;
/*!40000 ALTER TABLE `photo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_user_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Helen Metzger','mother'),(2,'Jesse Metzger','jesse'),(3,'Jennifer Metzger','sister'),(4,'Ellina Metzger','wife');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `visitor`
--

DROP TABLE IF EXISTS `visitor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `visitor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ip_address` varchar(225) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_visitor_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `visitor`
--

LOCK TABLES `visitor` WRITE;
/*!40000 ALTER TABLE `visitor` DISABLE KEYS */;
/*!40000 ALTER TABLE `visitor` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-01-18  4:23:34
