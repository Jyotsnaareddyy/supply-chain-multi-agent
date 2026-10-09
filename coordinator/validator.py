"""Validate recommendations against capacity/service/budget constraints."""
from __future__ import annotations

import pandas as pd

from schemas.recommendation import Recommendation


class Validator:
    def __init__(self, suppliers: pd.DataFrame, warehouses: pd.DataFrame, constraints: pd.DataFrame):
        self.suppliers = suppliers.set_index("supplier_id")
        self.warehouses = warehouses.set_index("warehouse_id")
        self.constraints = constraints.iloc[0]

    def validate(self, rec: Recommendation) -> tuple[bool, str]:
        payload = rec.recommendation
        if payload.quantity is not None and payload.quantity < 0:
            return False, "negative quantity"

        if payload.source in self.suppliers.index and payload.quantity:
            cap = self.suppliers.loc[payload.source, "capacity"]
            if payload.quantity > cap:
                return False, f"exceeds supplier capacity ({cap})"

        if payload.destination in self.warehouses.index and payload.quantity:
            cap = self.warehouses.loc[payload.destination, "capacity"]
            if payload.quantity > cap:
                return False, f"exceeds warehouse capacity ({cap})"

        if payload.action == "expedite" and payload.quantity:
            if payload.quantity > self.constraints["max_expedite"]:
                return False, "exceeds max expedite quantity"

        return True, "ok"
