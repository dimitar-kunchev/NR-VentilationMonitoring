CREATE TABLE `sensors_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ts` datetime DEFAULT NULL,
  `sensor` int(11) NOT NULL,
  `temperature` float DEFAULT NULL,
  `rpm` float DEFAULT NULL,
  `airflow` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ts` (`ts`),
  KEY `sensor` (`sensor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `sensors_data_5min` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ts` datetime DEFAULT NULL,
  `sensor` int(11) NOT NULL,
  `temperature` float DEFAULT NULL,
  `rpm` float DEFAULT NULL,
  `airflow` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ts` (`ts`),
  KEY `sensor` (`sensor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `sensors_data_1hour` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ts` datetime DEFAULT NULL,
  `sensor` int(11) NOT NULL,
  `temperature` float DEFAULT NULL,
  `rpm` float DEFAULT NULL,
  `airflow` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ts` (`ts`),
  KEY `sensor` (`sensor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `sensors_data_1day` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ts` datetime DEFAULT NULL,
  `sensor` int(11) NOT NULL,
  `temperature` float DEFAULT NULL,
  `rpm` float DEFAULT NULL,
  `airflow` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ts` (`ts`),
  KEY `sensor` (`sensor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;