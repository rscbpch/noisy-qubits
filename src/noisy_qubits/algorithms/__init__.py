from .superposition import run as run_superposition

# Register algorithms here as they are added (plan section 3).
REGISTRY = {"superposition": run_superposition}
