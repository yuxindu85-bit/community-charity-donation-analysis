import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {".py", ".csv", ".md", ".json", ".txt", ".yml", ".yaml"}
SKIP_PARTS = {
    ".git",
    "__pycache__",
    ".matplotlib_cache",
    ".ipynb_checkpoints",
    ".venv",
    "venv",
}
SUSPICIOUS_PATTERN_PARTS = [
    ("import os", "from pathlib"),
    ("import sys", "import unittest"),
    ("import json", "from pathlib"),
    ("from pathlib import Path", "import"),
]


def line_count(path):
    return len(path.read_text(encoding="utf-8").splitlines())


def is_skipped(path):
    return any(part in SKIP_PARTS for part in path.parts)


def important_files():
    patterns = [
        "README.md",
        "requirements.txt",
        "src/*.py",
        "tests/*.py",
        "dashboard/*.py",
        "tools/*.py",
        "data/raw/*.csv",
        "data/processed/*.csv",
        "docs/*.md",
        "reports/*.md",
        "models/*.json",
        "notebooks/*.ipynb",
    ]

    seen = set()
    for pattern in patterns:
        for path in PROJECT_ROOT.glob(pattern):
            if path.is_file() and not is_skipped(path) and path not in seen:
                seen.add(path)
                yield path


def check_python_file(path, text, lines):
    issues = []
    package_marker_names = {"__init__.py"}

    if path.name not in package_marker_names and lines < 30:
        issues.append("too few physical lines for Python")

    if path.parent.name == "src" and path.name not in package_marker_names | {"run_all.py"} and lines < 35:
        issues.append("major src file should have at least 35 lines")

    if path.name == "run_all.py" and lines < 40:
        issues.append("run_all.py should have at least 40 lines")

    if path.name == "clean_data.py" and lines < 80:
        issues.append("clean_data.py should have at least 80 lines")

    if path.name == "utils.py" and lines < 80:
        issues.append("utils.py should have at least 80 lines")

    for pattern_parts in SUSPICIOUS_PATTERN_PARTS:
        pattern = " ".join(pattern_parts)
        if pattern in text:
            issues.append(f"suspicious compressed import pattern: {pattern}")

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.count(";") >= 3:
            issues.append(f"too many semicolons on line {line_number}")
        if stripped.startswith("import ") and " import " in stripped[7:]:
            issues.append(f"multiple imports may be compressed on line {line_number}")

    return issues


def check_csv_file(path, text, lines):
    issues = []

    if lines < 10:
        issues.append("CSV should have at least 10 physical lines")

    csv_lines = text.splitlines()
    if csv_lines and "," not in csv_lines[0]:
        issues.append("CSV header does not contain commas")

    if lines == 1 and text.count(",") > 10:
        issues.append("CSV appears compressed into one physical line")

    return issues


def check_markdown_file(path, text, lines):
    issues = []

    if path.name == "README.md" and lines < 120:
        issues.append("README.md should have at least 120 physical lines")

    if path.parent.name == "docs" and lines < 15:
        issues.append("Markdown docs should have at least 15 physical lines")

    if path.parent.name == "reports" and lines < 20:
        issues.append("Markdown reports should have at least 20 physical lines")

    if lines <= 3 and text.count("#") >= 3:
        issues.append("Markdown headings appear compressed into too few lines")

    return issues


def check_json_file(path, text, lines):
    issues = []

    try:
        json.loads(text)
    except json.JSONDecodeError as error:
        issues.append(f"invalid JSON: {error}")

    if path.name == "model_metrics.json" and lines < 10:
        issues.append("model_metrics.json should be pretty-printed")

    return issues


def check_notebook_file(path, text, lines):
    issues = []

    try:
        notebook = json.loads(text)
    except json.JSONDecodeError as error:
        return [f"invalid notebook JSON: {error}"]

    cells = notebook.get("cells", [])
    if not cells:
        issues.append("notebook has no cells")

    markdown_cells = [cell for cell in cells if cell.get("cell_type") == "markdown"]
    code_cells = [cell for cell in cells if cell.get("cell_type") == "code"]
    if not markdown_cells:
        issues.append("notebook has no Markdown cells")
    if not code_cells:
        issues.append("notebook has no code cells")

    if lines < 20:
        issues.append("notebook should not be a tiny placeholder")

    return issues


def audit_file(path):
    text = path.read_text(encoding="utf-8")
    lines = len(text.splitlines())
    suffix = path.suffix.lower()

    if path.name == "README.md":
        issues = check_markdown_file(path, text, lines)
    elif suffix == ".py":
        issues = check_python_file(path, text, lines)
    elif suffix == ".csv":
        issues = check_csv_file(path, text, lines)
    elif suffix == ".md":
        issues = check_markdown_file(path, text, lines)
    elif suffix == ".json":
        issues = check_json_file(path, text, lines)
    elif suffix == ".ipynb":
        issues = check_notebook_file(path, text, lines)
    else:
        issues = []

    if len(text) > 200 and text.count("\n") <= 1:
        issues.append("large text file appears compressed into one line")

    return lines, issues


def run_audit():
    rows = []
    failures = []

    for path in sorted(important_files(), key=lambda item: str(item)):
        relative_path = path.relative_to(PROJECT_ROOT)
        lines, issues = audit_file(path)
        status = "FAIL" if issues else "OK"
        issue_text = "; ".join(issues) if issues else "-"
        rows.append((str(relative_path), lines, status, issue_text))
        if issues:
            failures.append(str(relative_path))

    print("FILE | LINE COUNT | STATUS | ISSUE")
    print("--- | ---: | --- | ---")
    for file_name, lines, status, issue_text in rows:
        print(f"{file_name} | {lines} | {status} | {issue_text}")

    if failures:
        print()
        print("Format audit failed.")
        print("Broken files:")
        for file_name in failures:
            print(f"- {file_name}")
        return 1

    print()
    print(f"Format audit passed. Checked {len(rows)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(run_audit())
