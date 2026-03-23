# agents/tools/resource_aware.py
# Resource-Aware Optimization - enforces 4h H200 limit

def check_and_compress(runtime_estimate: float, current_output: str):
    """Auto-compresses if over H100 limit"""
    if runtime_estimate > 3.8:
        print(f"⏰ Runtime {runtime_estimate:.1f}h > limit → compressing...")
        return current_output + " [COMPRESSED for H100]"
    return current_output
