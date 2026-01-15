"""Asset data loaders."""

import json
import sys
from pathlib import Path
from config import DEFAULT_ASSETS_FILE


def load_assets(file_path=None):
    """Load assets from JSON file."""
    if file_path is None:
        file_path = DEFAULT_ASSETS_FILE
    else:
        file_path = Path(file_path)

    if not file_path.exists():
        print(f"Error: Assets file not found: {file_path}")
        sys.exit(1)

    with open(file_path, 'r') as f:
        return json.load(f)
