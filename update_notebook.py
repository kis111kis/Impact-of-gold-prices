import json

with open("Panel_regression.ipynb", "r", encoding="utf-8") as f:
    notebook = json.load(f)

# Find the markdown cell with "Загрузка data" and add data folder selection
for i, cell in enumerate(notebook["cells"]):
    if cell["cell_type"] == "markdown" and "Загрузка data" in "".join(cell["source"]):
        new_cell = {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "### Выбор папки с data\n",
                "\n",
                "Укажите папку, в которой находятся файлы с data. Доступные папки:\n",
                "- `data2/` - основные data\n",
                "- `data3/` - альтернативные data\n",
                "\n",
                "По умолчанию используется `data3/`."
            ]
        }
        notebook["cells"].insert(i, new_cell)
        break

# Find the first code cell after imports and add data folder config
for i, cell in enumerate(notebook["cells"]):
    if cell["cell_type"] == "code" and "print(\"✅ Библиотеки загружены\")" in "".join(cell["source"]):
        new_cell = {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# ============================================\n",
                "# НАСТРОЙКА: Выбор папки с data\n",
                "# ============================================\n",
                "\n",
                "# Измените эту переменную для выбора другой папки\n",
                "DATA_FOLDER = \"data3/\"  # Варианты: \"data2/\", \"data3/\"\n",
                "\n",
                "print(f\"📁 Используемая папка с data: {DATA_FOLDER}\")\n",
                "\n",
                "# Проверяем существование папки\n",
                "import os\n",
                "if not os.path.exists(DATA_FOLDER):\n",
                "    print(f\"⚠️ Папка {DATA_FOLDER} не найдена!\")\n",
                "    print(\"Доступные папки:\")\n",
                "    for folder in [\"data2/\", \"data3/\"]:\n",
                "        if os.path.exists(folder):\n",
                "            print(f\"  ✅ {folder}\")\n",
                "    raise FileNotFoundError(f\"Папка {DATA_FOLDER} не найдена\")\n",
                "else:\n",
                "    print(f\"✅ Папка {DATA_FOLDER} найдена\")\n",
                "    print(f\"   Файлов в папке: {len(os.listdir(DATA_FOLDER))}\")"
            ]
        }
        notebook["cells"].insert(i + 1, new_cell)
        break

# Update load_data_file function to use DATA_FOLDER
for cell in notebook["cells"]:
    if cell["cell_type"] == "code":
        source = "".join(cell["source"])
        if "def load_data_file(config):" in source:
            new_source = source.replace(
                "df = pd.read_csv(config[\"path\"])", 
                "file_path = os.path.join(DATA_FOLDER, config[\"path\"])\n        df = pd.read_csv(file_path)"
            )
            cell["source"] = new_source.split("\n")
            cell["source"] = [line + "\n" if j < len(cell["source"]) - 1 else line 
                             for j, line in enumerate(cell["source"])]
            break

with open("Panel_regression.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print("Notebook updated successfully!")