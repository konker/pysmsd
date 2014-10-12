/*
   db schema for pysmsd internal database, intended for use with sqlite3

   TODO:
       - do in_messages and out_messages need to be in seperate tables?
*/

DROP TABLE IF EXISTS `clients`;
CREATE TABLE `clients` (
    `id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,

    -- basic text info --
    `name` varchar(32) NOT NULL,
    `password` varchar(128) NOT NULL, -- should be bcrypt hashed

    `created` datetime NOT NULL,
    `updated` timestamp NOT NULL,

    CONSTRAINT `idx_name` UNIQUE(`name`)
);
-- password default is 'pysmsd'
INSERT INTO `clients` (`id`, `name`, `password`, `created`, `updated`)
    VALUES(0, 'SYSTEM', '$2a$12$X5HfXpRYLXaNUR6gOsfkaO4jNZopZBuSBoFHiSmoGMMoiikH69u2C', datetime('now'), datetime('now'));
INSERT INTO `clients` (`id`, `name`, `password`, `created`, `updated`)
    VALUES(1, 'pysmsd_test', '$2a$12$X5HfXpRYLXaNUR6gOsfkaO4jNZopZBuSBoFHiSmoGMMoiikH69u2C', datetime('now'), datetime('now'));

DROP TABLE IF EXISTS `in_messages`;
CREATE TABLE `in_messages` (
    `id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,

    -- basic text info --
    `number` varchar(32) NOT NULL,
    `Text` varchar(255) NOT NULL,
    `Length` integer NOT NULL,
    `Coding` varchar(32) DEFAULT 'Default_No_Compression',
    `Datetime` datetime NOT NULL, -- this is the received date

    `Keyword` varchar(255) DEFAULT NULL,
    `Rest` varchar(255) DEFAULT NULL,

    -- internal data --
    `marked` datetime DEFAULT NULL,
    `marked_by` integer DEFAULT NULL, -- FK -> client.id

    `created` datetime NOT NULL,
    `updated` timestamp NOT NULL
);



DROP TABLE IF EXISTS `out_messages`;
CREATE TABLE `out_messages` (
    `id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,

    -- basic text info --
    `number` varchar(32) NOT NULL,
    `Text` varchar(255) NOT NULL,
    `Length` integer NOT NULL,
    `Coding` varchar(32) DEFAULT NULL,
    `Datetime` datetime DEFAULT NULL, -- this will be the sent date

    -- internal data --
    `queued` datetime DEFAULT NULL,
    `queued_by` integer NOT NULL, -- FK -> client.id

    `created` datetime NOT NULL,
    `updated` timestamp NOT NULL
);

