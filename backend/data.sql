-- 文章表
CREATE TABLE `articles` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `unique_id` VARCHAR(100) NOT NULL COMMENT '文章唯一标识',
  `url` VARCHAR(500) NOT NULL COMMENT '文章URL',
  `title` VARCHAR(200) NOT NULL COMMENT '文章标题',
  `digest` TEXT COMMENT '文章摘要',
  `pub_time` BIGINT COMMENT '发布时间戳',
  `pub_time_iso` DATETIME COMMENT '格式化发布时间',
  `cover` VARCHAR(500) COMMENT '封面图片URL',
  `bizname` VARCHAR(100) COMMENT '公众号名称',
  `biz` VARCHAR(100) COMMENT '公众号ID',
  `mid` VARCHAR(100) COMMENT '文章mid',
  `idx` VARCHAR(10) COMMENT '文章idx',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_unique_id` (`unique_id`),
  KEY `idx_bizname` (`bizname`),
  KEY `idx_pub_time` (`pub_time_iso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='微信文章';

-- 日志表
CREATE TABLE `logs` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `timestamp` DATETIME NOT NULL COMMENT '日志时间',
  `method` VARCHAR(10) COMMENT '请求方法',
  `path` VARCHAR(200) COMMENT '请求路径',
  `client` VARCHAR(50) COMMENT '客户端IP',
  `data` JSON COMMENT '日志数据',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统日志';