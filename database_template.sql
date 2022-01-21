CREATE TABLE IF NOT EXISTS `guild_config` (
  `guild_id` bigint(20) NOT NULL,
  `exp_active` bit(1) DEFAULT NULL,
  `exp_levelup_channel` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`guild_id`)
);

CREATE TABLE IF NOT EXISTS `reminders` (
  `due_datetime` datetime NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `content` text NOT NULL
);

CREATE TABLE IF NOT EXISTS `user_exp` (
  `guild_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `exp` bigint(20) NOT NULL DEFAULT 0,
  PRIMARY KEY (`guild_id`,`user_id`)
);

CREATE TABLE IF NOT EXISTS `user_exp_card` (
  `user_id` bigint(20) NOT NULL,
  `red` tinyint(3) unsigned NOT NULL,
  `green` tinyint(3) unsigned NOT NULL,
  `blue` tinyint(3) unsigned NOT NULL,
  PRIMARY KEY (`user_id`)
);
