create database e_software;
use e_software;
create table programa (
    cod_p SMALLINT PRIMARY KEY,
    nom VARCHAR(30) NOT NULL,
    descip VARCHAR(100)
)
create table ventana (
    cod_v SMALLINT PRIMARY KEY,
    titulo VARCHAR(30) NOT NULL,
    descrip VARCHAR(100),
    cod_p SMALLINT,
    FOREIGN KEY (cod_p) REFERENCES programa(cod_p)
)
create table control (
    cod_c SMALLINT PRIMARY KEY,
    etiqueta VARCHAR(30) NOT NULL,
    tipo VARCHAR(20),
    funcion VARCHAR(100),
    cod_v SMALLINT,
    FOREIGN KEY (cod_v) REFERENCES ventana(cod_v)
)
create table accion (
    cod_a SMALLINT PRIMARY KEY,
    descrip VARCHAR(100)
)
create table contiene (
    cod_cont SMALLINT PRIMARY KEY,
    cod_v SMALLINT,
    FOREIGN KEY (cod_v) REFERENCES ventana(cod_v),
    cod_c SMALLINT,
    FOREIGN KEY (cod_c) REFERENCES control(cod_c)
)