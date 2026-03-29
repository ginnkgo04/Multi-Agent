from __future__ import annotations

from copy import deepcopy
from typing import Any


class ContextBudgeter:
    def __init__(self, char_budget: int = 8000) -> None:
        self.char_budget = char_budget

    def apply(self, context_sources: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        budgeted = [deepcopy(source) for source in context_sources]
        for index, source in enumerate(budgeted):
            source.setdefault("order_index", index)
            source.setdefault("included", True)
        initial_chars = sum(self._char_count(source) for source in budgeted)
        removed_items: list[dict[str, Any]] = []
        trimmed_items: list[dict[str, Any]] = []
        if initial_chars <= self.char_budget:
            return budgeted, self._metadata(initial_chars, initial_chars, removed_items, trimmed_items)

        for section in ("recent_memories", "cycle_summaries"):
            self._drop_section_items(budgeted, section, removed_items)
            if sum(self._char_count(source) for source in budgeted if source.get("included")) <= self.char_budget:
                break

        if sum(self._char_count(source) for source in budgeted if source.get("included")) > self.char_budget:
            self._drop_low_score_retrieved_docs(budgeted, removed_items)

        if sum(self._char_count(source) for source in budgeted if source.get("included")) > self.char_budget:
            self._trim_artifact_previews(budgeted, trimmed_items)

        final_chars = sum(self._char_count(source) for source in budgeted if source.get("included"))
        return budgeted, self._metadata(initial_chars, final_chars, removed_items, trimmed_items)

    def _drop_section_items(self, sources: list[dict[str, Any]], section: str, removed_items: list[dict[str, Any]]) -> None:
        for source in sources:
            if source.get("section") != section or not source.get("included", True):
                continue
            source["included"] = False
            removed_items.append(
                {
                    "section": section,
                    "source_id": source.get("source_id"),
                    "path": source.get("path"),
                }
            )

    def _drop_low_score_retrieved_docs(self, sources: list[dict[str, Any]], removed_items: list[dict[str, Any]]) -> None:
        retrieved = sorted(
            [source for source in sources if source.get("section") == "retrieved_docs" and source.get("included", True)],
            key=lambda item: item.get("score") if item.get("score") is not None else -1.0,
        )
        for source in retrieved:
            if sum(self._char_count(item) for item in sources if item.get("included")) <= self.char_budget:
                return
            source["included"] = False
            removed_items.append(
                {
                    "section": "retrieved_docs",
                    "source_id": source.get("source_id"),
                    "path": source.get("path"),
                    "score": source.get("score"),
                }
            )

    def _trim_artifact_previews(self, sources: list[dict[str, Any]], trimmed_items: list[dict[str, Any]]) -> None:
        artifact_sources = [source for source in sources if source.get("section") == "upstream_artifacts" and source.get("included", True)]
        for source in artifact_sources:
            current_total = sum(self._char_count(item) for item in sources if item.get("included"))
            if current_total <= self.char_budget:
                return
            overflow = current_total - self.char_budget
            excerpt = str(source.get("excerpt", ""))
            minimum = 24
            if len(excerpt) <= minimum:
                continue
            new_length = max(minimum, len(excerpt) - overflow)
            if new_length >= len(excerpt):
                continue
            source["excerpt"] = excerpt[:new_length]
            trimmed_items.append(
                {
                    "section": "upstream_artifacts",
                    "source_id": source.get("source_id"),
                    "path": source.get("path"),
                    "new_length": new_length,
                }
            )

    @staticmethod
    def _char_count(source: dict[str, Any]) -> int:
        if not source.get("included", True):
            return 0
        excerpt = str(source.get("excerpt", ""))
        metadata = str(source.get("metadata", {}))
        return len(excerpt) + len(metadata)

    def _metadata(
        self,
        initial_chars: int,
        final_chars: int,
        removed_items: list[dict[str, Any]],
        trimmed_items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "char_budget": self.char_budget,
            "initial_chars": initial_chars,
            "final_chars": final_chars,
            "removed_items": removed_items,
            "trimmed_items": trimmed_items,
        }
