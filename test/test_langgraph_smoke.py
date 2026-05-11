from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_langgraph_builds_and_runs_shipment_path():
    """
    Smoke test: graph compiles and can run one turn without real DB/OpenAI.
    """
    from app.modules.AI.Langgraph.graph import build_graph

    db = AsyncMock()
    graph = build_graph(db)

    fake_shipment = MagicMock()
    fake_shipment.tracking_number = "TRK-TEST0001"
    fake_shipment.status = "CREATED"
    fake_shipment.origin = "NY"
    fake_shipment.destination = "LA"
    fake_shipment.weight = 1.0
    fake_shipment.recipient_name = "Test User"

    class FakeResp:
        content = "ok"

    with patch("app.modules.AI.Langgraph.node.ShipmentRespository") as Repo:
        Repo.return_value.get_by_tracking_number = AsyncMock(return_value=fake_shipment)
        with patch("app.modules.AI.Langgraph.node.llm") as llm:
            llm.ainvoke = AsyncMock(return_value=FakeResp())
            out = await graph.ainvoke(
                {
                    "question": "track shipment TRK-TEST0001",
                    "session_id": "s1",
                    "messages": [],
                }
            )

    assert out["intent"] == "shipment"
    assert "Shipment Details" in out["context"]
    assert out["answer"] == "ok"


@pytest.mark.asyncio
async def test_langgraph_builds_and_runs_policy_path():
    from app.modules.AI.Langgraph.graph import build_graph

    db = AsyncMock()
    graph = build_graph(db)

    class FakeResp:
        content = "policy ok"

    with patch("app.modules.AI.Langgraph.node.semantic_search") as search:
        search.return_value = [{"source": "s", "content": "Some policy text"}]
        with patch("app.modules.AI.Langgraph.node.llm") as llm:
            llm.ainvoke = AsyncMock(return_value=FakeResp())
            out = await graph.ainvoke(
                {
                    "question": "what is your delivery policy?",
                    "session_id": "s1",
                    "messages": [],
                }
            )

    assert out["intent"] == "policy"
    assert "policy" in (out["context"] or "").lower() or "Some policy text" in out["context"]
    assert out["answer"] == "policy ok"

