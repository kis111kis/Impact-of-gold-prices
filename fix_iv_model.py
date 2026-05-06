import json

with open("Panel_regression.ipynb", "r", encoding="utf-8") as f:
    notebook = json.load(f)

# Find the cell with IV2SLS model and fix the fit() call
for cell in notebook["cells"]:
    if cell["cell_type"] == "code":
        source = "".join(cell["source"])
        if "IV2SLS(" in source and "model_iv.fit(cov_type='clustered'" in source:
            # Fix the fit() call - use 'robust' instead of 'clustered' for IV models
            new_source = source.replace(
                "results_iv = model_iv.fit(cov_type='clustered', \n                          cluster_entity=True, \n                          cluster_time=True)",
                "results_iv = model_iv.fit(cov_type='robust')"
            )
            cell["source"] = new_source.split("\n")
            cell["source"] = [line + "\n" if j < len(cell["source"]) - 1 else line 
                             for j, line in enumerate(cell["source"])]
            break

with open("Panel_regression.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print("Fixed IV2SLS model fit() call!")