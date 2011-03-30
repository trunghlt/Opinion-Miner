CREATE TABLE IF NOT EXISTS `svm_features` (
  `id` int(10) unsigned NOT NULL,
  `name` varchar(60) NOT NULL,
  `negative` double default NULL,
  `neutral` double default NULL,
  `positive` double default NULL,
  `class_0` double NOT NULL,
  `class_1` double default NULL,
  `class_2` double default NULL,
  `class_3` double default NULL,
  `class_4` double default NULL,
  `class_5` double default NULL,
  PRIMARY KEY  (`id`),
  KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
