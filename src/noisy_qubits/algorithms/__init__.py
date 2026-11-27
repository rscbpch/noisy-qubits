from .deutsch_jozsa import run as run_deutsch_jozsa
from .qft import run as run_qft
from .superposition import run as run_superposition

# Register algorithms here as they are added (plan section 3).
REGISTRY = {
    "superposition": run_superposition,
    "deutsch_jozsa": run_deutsch_jozsa,
    "qft": run_qft,
}