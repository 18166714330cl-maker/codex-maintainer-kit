from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STALE_DAYS = 14
BLOCKER_LABELS = {"bug", "blocker", "regression", "security", "release-blocker"}


@dataclass(frozen=True)
class Item:
    kind: str
    number: int
    title: str
    url: str
    updated_at: datetime
    labels: tuple[str, ...]
    is_draft: bool = False

    @property
    def age_days(self) -> int:
        now = datetime.now(timezone.utc)
        return max(0, (now - self.updated_at).days)

    @property
    def is_stale(self) -> bool:
        return self.age_days >= STALE_DAYS

    @property
    def is_blocker(self) -> bool:
        labels = {label.lower() for label in self.labels}
        return bool(labels & BLOCKER_LABELS)


def parse_time(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def label_names(raw_labels: Any) -> tuple[str, ...]:
    names: list[str] = []
    for label in raw_labels or []:
        if isinstance(label, str):
            names.append(label)
        elif isinstance(label, dict) and label.get("name"):
            names.append(str(label["name"]))
    return tuple(names)


def load_items(path: Path, kind: str) -> list[Item]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    items: list[Item] = []
    for row in raw:
        items.append(
            Item(
                kind=kind,
                number=int(row["number"]),
                title=str(row["title"]),
                url=str(row.get("url", "")),
                updated_at=parse_time(str(row["updatedAt"])),
                labels=label_names(row.get("labels")),
                is_draft=bool(row.get("isDraft", False)),
            )
        )
    return items


def bullet(item: Item) -> str:
    flags: list[str] = []
    if item.is_blocker:
        flags.append("blocker")
    if item.is_stale:
        flags.append(f"stale {item.age_days}d")
    if item.is_draft:
        flags.append("draft")
    suffix = f" ({', '.join(flags)})" if flags else ""
    link = f" [{item.url}]({item.url})" if item.url else ""
    return f"- {item.kind} #{item.number}: {item.title}{suffix}{link}"


def render_digest(repo: str, issues: list[Item], prs: list[Item]) -> str:
    all_items = issues + prs
    blockers = [item for item in all_items if item.is_blocker]
    stale = [item for item in all_items if item.is_stale]
    review_ready = [item for item in prs if not item.is_draft and not item.is_blocker]

    lines = [
        f"# Maintainer Digest: {repo}",
        "",
        "## Summary",
        "",
        f"- Open issues: {len(issues)}",
        f"- Open pull requests: {len(prs)}",
        f"- Blockers: {len(blockers)}",
        f"- Stale items: {len(stale)}",
        "",
        "## First Actions",
        "",
    ]

    if blockers:
        lines.extend(bullet(item) for item in sorted(blockers, key=lambda row: row.updated_at))
    elif review_ready:
        lines.extend(bullet(item) for item in sorted(review_ready, key=lambda row: row.updated_at)[:5])
    elif stale:
        lines.extend(bullet(item) for item in sorted(stale, key=lambda row: row.updated_at)[:5])
    else:
        lines.append("- No urgent maintenance actions found.")

    lines.extend(["", "## Stale Decisions", ""])
    if stale:
        lines.extend(bullet(item) for item in sorted(stale, key=lambda row: row.updated_at))
    else:
        lines.append("- No stale issues or pull requests.")

    lines.extend(["", "## Release Check", ""])
    if blockers:
        lines.append("- Do not cut a release until blockers are resolved.")
    else:
        lines.append("- No blocker labels found in the provided export.")

    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a Markdown maintainer digest.")
    parser.add_argument("--issues", type=Path, default=Path("issues.json"))
    parser.add_argument("--prs", type=Path, default=Path("prs.json"))
    parser.add_argument("--repo", required=True, help="Repository name, for example owner/repo.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    issues = load_items(args.issues, "issue")
    prs = load_items(args.prs, "pr")
    print(render_digest(args.repo, issues, prs), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
