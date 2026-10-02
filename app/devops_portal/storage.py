"""Load and save the portal's data as a JSON file.

The data is one dictionary with two lists:
    {"members": [...], "services": [...]}
"""

import json
import os
from pathlib import Path

# Where data is kept unless the PORTAL_DATA environment variable says otherwise.
DEFAULT_PATH = Path.home() / ".devops-portal.json"


def data_path():
    """Return the path of the data file."""
    return Path(os.environ.get("PORTAL_DATA", DEFAULT_PATH))


def empty_data():
    """Return the data for a brand-new portal."""
    return {"members": [], "services": []}


def load(path=None):
    """Read the data file. Returns empty data if the file doesn't exist yet."""
    path = Path(path) if path else data_path()
    if not path.exists():
        return empty_data()

    with path.open(encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as err:
            raise ValueError(f"Data file {path} is not valid JSON: {err}") from err

    # Older or hand-edited files may be missing a key, so fill in the gaps.
    for key, value in empty_data().items():
        data.setdefault(key, value)
    return data


def save(data, path=None):
    """Write the data file, creating its folder if needed."""
    path = Path(path) if path else data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
