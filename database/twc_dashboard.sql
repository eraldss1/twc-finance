-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 21, 2023 at 04:41 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4
SET
  SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";

START TRANSACTION;

SET
  time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */
;

/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */
;

/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */
;

/*!40101 SET NAMES utf8mb4 */
;

CREATE DATABASE IF NOT EXISTS twc_dashboard;

USE twc_dashboard;

--
-- Database: `twc_dashboard`
--
-- --------------------------------------------------------
--
-- Table structure for table `finance`
--
CREATE TABLE `finance` (
  `id_cluster_finance` int(20) NOT NULL,
  `cluster_finance` varchar(50) NOT NULL,
  `id_unit` int(20) NOT NULL,
  `unit_name` varchar(50) NOT NULL,
  `id_component_name` text NOT NULL,
  `component_name` varchar(50) NOT NULL,
  `bytelevel` int(20) NOT NULL,
  `bRealization` int(20) NOT NULL,
  `py` year(4) NOT NULL,
  `pq` int(20) NOT NULL,
  `pm` int(20) NOT NULL,
  `amount` float NOT NULL,
  `lastUpdated` datetime NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

-- --------------------------------------------------------
--
-- Table structure for table `logdata`
--
CREATE TABLE `logdata` (
  `fileName` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `dataType` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `sheetName` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `periodTime` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `executeTime` datetime DEFAULT NULL,
  `status` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `deskripsi` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `jumlahRow` int(11) DEFAULT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */
;

/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */
;

/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */
;