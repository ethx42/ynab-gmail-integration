import os

def dump_directory(dir_path, output_file, excluded_extensions=('.log', '.tmp', '.json', '.DS_Store'), excluded_dirs=('venv', '__pycache__', '.git')):
    with open(output_file, 'w', encoding='utf-8') as out:
        for root, dirs, files in os.walk(dir_path, topdown=True):
            # Excluir directorios no deseados
            dirs[:] = [d for d in dirs if d not in excluded_dirs]

            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path) and not os.path.splitext(file_path)[1] in excluded_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            text = f.read()
                            out.write(f"\n### Archivo: {file_path}\n{text}\n")
                    except UnicodeDecodeError:
                        print(f"Could not decode {file_path}; skipping.")

# Directorio a procesar: subir un nivel respecto a la ubicación actual del script
dir_path = os.path.join(os.path.dirname(__file__), "..")

# Archivo de salida
output_file = "dump.txt"

# Llamar a la función con las exclusiones deseadas
dump_directory(dir_path, output_file)
