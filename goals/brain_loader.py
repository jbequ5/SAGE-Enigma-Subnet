# goals/brain_loader.py — v1.0 Brain Loader (Lean/Rich + Caching)

import os
from typing import Optional
import functools

# Simple in-memory cache for brain components (small files, frequent reads)
_brain_cache = {}

def load_toggle(key: str, default: str = "lean") -> str:
    """Simple toggle parser from brain/toggles.md"""
    try:
        with open("goals/brain/toggles.md", "r", encoding="utf-8") as f:
            content = f.read()
        for line in content.splitlines():
            if line.strip().startswith(f"{key}:"):
                value = line.split(":", 1)[1].strip().strip('"\'')
                return value
        return default
    except:
        return default

def prune_to_dense_lines(content: str, max_lines: int = 12) -> str:
    """Improved lean-mode pruner: keep header + core content, strip examples/comments if too long"""
    lines = content.splitlines()
    if len(lines) <= max_lines:
        return content

    # Keep first few lines (header + intro) + any line containing key terms
    key_terms = ["core", "mandate", "rule", "principle", "evolution", "embodiment", "meta-tuning", "retrospective", "SOTA"]
    dense = []
    for line in lines[:max_lines]:
        dense.append(line)
        if any(term in line.lower() for term in key_terms):
            break

    if len(dense) < max_lines:
        dense.extend(lines[len(dense):max_lines])

    return "\n".join(dense) + "\n... (lean mode — full content in rich mode)"


@functools.lru_cache(maxsize=64)
def load_brain_component(component_path: str, depth: Optional[str] = None) -> str:
    """Lightweight, reusable brain loader with caching and lean/rich support"""
    if depth is None:
        depth = load_toggle("brain_depth", "lean")

    full_path = f"goals/brain/{component_path}.md"
    if not os.path.exists(full_path):
        # Friendly fallback for missing components during transition
        return f"# Missing brain component: {component_path}\n\nThis component will be created automatically on first high-signal run."

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return f"# Error loading brain component {component_path}: {e}"

    if depth == "lean":
        content = prune_to_dense_lines(content)

    return content
