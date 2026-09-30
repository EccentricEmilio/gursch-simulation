import sys
from pathlib import Path

# Add the repository root to Python's import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gursh import engine as gu_engine, state as gu_state

gu_state.create_new_state()