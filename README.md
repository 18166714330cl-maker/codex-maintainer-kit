# Codex Maintainer Kit

A small command line toolkit for open-source maintainers who need a quick daily
view of issue and pull request work.

The first tool, `maintainer-digest`, reads JSON exported from GitHub CLI and
turns it into a concise Markdown digest:

- urgent issues and pull requests
- stale items that need a decision
- release blockers
- a short "next actions" checklist

This project is intentionally lightweight. It is designed for solo maintainers
and small projects that do not need a dashboard server.

## Install

```bash
python -m pip install .
```

## Usage

Export issues or pull requests with GitHub CLI:

```bash
gh issue list --repo owner/repo --state open --json number,title,labels,updatedAt,url > issues.json
gh pr list --repo owner/repo --state open --json number,title,labels,updatedAt,url,isDraft > prs.json
```

Generate a digest:

```bash
maintainer-digest --issues issues.json --prs prs.json --repo owner/repo
```

## Example

```bash
maintainer-digest --issues examples/issues.json --prs examples/prs.json --repo demo/project
```

## License

MIT
