from __future__ import annotations

from pathlib import Path

from orchestrator.main import _agent_dir
from orchestrator.registry import load_cards


def test_agent_cards_are_resolved_independently_of_working_directory(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)

    cards_dir = _agent_dir()
    cards = load_cards(cards_dir)

    assert cards_dir.is_absolute()
    assert {card.id for card in cards} == {"comm-agent", "skill-agent", "tool-agent"}
