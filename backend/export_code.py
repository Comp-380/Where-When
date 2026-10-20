import os

EXCLUDE_DIRS = {'.git', '.venv', '__pycache__', '.pytest_cache', 'venv'}
INCLUDE_EXTENSIONS = {'.py', '.html', '.css', '.js', '.ini', '.md', '.txt'}
OUTPUT_FILE = "codebase_summary.txt"

with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in INCLUDE_EXTENSIONS and file != OUTPUT_FILE and file != "export_code.py":
                file_path = os.path.join(root, file)
                outfile.write(f"\n{'=' * 60}\n")
                outfile.write(f"FILE: {file_path}\n")
                outfile.write(f"{'=' * 60}\n\n")
                try:
                    with open(file_path, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"Error reading file: {e}\n")

print(f"Done! Codebase exported to {OUTPUT_FILE}")