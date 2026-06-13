-- Схема базы данных для эмулятора EVE Online
-- Адаптировано на основе дампов EVEmu

-- Таблица аккаунтов (из вашего account.sql)
-- Таблица аккаунтов
-- Note: email НЕ используется для входа, только для коммуникации
-- Один email может принадлежать множеству аккаунтов
CREATE TABLE IF NOT EXISTS `account` (
  `accountID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `clientID` int(10) unsigned NOT NULL DEFAULT 0,
  `accountName` varchar(43) NOT NULL DEFAULT '',      -- ЛОГИН для входа
  `email` varchar(60) DEFAULT NULL,                  -- НЕ для входа! Только для восстановления
  `password` varchar(43) NOT NULL DEFAULT '',        -- Пароль (в идеале хеш)
  `hash` tinyblob DEFAULT NULL,                      -- Хеш пароля (если используется)
  `type` tinyint(3) unsigned NOT NULL DEFAULT 23,
  `role` bigint(20) unsigned NOT NULL DEFAULT 0,
  `online` tinyint(1) NOT NULL DEFAULT 0,
  `banned` tinyint(1) NOT NULL DEFAULT 0,
  `logonCount` int(10) unsigned NOT NULL DEFAULT 0,
  `lastLogin` timestamp NULL DEFAULT NULL,
  `session_sid` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`accountID`),
  UNIQUE KEY `accountName` (`accountName`),          -- Логин должен быть уникальным
  KEY `idx_email` (`email`)                          -- Индекс для поиска по email
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Таблица персонажей (из вашего chrCharacters.sql, упрощена)
CREATE TABLE IF NOT EXISTS `chrCharacters` (
  `characterID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `accountID` int(10) unsigned DEFAULT NULL,
  `characterName` varchar(30) NOT NULL DEFAULT '<no name>',
  `title` varchar(100) NOT NULL DEFAULT '<no title>',
  `description` varchar(300) NOT NULL DEFAULT '<no description>',
  `typeID` int(6) NOT NULL DEFAULT 0,
  `gender` tinyint(1) NOT NULL DEFAULT 0,
  `balance` double NOT NULL DEFAULT 0,
  `aurBalance` double NOT NULL DEFAULT 0,
  `securityRating` float NOT NULL DEFAULT 0,
  `locationID` int(10) NOT NULL DEFAULT 0,
  `skillPoints` bigint(20) NOT NULL DEFAULT 0,
  `corporationID` int(10) unsigned NOT NULL DEFAULT 0,
  `bloodlineID` tinyint(3) unsigned NOT NULL DEFAULT 0,
  `raceID` tinyint(3) unsigned NOT NULL DEFAULT 0,
  `ancestryID` int(10) unsigned NOT NULL DEFAULT 0,
  `createDateTime` bigint(20) NOT NULL DEFAULT 0,
  `deletePrepareDateTime` bigint(20) unsigned DEFAULT 0,
  PRIMARY KEY (`characterID`),
  KEY `FK_CHARACTER__ACCOUNTS` (`accountID`),
  CONSTRAINT `FK_CHARACTER__ACCOUNTS` FOREIGN KEY (`accountID`) REFERENCES `account` (`accountID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Логи аутентификации (новая таблица)
CREATE TABLE IF NOT EXISTS `auth_logs` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(43) NOT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `success` tinyint(1) NOT NULL DEFAULT 0,
  `reason` varchar(200) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_username` (`username`),
  KEY `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Тестовые данные
INSERT INTO `account` (`accountID`, `accountName`, `password`, `email`, `type`, `role`) VALUES
(1, 'test', 'test', 'test@example.com', 23, 0),
(2, 'admin', 'admin', 'admin@example.com', 23, 1);

INSERT INTO `chrCharacters` (`characterID`, `accountID`, `characterName`, `typeID`, `gender`, `balance`, `corporationID`, `bloodlineID`, `raceID`, `ancestryID`) VALUES
(90000001, 1, 'Test Pilot', 1383, 0, 1000000.00, 1000169, 1, 1, 1),
(90000002, 1, 'Test Alt', 1383, 1, 500000.00, 1000169, 2, 2, 2);