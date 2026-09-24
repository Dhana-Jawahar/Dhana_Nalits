-- CREATE DATABASE bookinvdb;
\c bookinvdb;

 CREATE TABLE books (
    bookid SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS users (
    userid SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    userpwd VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user' ,  
    CONSTRAINT chk_only_role
    CHECK (role IN ('admin', 'user')));

 