"""One-off helper: append a short Chinese footer to markdown cells in notebooks.

Run: uv run python scripts/append_notebook_markdown_zh.py
"""

from __future__ import annotations

import json
import pathlib
import re
import sys


def patch_notebook(path: pathlib.Path) -> int:
    nb = json.loads(path.read_text(encoding="utf-8"))
    m = re.search(r"week(\d+)", path.as_posix().replace("\\", "/"))
    wk = m.group(1) if m else "?"

    tag = (
        "\n\n---\n\n"
        f"> **中文（单元格对照）：** 上文/上表 **英文为原文**；本段补充中文提示：请结合 **第 {wk} 周** "
        f"仓库 `README.md` 与 `notebooks/week{wk}/README.md` 理解术语与步骤。\n"
    )

    changed = 0
    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "markdown":
            continue
        src = cell.get("source", [])
        text = src if isinstance(src, str) else "".join(src)
        if i == 0 and "中文导读 / Chinese Guide" in text:
            continue
        if "中文（单元格对照）" in text:
            continue
        if not text.strip():
            continue
        new_text = text if text.endswith("\n") else text + "\n"
        new_text += tag
        cell["source"] = [new_text]
        changed += 1

    if changed:
        path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return changed


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1] / "notebooks"
    total = 0
    for p in sorted(root.rglob("*.ipynb")):
        c = patch_notebook(p)
        total += c
        print(f"{p}: markdown cells patched: {c}")
    print("total appended:", total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
