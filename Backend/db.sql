-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               5.7.25-0ubuntu0.18.04.2 - (Ubuntu)
-- Server OS:                    Linux
-- HeidiSQL Version:             10.1.0.5464
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Dumping database structure for cs3243
CREATE DATABASE IF NOT EXISTS `cs3243` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `cs3243`;

-- Dumping structure for table cs3243.results
CREATE TABLE IF NOT EXISTS `results` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `iteration` int(11) NOT NULL,
  `weight` int(11) NOT NULL,
  `test_value` decimal(10,4) NOT NULL,
  `result` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `iteration_weight` (`iteration`,`weight`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1;

-- Dumping data for table cs3243.results: ~0 rows (approximately)
/*!40000 ALTER TABLE `results` DISABLE KEYS */;
/*!40000 ALTER TABLE `results` ENABLE KEYS */;

-- Dumping structure for table cs3243.weights
CREATE TABLE IF NOT EXISTS `weights` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `iteration` int(11) NOT NULL,
  `weight` int(11) NOT NULL,
  `val` decimal(10,4) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `iteration_weight` (`iteration`,`weight`),
  KEY `iteration` (`iteration`,`weight`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=latin1;

-- Dumping data for table cs3243.weights: ~16 rows (approximately)
/*!40000 ALTER TABLE `weights` DISABLE KEYS */;
REPLACE INTO `weights` (`id`, `iteration`, `weight`, `val`) VALUES
	(1, 1, 0, 0.3200),
	(2, 1, 1, 0.7900),
	(3, 1, 2, 0.4500),
	(4, 1, 3, 0.6800),
	(5, 0, 4, 0.1300),
	(6, 0, 5, 0.0600),
	(7, 0, 6, 0.2600),
	(8, 0, 7, 0.7300),
	(9, 0, 8, 0.5900),
	(10, 0, 9, 0.7700),
	(11, 0, 10, 0.6500),
	(12, 0, 11, 0.7800),
	(13, 0, 0, 0.9000),
	(14, 0, 1, 0.7100),
	(15, 0, 3, 0.3900),
	(16, 0, 2, 0.7700),
	(21, 1, 4, 0.1300),
	(22, 1, 5, 0.0200);
/*!40000 ALTER TABLE `weights` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
