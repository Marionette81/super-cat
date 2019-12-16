DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS creneau;
DROP TABLE IF EXISTS sondage;
DROP TABLE IF EXISTS creneau_sondage;
DROP TABLE IF EXISTS sondage_user;
DROP TABLE IF EXISTS calendrier;
DROP TABLE IF EXISTS calendrier_user;
DROP TABLE IF EXISTS sondage_calendrier;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  nom_doodle TEXT NOT NULL,
  password TEXT NOT NULL,
  mail TEXT UNIQUE NOT NULL
);

CREATE TABLE sondage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL,
  titre TEXT NOT NULL,
  date_entree DATETIME,
  date_maj DATETIME,
  lieu TEXT,
  description TEXT,
  liste_options JSON,
  est_final BOOLEAN
);

CREATE TABLE sondage_user (
  sondage_key TEXT NOT NULL,
  user_id INTEGER NOT NULL,
  FOREIGN KEY (sondage_key) REFERENCES sondage (key),
  FOREIGN KEY (user_id) REFERENCES user (id),
  CONSTRAINT PK_sondage_user PRIMARY KEY (sondage_key,user_id)
);

CREATE TABLE sondage_calendrier (
  sondage_key TEXT NOT NULL,
  calendrier_nom TEXT NOT NULL,
  user_id INTEGER NOT NULL,
  FOREIGN KEY (sondage_key) REFERENCES sondage (key),
  FOREIGN KEY (calendrier_nom) REFERENCES calendrier (calendrier_nom),
  FOREIGN KEY (user_id) REFERENCES user (id),
  CONSTRAINT PK_sondage_calendrier PRIMARY KEY (sondage_key,calendrier_nom,user_id)
);

CREATE TABLE creneau (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cle TEXT,
  debut DATETIME,
  fin DATETIME,
  jourComplet DATETIME
);

CREATE TABLE creneau_sondage (
  creneau_id INTEGER NOT NULL,
  sondage_key TEXT NOT NULL,
  user_id INTEGER NOT NULL,
  FOREIGN KEY (creneau_id) REFERENCES creneau (id),
  FOREIGN KEY (sondage_key) REFERENCES sondage (key),
  FOREIGN KEY (user_id) REFERENCES user (id),
  CONSTRAINT PK_creneau_sondage PRIMARY KEY (creneau_id,sondage_key,user_id)
);



CREATE TABLE calendrier (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	calendrier_nom TEXT UNIQUE NOT NULL,
	calendrier_fichier TEXT UNIQUE NOT NULL,
	description TEXT 
);

CREATE TABLE calendrier_user(
	calendrier_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	FOREIGN KEY (calendrier_id) REFERENCES calendrier(id),
	FOREIGN KEY (user_id) REFERENCES user (id),
	CONSTRAINT PK_calendrier_user PRIMARY KEY (calendrier_id,user_id)
);