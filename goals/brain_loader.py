# goals/brain_loader.py
import os
from typing import Optional

def load_toggle(key: str, default: str = "lean") -> str:
    """Simple toggle parser from brain/toggles.md"""
    try:
        with open("goals/brain/toggles.md", "r") as f:
            content = f.read()
        for line in content.splitlines():
            if line.strip().startswith(f"{key}:"):
                return line.split(":", 1)[1].strip().strip('"\'')
        return default
    except:
        return default

def prune_to_dense_lines(content: str, max_lines: int = 12) -> str:
    """Basic lean-mode pruner: keep first N lines + shared_core reference"""
    lines = content.splitlines()
    # Simple heuristic - keep header + core content, strip examples/comments if too long
    if len(lines) > max_lines:
        return "\n".join(lines[:max_lines]) + "\n... (lean mode - full in rich)"
    return content

def load_brain_component(component_path: str, depth: Optional[str] = None) -> str:
    """Lightweight, reusable brain loader — reuses existing expert loading style"""
    if depth is None:
        depth = load_toggle("brain_depth")
    
    full_path = f"goals/brain/{component_path}.md"
    if not os.path.exists(full_path):
        # Fallback for backward compatibility during transition
        return f"# Missing brain component: {component_path}"
    
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if depth == "lean":
        content = prune_to_dense_lines(content)
    
    return content
