import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def data() -> dict[str, pd.DataFrame]:
    return {
        name: pd.read_csv(DATA / f"{name}.csv")
        for name in [
            "demand", "suppliers", "warehouses", "customers",
            "inventory", "scenarios", "constraints", "transport",
        ]
    }
