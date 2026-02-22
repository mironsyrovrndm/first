import os

# Настройки
OUTPUT_FILE = 'all_project_code.txt'

# Папки, которые нужно ИГНОРИРОВАТЬ
IGNORE_DIRS = {
    '.git', '.idea', '.vscode', '__pycache__', 'venv', 'env',
    'node_modules', '.next', 'dist', 'build', 'coverage', 'migrations'
}

# Файлы, которые нужно ИГНОРИРОВАТЬ
IGNORE_FILES = {
    '.env', '.env.local', 'package-lock.json', 'yarn.lock',
    'poetry.lock', '.DS_Store', 'collect_code.py', OUTPUT_FILE
}

# Расширения файлов, которые нужно читать
# Добавьте сюда нужные вам, если их нет
ALLOWED_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx',
    '.css', '.j2', '.html', '.sql',
    '.json', '.yaml', '.yml', '.dockerfile', 'Dockerfile', '.toml'
}


def is_text_file(filename):
    """Проверяет, подходит ли файл по расширению"""
    return any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS) or filename == 'Dockerfile'


def collect_files(start_dir):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(start_dir):
            # Удаляем игнорируемые папки из обхода
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                if file in IGNORE_FILES:
                    continue

                if is_text_file(file):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Красивый разделитель для понимания структуры
                        outfile.write(f"\n{'=' * 50}\n")
                        outfile.write(f"FILE: {file_path}\n")
                        outfile.write(f"{'=' * 50}\n")
                        outfile.write(content + "\n")
                        print(f"Добавлен: {file_path}")

                    except Exception as e:
                        print(f"Ошибка чтения {file_path}: {e}")


if __name__ == "__main__":
    current_dir = os.getcwd()
    print(f"Начинаю сборку кода из: {current_dir}")
    collect_files(current_dir)
    print(f"\nГотово! Весь код сохранен в файле: {OUTPUT_FILE}")
