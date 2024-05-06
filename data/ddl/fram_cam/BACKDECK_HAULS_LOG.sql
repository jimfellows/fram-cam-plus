/*
 Navicat Premium Data Transfer

 Source Server         : sqlite - fram_cam
 Source Server Type    : SQLite
 Source Server Version : 3030001
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3030001
 File Encoding         : 65001

 Date: 06/05/2024 09:30:43
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for BACKDECK_HAULS_LOG
-- ----------------------------
DROP TABLE IF EXISTS "BACKDECK_HAULS_LOG";
CREATE TABLE "BACKDECK_HAULS_LOG" (
  "BACKDECK_HAULS_LOG_ID" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "HAUL_NUMBER" text not null unique,
  "INSERTED_DT" text
);

-- ----------------------------
-- Records of BACKDECK_HAULS_LOG
-- ----------------------------

PRAGMA foreign_keys = true;
