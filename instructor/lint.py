from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
EXCLUDED = {".git", ".venv", "__pycache__", "runs"}
problems: list[str] = []

for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or EXCLUDED & set(path.parts):
        continue
    if path.suffix in {".py", ".md", ".json", ".toml"}:
        text = path.read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), 1):
            if line.rstrip() != line:
                problems.append(f"{path.relative_to(ROOT)}:{number}: trailing whitespace")
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=str(path))
            except SyntaxError as error:
                problems.append(f"{path.relative_to(ROOT)}:{error.lineno}: {error.msg}")
        elif path.suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as error:
                problems.append(f"{path.relative_to(ROOT)}:{error.lineno}: {error.msg}")
        elif path.suffix == ".md":
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                relative = target.split("#", 1)[0]
                if relative and not relative.startswith(("http://", "https://", "mailto:")):
                    if not (path.parent / relative).exists():
                        problems.append(
                            f"{path.relative_to(ROOT)}: unresolved markdown link: {target}"
                        )

if problems:
    print("\n".join(problems))
    raise SystemExit(1)
print("lint: OK")
