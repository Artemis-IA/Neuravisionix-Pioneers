-- init.sql
CREATE DATABASE IF NOT EXISTS bdd_user;
USE bdd_user;

-- Création de la table
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'utilisateur') NOT NULL
);
