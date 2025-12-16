# apply_fixes.py
# Как использовать:
# 1) помести этот файл в ту же папку, где лежит tests.ipynb
# 2) выполните: python apply_fixes.py
# Результат: tests_cleaned.ipynb

from nbformat import read, write, v4
from pathlib import Path
import re

SRC = Path("tests.ipynb")
OUT = Path("tests_cleaned.ipynb")

if not SRC.exists():
    raise FileNotFoundError(f"Не найден {SRC}. Помести этот скрипт в ту же папку, где tests.ipynb")

with open(SRC, "r", encoding="utf-8") as f:
    nb = read(f, as_version=4)


def mk_code_cell(code):
    header = "# 🔧 Исправлено ChatGPT: внесены правки и добавлены безопасные проверки\n"
    return v4.new_code_cell(header + code)

# Улучшенные функции (вставляются как готовые блоки)
select_code = r"""
def safe_select_order(df, maxlags=None, verbose=True):
    import numpy as np
    from statsmodels.tsa.api import VAR
    nobs = df.shape[0]
    k = df.shape[1]
    if maxlags is None:
        maxlags = min(24, max(1, int(np.floor(nobs/3))))
    maxlags = int(maxlags)
    if verbose:
        print(f"[safe_select_order] nobs={nobs}, k={k}, maxlags={maxlags}")
    model = VAR(df)
    sel = model.select_order(maxlags=maxlags)
    aic = getattr(sel, 'aic', None)
    bic = getattr(sel, 'bic', None)
    hqic = getattr(sel, 'hqic', None)
    if verbose:
        print(" select_order -> AIC:", aic, "BIC:", bic, "HQIC:", hqic)
    if aic is not None and bic is not None and aic > (bic + 3):
        chosen, reason = bic, "BIC (консервативный выбор; AIC предлагает существенно больше лагов)"
    else:
        chosen, reason = aic or bic or hqic or 1, "AIC/BIC fallback"
    if verbose:
        print(f"[safe_select_order] chosen p = {chosen} ({reason})")
    return int(chosen), sel
"""

create_opt_code = r"""
def create_optimal_var_dataset(df, keep_financial_only=False, verbose=True):
    import pandas as pd
    financial_candidates = ['Gold','GDX','HUI','SPT','MVG','GDM','FTGM','XAU','MSCI_ACWI_IMI','JUNR']
    cols = list(df.columns)
    if keep_financial_only:
        keep = [c for c in cols if c in financial_candidates]
    else:
        keep = cols.copy()
        na_frac = df.isna().mean()
        dropna_cols = list(na_frac[na_frac > 0.4].index)
        if dropna_cols and verbose:
            print("Удаляю колонки с >40% пропусков:", dropna_cols)
            keep = [c for c in keep if c not in dropna_cols]
    out = df[keep].dropna(how='any').copy()
    if verbose:
        print("Создан оптимальный набор переменных для VAR. shape:", out.shape)
    return out
"""

fevd_code = r"""
def safe_feved_and_irf(res, gold_name=None, h=12, verbose=True):
    out = {}
    try:
        fevd = res.fevd(h)
        decomp = getattr(fevd, 'decomp', getattr(fevd, '_decomp', None))
        out['fevd_shape'] = None if decomp is None else decomp.shape
        out['fevd_decomp'] = decomp
        if verbose:
            print("[safe_feved_and_irf] FEVD shape:", out['fevd_shape'])
        if gold_name is not None and decomp is not None:
            cols = list(res.endog_names)
            if gold_name in cols:
                gold_idx = cols.index(gold_name)
                k = len(cols)
                contribs = {}
                for i in range(k):
                    if i == gold_idx: continue
                    try:
                        mean_share = decomp[1:h+1, i, gold_idx].mean() * 100
                    except Exception:
                        mean_share = None
                    contribs[cols[i]] = mean_share
                out['gold_contrib_mean_pct'] = contribs
    except Exception as e:
        out['fevd_error'] = str(e)
        if verbose:
            print("FEVD error:", e)
    try:
        irf = res.irf(h)
        out['irf_shape'] = getattr(irf, 'irfs', None).shape if hasattr(irf, 'irfs') else None
        out['irf_obj'] = irf
        if verbose:
            print("[safe_feved_and_irf] IRF shape:", out.get('irf_shape'))
    except Exception as e:
        out['irf_error'] = str(e)
        if verbose:
            print("IRF error:", e)
    return out
"""

# Traverse and modify
replaced = []
for i, cell in enumerate(nb.cells):
    if cell.cell_type != "code":
        continue
    src = cell.source or ""
    if re.search(r"def\s+select_var_lags\s*\(", src) or re.search(r"def\s+select_optimal_lags\s*\(", src):
        nb.cells[i] = mk_code_cell(select_code + "\n\n" + fevd_code)
        replaced.append(("select", i))
    elif re.search(r"def\s+create_optimal_var_dataset\s*\(", src):
        nb.cells[i] = mk_code_cell(create_opt_code)
        replaced.append(("create_opt", i))
    elif ".fevd(" in src or ".irf(" in src:
        # append safe call example
        new_src = "# 🔧 Исправлено ChatGPT: добавлена обёртка safe_feved_and_irf\n" + src + "\n\n# Пример безопасного вызова:\ntry:\n    _safe_out = safe_feved_and_irf(res, gold_name='Gold', h=12, verbose=True)\n    print('safe_feved_and_irf keys:', list(_safe_out.keys()))\nexcept Exception as _e:\n    print('FEVD/IRF safe wrapper error:', _e)\n"
        nb.cells[i] = v4.new_code_cell(new_src)
        replaced.append(("fevd_wrap", i))

# If core helper not present, insert near top (after first import cell)
core_present = any('safe_select_order' in (c.source or "") for c in nb.cells)
if not core_present:
    insert_pos = 0
    for idx, c in enumerate(nb.cells[:8]):
        if c.cell_type == "code" and ("import pandas" in (c.source or "") or "import numpy" in (c.source or "")):
            insert_pos = idx + 1
            break
    nb.cells.insert(insert_pos, mk_code_cell(select_code + "\n\n" + create_opt_code + "\n\n" + fevd_code))
    replaced.append(("insert_core", insert_pos))

# Append summary markdown
summary = """
**🔧 Исправлено ChatGPT — сводка:**  
- Улучшен выбор лагов: `safe_select_order` учитывает nobs и выбирает между AIC/BIC с консервативным fallback.  
- Добавлена `create_optimal_var_dataset` с флагом keep_financial_only и фильтром пропусков.  
- FEVD/IRF вызовы обёрнуты в `safe_feved_and_irf` с обработкой ошибок.  
(Изменённые ячейки помечены комментарием в начале.)  
"""
nb.cells.append(v4.new_markdown_cell(summary))

with open(OUT, "w", encoding="utf-8") as f:
    write(nb, f)

print("Сохранено:", OUT)
print("Заменённые ячейки:", replaced)
