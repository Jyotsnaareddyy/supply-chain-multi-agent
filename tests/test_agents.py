from agents.demand_agent import DemandAgent
from agents.inventory_agent import InventoryAgent
from agents.logistics_agent import LogisticsAgent
from agents.supplier_risk_agent import SupplierRiskAgent
from schemas.recommendation import Recommendation


def test_demand_agent(data):
    rec = DemandAgent(data["demand"], data["customers"]).run("S1_DISRUPTION_01")
    assert isinstance(rec, Recommendation)
    assert rec.agent == "demand"
    assert 0 <= rec.confidence <= 1
    assert rec.recommendation.action


def test_inventory_agent(data):
    rec = InventoryAgent(data["inventory"], data["warehouses"]).run("S1_DISRUPTION_01")
    assert rec.agent == "inventory"
    assert rec.recommendation.quantity is None or rec.recommendation.quantity >= 0


def test_supplier_risk_agent_picks_alternate(data):
    rec = SupplierRiskAgent(data["suppliers"], data["scenarios"]).run("S1_DISRUPTION_01")
    assert rec.recommendation.source != "S1"
    assert rec.recommendation.action == "alternate_source"


def test_logistics_agent(data):
    rec = LogisticsAgent(data["transport"]).run("S1_DISRUPTION_01")
    assert rec.recommendation.action == "expedite"
    assert rec.recommendation.source
