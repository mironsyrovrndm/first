-- Создаем таблицу проектов
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    title_ru VARCHAR(255) NOT NULL,
    title_en VARCHAR(255),
    short_desc_ru TEXT,
    short_desc_en TEXT,
    preview_image VARCHAR(255),
    full_desc_ru TEXT,
    full_desc_en TEXT,
    video_url VARCHAR(500),
    order_num INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблица галереи (один-ко-многим)
CREATE TABLE project_images (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    image_filename VARCHAR(255) NOT NULL
);

-- Индексы для скорости
CREATE INDEX idx_projects_published ON projects(is_published);
CREATE INDEX idx_projects_order ON projects(order_num);
CREATE INDEX idx_project_images_project ON project_images(project_id);
