import json

with open("Panel_regression.ipynb", "r", encoding="utf-8") as f:
    notebook = json.load(f)

# Find the cell with the comparison code and fix the F-statistic formatting
for cell in notebook["cells"]:
    if cell["cell_type"] == "code":
        source = "".join(cell["source"])
        if "results.f_statistic:.2f" in source:
            # Fix the F-statistic formatting - use .statistic attribute for numeric value
            new_source = source.replace(
                "'F-statistic': f\"{results.f_statistic:.2f}\"",
                "'F-statistic': f\"{results.f_statistic.statistic:.2f}\""
            )
            cell["source"] = new_source.split("\n")
            cell["source"] = [line + "\n" if j < len(cell["source"]) - 1 else line 
                             for j, line in enumerate(cell["source"])]
            break

with open("Panel_regression.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print("Fixed F-statistic formatting!")