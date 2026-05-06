import json

with open('Panel_regression.ipynb') as f:
    nb = json.load(f)

print(f"Всего ячеек: {len(nb['cells'])}")

# Show cells 2-10
for i in range(2, 12):
    if i < len(nb['cells']):
        src = ''.join(nb['cells'][i]['source'])[:300]
        print(f"\n=== Ячейка {i} ===")
        print(src)
