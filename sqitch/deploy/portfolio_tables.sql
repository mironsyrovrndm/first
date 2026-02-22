BEGIN;

CREATE TABLE profile (
    id SERIAL PRIMARY KEY,
    full_name TEXT,
    intro_text TEXT,
    photo_url TEXT,
    specialization TEXT,
    education TEXT,
    looking_for TEXT
);

CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL, -- 'design', 'video', 'soft'
    name TEXT NOT NULL,
    level INTEGER -- м.б. NULL для софт скиллов
);

CREATE TABLE experience (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    period TEXT,
    description TEXT
);

CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    network_name TEXT,
    link_url TEXT,
    display_text TEXT
);

-- Вставим дефолтную запись профиля, чтобы на сайте не было пусто
INSERT INTO profile (full_name, intro_text) VALUES ('Имя Фамилия', 'Описание профиля...');

COMMIT;
