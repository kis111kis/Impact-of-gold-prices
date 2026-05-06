import json

with open("Panel_regression.ipynb", "r", encoding="utf-8") as f:
    notebook = json.load(f)

fixes_applied = 0

for cell in notebook["cells"]:
    if cell["cell_type"] == "code":
        source = "".join(cell["source"])
        modified = False
        
        # Fix 1: IV2SLS model - replace clustered with robust
        if "model_iv.fit(cov_type='clustered'" in source:
            new_source = source.replace(
                "results_iv = model_iv.fit(cov_type='clustered', \n                          cluster_entity=True, \n                          cluster_time=True)",
                "results_iv = model_iv.fit(cov_type='robust')"
            )
            if new_source != source:
                cell["source"] = new_source.split("\n")
                cell["source"] = [line + "\n" if j < len(cell["source"]) - 1 else line 
                                 for j, line in enumerate(cell["source"])]
                modified = True
                fixes_applied += 1
                print("Fixed IV2SLS fit() call")
        
        # Fix 2: F-statistic formatting - first_stage_results
        if "first_stage_results.f_statistic:.2f" in source:
            new_source = source.replace(
                "first_stage_results.f_statistic:.2f",
                "first_stage_results.f_statistic.stat:.2f"
            )
            if new_source != source:
                cell["source"] = new_source.split("\n")
                cell["source"] = [line + "\n" if j < len(cell["source"]) - 1 else line 
                                 for j, line in enumerate(cell["source"])]
                modified = True
                fixes_applied += 1
                print("Fixed first_stage_results F-statistic formatting")
        
        # Fix 3: F-statistic formatting - results.f_statistic (any remaining)
        if "results.f_statistic:.2f" in source and "results.f_statistic.stat" not in source:
            new_source = source.replace(
                "results.f_statistic:.2f",
                "results.f_statistic.stat:.2f"
            )
            if new_source != source:
                cell["source"] = new_source.split("\n")
                cell["source"] = [line + "\n" if j < len(cell["source"]) - 1 else line 
                                 for j, line in enumerate(cell["source"])]
                modified = True
                fixes_applied += 1
                print("Fixed results F-statistic formatting")

if fixes_applied == 0:
    print("No fixes needed or all fixes already applied")
else:
    with open("Panel_regression.ipynb", "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    print(f"\nTotal fixes applied: {fixes_applied}")
    print("Notebook updated successfully!")