/*
 Navicat Premium Data Transfer

 Source Server         : sqlite - fram_cam
 Source Server Type    : SQLite
 Source Server Version : 3030001
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3030001
 File Encoding         : 65001

 Date: 06/05/2024 09:31:19
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for BACKDECK_BIOS_LOG
-- ----------------------------
DROP TABLE IF EXISTS "BACKDECK_BIOS_LOG";
CREATE TABLE "BACKDECK_BIOS_LOG" (
  "BACKDECK_BIOS_LOG_ID" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "BACKDECK_CLIENT_NAME" text,
  "HAUL_NUMBER" text,
  "DISPLAY_NAME" text,
  "COMMON_NAME" text,
  "SCIENTIFIC_NAME" text,
  "BIO_LABEL" text,
  "BIO_TYPE" text,
  "BIO_SUBTYPE" text,
  "PROJECT_NAME" text,
  "PROJECT_SCIENTIST" text,
  "INSERTED_DT" text,
  HAUL_ID integer,
  CATCH_ID integer,
  SPECIMEN_ID integer,
  SPECIMEN_ATTR_ID integer,
  TAXONOMY_ID integer
);

-- ----------------------------
-- Auto increment value for BACKDECK_BIOS_LOG
-- ----------------------------
-- UPDATE "sqlite_sequence" SET seq = 64 WHERE name = 'BACKDECK_BIOS_LOG';

PRAGMA foreign_keys = true;
