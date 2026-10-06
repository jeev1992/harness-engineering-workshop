from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

MIN_TOKEN_LENGTH = 4
NO_MATCH = "No matching lines. Import more documents or rephrase the question."


def _tokens(text: str) -> set[str]:
    return set(re.findall(rf"[a-z0-9]{{{MIN_TOKEN_LENGTH},}}", text.lower()))


def _title(text: str, filename: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return text.splitlines()[0].strip() or filename


def _metadata(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    return {
        "id": path.stem,
        "title": _title(text, path.name),
        "filename": path.name,
        "lines": len(text.rstrip("\n").splitlines()),
    }


def init(data_dir: Path, seed_dir: Path) -> dict[str, object]:
    documents = data_dir / "documents"
    index_dir = data_dir / "index"
    documents.mkdir(parents=True, exist_ok=True)
    index_dir.mkdir(parents=True, exist_ok=True)
    for source in sorted(seed_dir.iterdir()):
        if source.is_file():
            shutil.copy2(source, documents / source.name)
    entries = [_metadata(path) for path in sorted(documents.iterdir()) if path.is_file()]
    _write_index(data_dir, entries)
    return {"documents": len(entries), "data_dir": str(data_dir)}


def _read_index(data_dir: Path) -> list[dict[str, object]]:
    path = data_dir / "index" / "documents.json"
    if not path.is_file():
        raise ValueError(f"metadata index missing in {data_dir}; run workshop reset")
    return json.loads(path.read_text(encoding="utf-8"))


def _write_index(data_dir: Path, entries: list[dict[str, object]]) -> None:
    path = data_dir / "index" / "documents.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(entries, key=lambda item: item["id"]), indent=2) + "\n")


def list_documents(data_dir: Path) -> dict[str, object]:
    return {"documents": _read_index(data_dir)}


def ask(data_dir: Path, question: str) -> dict[str, object]:
    query = _tokens(question)
    matches: list[tuple[int, str, int, str]] = []
    for entry in _read_index(data_dir):
        path = data_dir / "documents" / str(entry["filename"])
        if not path.is_file():
            raise ValueError(
                f"indexed document {entry['id']} has no source file {entry['filename']}"
            )
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            score = len(query & _tokens(line))
            if score:
                matches.append((-score, str(entry["id"]), line_number, line.strip()))
    matches.sort()
    citations = [
        {"document": document, "line": line_number, "text": line}
        for _, document, line_number, line in matches[:2]
    ]
    answer = " ".join(item["text"] for item in citations) if citations else NO_MATCH
    return {"question": question, "answer": answer, "citations": citations}


def reconcile(data_dir: Path) -> dict[str, object]:
    """Drop index entries whose source file no longer exists."""
    entries = _read_index(data_dir)
    kept = [entry for entry in entries if (data_dir / "documents" / str(entry["filename"])).is_file()]
    dropped = sorted(str(entry["id"]) for entry in entries if entry not in kept)
    _write_index(data_dir, kept)
    return {"dropped": dropped, "remaining": len(kept)}


def compact(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def main(argv: list[str] | None = None) -> int:
    """Command line: python kb/kb.py <data_dir> list | ask <question> | delete <id> | import <file> | reconcile"""
    parser = argparse.ArgumentParser(prog="kb")
    parser.add_argument("data_dir", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    commands.add_parser("ask").add_argument("question")
    commands.add_parser("delete").add_argument("document_id")
    commands.add_parser("import").add_argument("source", type=Path)
    commands.add_parser("reconcile")
    args = parser.parse_args(argv)
    # Deletion and import are the class work items: until a function exists, say so.
    pending = {"delete": "delete", "import": "import_document"}
    if args.command in pending and pending[args.command] not in globals():
        print(f"error: {args.command} is not implemented yet")
        return 2
    try:
        if args.command == "list":
            result = list_documents(args.data_dir)
        elif args.command == "ask":
            answer = ask(args.data_dir, args.question)
            print(compact(answer))
            return 0 if answer["citations"] else 1
        elif args.command == "delete":
            result = globals()["delete"](args.data_dir, args.document_id)
        elif args.command == "import":
            result = globals()["import_document"](args.data_dir, args.source)
        else:
            result = reconcile(args.data_dir)
    except (ValueError, OSError) as error:
        print(f"error: {error}")
        return 1
    print(compact(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

