from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _pyproject() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_wheel_contains_all_runtime_packages_and_agent_cards() -> None:
    cfg = _pyproject()["tool"]["hatch"]["build"]["targets"]["wheel"]

    assert set(cfg["packages"]) >= {
        "agents",
        "bridge",
        "config",
        "gateway",
        "orchestrator",
        "skills",
        "tool",
        "web",
    }
    forced = cfg["force-include"]
    assert forced[".agent/agents"] == ".agent/agents"
    for module in (
        "agent_display.py",
        "agent_paths.py",
        "cli.py",
        "project_context.py",
        "prompt_rules.py",
    ):
        assert forced[module] == module


def test_build_config_does_not_reference_missing_paths() -> None:
    targets = _pyproject()["tool"]["hatch"]["build"]["targets"]

    for target in ("wheel", "sdist"):
        for key in ("packages", "include"):
            for item in targets[target].get(key, []):
                assert (
                    ROOT / item.lstrip("/")
                ).exists(), f"{target}.{key} references missing path: {item}"
    for source in targets["wheel"]["force-include"]:
        assert (ROOT / source).exists(), f"wheel.force-include references missing path: {source}"


def test_requests_is_declared_as_compatible_runtime_dependency() -> None:
    dependencies = _pyproject()["project"]["dependencies"]

    assert any(re.fullmatch(r"requests>=2\.32\.5", dep) for dep in dependencies)
