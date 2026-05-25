"""Path and slug helpers shared by roadmap delivery tools."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Dict, Iterable, List, Optional, TypeVar


T = TypeVar("T")


def unique(items: Iterable[T]) -> List[T]:
    seen = set()
    out: List[T] = []
    for item in items:
        if item not in seen:
            out.append(item)
            seen.add(item)
    return out


def unique_paths(paths: Iterable[Path]) -> List[Path]:
    seen = set()
    out: List[Path] = []
    for path in paths:
        key = str(path)
        if key not in seen:
            out.append(path)
            seen.add(key)
    return out


def slug_forms(slug: Optional[str]) -> Dict[str, Optional[str]]:
    if not slug:
        return {"input": None, "dash": None, "dir": None}
    return {
        "input": slug,
        "dash": slug.replace("_", "-"),
        "dir": slug.replace("-", "_"),
    }


def resolve_repo_path(repo_root: Path, value: Optional[str]) -> Optional[Path]:
    if not value:
        return None
    path = Path(str(value)).expanduser()
    if path.is_absolute():
        return path
    return repo_root / path


def path_for_report(path: Optional[Path]) -> Optional[str]:
    return str(path) if path is not None else None


def state_candidates(repo_root: Path, forms: Dict[str, Optional[str]]) -> List[Path]:
    candidates: List[Path] = []
    for slug in unique([item for item in (forms.get("dir"), forms.get("dash")) if item]):
        candidates.append(repo_root / "roadmaps" / "automation" / slug / "delivery_state.json")
        candidates.append(repo_root / "automation" / slug / "delivery_state.json")
    return unique_paths(candidates)


def automation_dir_candidates(repo_root: Path, forms: Dict[str, Optional[str]]) -> List[Path]:
    candidates: List[Path] = []
    for slug in unique([item for item in (forms.get("dir"), forms.get("dash")) if item]):
        candidates.append(repo_root / "roadmaps" / "automation" / slug)
        candidates.append(repo_root / "automation" / slug)
    return unique_paths(candidates)


def extract_roadmap_references(
    prompt: str,
    repo_root: Path,
    *,
    require_roadmap_suffix: bool = False,
) -> List[Path]:
    refs: List[Path] = []
    patterns = (
        r"/Users/[^`'\"\s]+?\.md",
        r"roadmaps/[^`'\"\s]+?\.md",
    )
    for pattern in patterns:
        for match in re.findall(pattern, prompt):
            path = Path(match)
            if require_roadmap_suffix:
                if not (path.name == "roadmap.md" or path.name.endswith("_roadmap.md")):
                    continue
            elif "roadmap" not in path.name:
                continue
            if not path.is_absolute():
                path = repo_root / path
            if path not in refs:
                refs.append(path)
    return refs


def package_repo_root(start: Optional[Path] = None) -> Optional[Path]:
    path = (start or Path(__file__)).resolve()
    for parent in [path.parent, *path.parents]:
        if (parent / "schemas").is_dir() and (parent / "skill").is_dir():
            return parent
    return None
