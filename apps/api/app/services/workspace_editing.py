from __future__ import annotations

import re
from pathlib import Path

from app.models.schemas import EditOperation

_HUNK_HEADER_RE = re.compile(
    r"^@@ -(?P<old_start>\d+)(?:,(?P<old_count>\d+))? \+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@"
)


def apply_edit_operation(file_path: Path, operation: EditOperation) -> tuple[str, str]:
    if operation.operation == "create":
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(operation.content, encoding="utf-8")
        return "create", operation.content[:1500]

    if operation.operation == "delete":
        if not file_path.exists():
            raise ValueError(f"Cannot delete missing file: {operation.path}")
        file_path.unlink()
        return "delete", ""

    if not file_path.exists():
        raise ValueError(f"Cannot update missing file: {operation.path}")

    original = file_path.read_text(encoding="utf-8")
    reject_whole_file_rewrite(original, operation)
    updated = apply_update(original, operation)
    file_path.write_text(updated, encoding="utf-8")
    return "update", updated[:1500]


def apply_update(original: str, operation: EditOperation) -> str:
    if operation.strategy == "replace":
        if operation.old_text not in original:
            raise ValueError(f"Expected text not found for {operation.path}")
        return original.replace(operation.old_text, operation.new_text, 1)

    if operation.strategy == "insert_after":
        anchor = operation.anchors[0]
        if anchor not in original:
            raise ValueError(f"Anchor not found for {operation.path}")
        return original.replace(anchor, f"{anchor}{operation.new_text}", 1)

    if operation.strategy == "insert_before":
        anchor = operation.anchors[0]
        if anchor not in original:
            raise ValueError(f"Anchor not found for {operation.path}")
        return original.replace(anchor, f"{operation.new_text}{anchor}", 1)

    if operation.strategy == "patch":
        return apply_single_file_unified_diff(original, operation.unified_diff, operation.path)

    raise ValueError(f"Unsupported update strategy: {operation.strategy}")


def apply_single_file_unified_diff(original: str, unified_diff: str, path: str) -> str:
    original_lines = original.splitlines()
    updated_lines: list[str] = []
    cursor = 0
    current_hunk_lines: list[str] = []
    current_old_start: int | None = None

    for line in unified_diff.splitlines():
        if line.startswith(("--- ", "+++ ")):
            continue

        header_match = _HUNK_HEADER_RE.match(line)
        if header_match:
            if current_old_start is not None:
                updated_lines, cursor = apply_hunk(
                    original_lines,
                    updated_lines,
                    cursor,
                    current_old_start,
                    current_hunk_lines,
                    path,
                )
                current_hunk_lines = []
            current_old_start = int(header_match.group("old_start"))
            continue

        current_hunk_lines.append(line)

    if current_old_start is None:
        raise ValueError(f"Patch for {path} is missing a hunk header")

    updated_lines, cursor = apply_hunk(
        original_lines,
        updated_lines,
        cursor,
        current_old_start,
        current_hunk_lines,
        path,
    )
    updated_lines.extend(original_lines[cursor:])
    updated = "\n".join(updated_lines)
    if original.endswith("\n"):
        updated += "\n"
    return updated


def apply_hunk(
    original_lines: list[str],
    updated_lines: list[str],
    cursor: int,
    old_start: int,
    hunk_lines: list[str],
    path: str,
) -> tuple[list[str], int]:
    target_index = max(old_start - 1, 0)
    if target_index < cursor:
        raise ValueError(f"Patch hunks for {path} are out of order")

    updated_lines.extend(original_lines[cursor:target_index])
    cursor = target_index

    for line in hunk_lines:
        if line.startswith("\\"):
            continue

        prefix, text = line[:1], line[1:]
        if prefix == " ":
            if cursor >= len(original_lines) or original_lines[cursor] != text:
                raise ValueError(f"Patch context mismatch for {path}")
            updated_lines.append(text)
            cursor += 1
            continue

        if prefix == "-":
            if cursor >= len(original_lines) or original_lines[cursor] != text:
                raise ValueError(f"Patch removal mismatch for {path}")
            cursor += 1
            continue

        if prefix == "+":
            updated_lines.append(text)
            continue

        raise ValueError(f"Unsupported patch line for {path}: {line}")

    return updated_lines, cursor


def reject_whole_file_rewrite(original: str, operation: EditOperation) -> None:
    if operation.strategy == "replace" and operation.old_text.rstrip("\n") == original.rstrip("\n"):
        raise ValueError(f"Rejected whole-file rewrite for existing file: {operation.path}")

    if operation.strategy != "patch":
        return

    patch_lines = [
        line
        for line in operation.unified_diff.splitlines()
        if line and not line.startswith(("--- ", "+++ ", "@@"))
    ]
    has_context = any(line.startswith(" ") for line in patch_lines)
    removed_lines = [line for line in patch_lines if line.startswith("-")]
    added_lines = [line for line in patch_lines if line.startswith("+")]
    if not has_context and removed_lines and added_lines and len(removed_lines) >= len(original.splitlines()):
        raise ValueError(f"Rejected whole-file rewrite for existing file: {operation.path}")
