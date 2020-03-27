create database IoT_datos;
use IoT_datos;


CREATE TABLE valorVariables (
  variable varchar(5),
  descripcion text ,
  PRIMARY KEY (variable)
);

INSERT INTO valorVariables VALUES ('2','Temperatura');

CREATE TABLE clima (
  id text,
  firma text,
  latitud long,
  longitud long,
  fecha date ,
  hora time,
  variable varchar(5),
  valor text,
  FOREIGN KEY (variable) REFERENCES valorVariables (variable)
);