
DROP TABLE IF EXISTS game_character;
DROP TABLE IF EXISTS game;
DROP TABLE IF EXISTS event;
DROP TABLE IF EXISTS mod;
DROP TABLE IF EXISTS player;
DROP TABLE IF EXISTS vod;
DROP TABLE IF EXISTS submission;

CREATE TABLE mod (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE game (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE game_character (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  game_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  icon_url TEXT,
  FOREIGN KEY (game_id) REFERENCES game (id)
);

CREATE TABLE player (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT NOT NULL
);

CREATE TABLE submission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    status INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    p1 TEXT,
    c1 TEXT,
    p2 TEXT,
    c2 TEXT,
    p3 TEXT,
    c3 TEXT,
    p4 TEXT,
    c4 TEXT,
    round TEXT,
    event TEXT,
    date TEXT,
    FOREIGN KEY (game_id) REFERENCES game (id)
);

CREATE TABLE event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    vods_url TEXT
);

CREATE TABLE vod (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  game_id INTEGER NOT NULL,
  event_id INTEGER NOT NULL,
  url TEXT NOT NULL,
  p1_id INTEGER NOT NULL,
  c1_id INTEGER NOT NULL,
  p2_id INTEGER NOT NULL,
  c2_id INTEGER NOT NULL,
  p3_id INTEGER,
  c3_id INTEGER,
  p4_id INTEGER,
  c4_id INTEGER,
  submission_id INTEGER,
  vod_date TIMESTAMP,
  round TEXT,
  FOREIGN KEY (game_id) REFERENCES game (id),
  FOREIGN KEY (event_id) REFERENCES event (id),
  FOREIGN KEY (p1_id) REFERENCES player (id),
  FOREIGN KEY (p2_id) REFERENCES player (id),
  FOREIGN KEY (p3_id) REFERENCES player (id),
  FOREIGN KEY (p4_id) REFERENCES player (id),
  FOREIGN KEY (c1_id) REFERENCES game_character (id),
  FOREIGN KEY (c2_id) REFERENCES game_character (id),
  FOREIGN KEY (c3_id) REFERENCES game_character (id),
  FOREIGN KEY (c4_id) REFERENCES game_character (id),
  FOREIGN KEY (submission_id) REFERENCES submission (id)
);

CREATE INDEX idx_submission_status ON submission (status);
CREATE INDEX idx_vod_c1 ON vod (c1_id);
CREATE INDEX idx_vod_c2 ON vod (c2_id);
CREATE INDEX idx_vod_p1 ON vod (p1_id);
CREATE INDEX idx_vod_p2 ON vod (p2_id);

INSERT INTO game (name) VALUES ("Rivals of Aether 2");

-- Clairen = 1
INSERT INTO game_character (game_id, name, icon_url) VALUES (1, "Clairen", "https://akbiggs-vods-18c62d7f-a87a-4da5-b315-7a7f450c7577.s3.us-east-2.amazonaws.com/clairen_small.png");
-- Ranno = 2
INSERT INTO game_character (game_id, name, icon_url) VALUES (1, "Ranno", "https://akbiggs-vods-18c62d7f-a87a-4da5-b315-7a7f450c7577.s3.us-east-2.amazonaws.com/ranno_small.png");
-- Zetter = 3
INSERT INTO game_character (game_id, name, icon_url) VALUES (1, "Zetterburn", "https://akbiggs-vods-18c62d7f-a87a-4da5-b315-7a7f450c7577.s3.us-east-2.amazonaws.com/zetter_small.png");
-- Forsburn = 4
INSERT INTO game_character (game_id, name, icon_url) VALUES (1, "Forsburn", "https://akbiggs-vods-18c62d7f-a87a-4da5-b315-7a7f450c7577.s3.us-east-2.amazonaws.com/fors_small.png");
-- Orcane = 5
INSERT INTO game_character (game_id, name, icon_url) VALUES (1, "Orcane", "https://akbiggs-vods-18c62d7f-a87a-4da5-b315-7a7f450c7577.s3.us-east-2.amazonaws.com/orcane_small.png");
-- Fleet = 6
INSERT INTO game_character (game_id, name, icon_url) VALUES (1, "Fleet", "https://akbiggs-vods-18c62d7f-a87a-4da5-b315-7a7f450c7577.s3.us-east-2.amazonaws.com/fleet_small.png");
-- Kragg = 7
INSERT INTO game_character (game_id, name, icon_url) VALUES (1, "Kragg", "https://akbiggs-vods-18c62d7f-a87a-4da5-b315-7a7f450c7577.s3.us-east-2.amazonaws.com/kragg_small.png");
-- Wrastor = 8
INSERT INTO game_character (game_id, name, icon_url) VALUES (1, "Wrastor", "https://akbiggs-vods-18c62d7f-a87a-4da5-b315-7a7f450c7577.s3.us-east-2.amazonaws.com/wrastor_small.png");
-- Loxodont = 9
INSERT INTO game_character (game_id, name, icon_url) VALUES (1, "Loxodont", "https://akbiggs-vods-18c62d7f-a87a-4da5-b315-7a7f450c7577.s3.us-east-2.amazonaws.com/loxodont_small.png");
-- Maypul = 10
INSERT INTO game_character (game_id, name, icon_url) VALUES (1, "Maypul", "https://akbiggs-vods-18c62d7f-a87a-4da5-b315-7a7f450c7577.s3.us-east-2.amazonaws.com/maypul_small.png");
-- Etalus = 11
INSERT INTO game_character (game_id, name, icon_url) VALUES (1, "Etalus", "https://akbiggs-vods-18c62d7f-a87a-4da5-b315-7a7f450c7577.s3.us-east-2.amazonaws.com/etalus_small.png");
-- Olympia = 12
INSERT INTO game_character (game_id, name, icon_url) VALUES (1, "Olympia", "https://akbiggs-vods-18c62d7f-a87a-4da5-b315-7a7f450c7577.s3.us-east-2.amazonaws.com/oly_small.png");
-- Absa = 13
INSERT INTO game_character (game_id, name, icon_url) VALUES (1, "Absa", "https://akbiggs-vods-18c62d7f-a87a-4da5-b315-7a7f450c7577.s3.us-east-2.amazonaws.com/absa_small.png");
-- Galvan = 14
INSERT INTO game_character (game_id, name, icon_url) VALUES (1, "Galvan", "https://akbiggs-vods-18c62d7f-a87a-4da5-b315-7a7f450c7577.s3.us-east-2.amazonaws.com/colin_small.png");