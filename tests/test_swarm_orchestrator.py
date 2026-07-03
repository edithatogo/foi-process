#!/usr/bin/env python3
"""Tests for swarm task-plan parsing and gated dispatch behavior."""

from __future__ import annotations

from scripts import swarm_orchestrator as m


def test_parse_task_plan_marks_blocked_followup_lines():
    tracks = m._parse_task_plan_text(
        "\n".join(
            [
                "## Phase 3: Deployment",
                "- [ ] Task: Verify active accounts via `gh auth status` and sync `.env` files.",
                "  - External-write gate: requires user approval",
                "- [ ] Task: Run local schema validator.",
                "",
            ]
        )
    )

    assert len(tracks) == 1
    blocked, dispatchable = tracks[0].tasks
    assert blocked.blocked
    assert "External-write gate" in blocked.block_reason
    assert not dispatchable.blocked


def test_blocked_tasks_are_not_assigned_to_gate_lanes():
    task = m.TrackTask(
        description="Task: Commit and push changes to GitHub origin.",
        completed=False,
        track_name="Phase 3: Deployment",
        track_number=10,
        blocked=True,
        block_reason="Blocked: requires user approval",
    )
    track = m.Track(name="Phase 3: Deployment", number=10, tasks=[task])

    assert m._task_gate_lane(task, ["Quality_Validator"]) is None
    assert m._assign_track_to_agent(track, task, ["Quality_Validator"]) is None


def test_parse_swarm_presets_includes_mimo_lane():
    cfg = m._load_swarm_config(m.SWARM_CONFIG_YAML)

    assert cfg is not None
    assert "track_swarm" in cfg.presets
    agents = cfg.presets["track_swarm"]["agents"]
    assert any(agent["name"] == "Xiaomi_MiMo_Code" for agent in agents)


def test_cli_docs_tasks_prefer_mimo_lane():
    task = m.TrackTask(
        description="Task: Implement Astro docs command migration in one repo.",
        completed=False,
        track_name="Astro Documentation Standard",
        track_number=29,
    )
    track = m.Track(name="Astro Documentation Standard", number=29, tasks=[task])

    assert m._assign_track_to_agent(
        track,
        task,
        ["General_Coder", "Xiaomi_MiMo_Code", "Codex_GPT55_Engineer"],
    ) == "Xiaomi_MiMo_Code"


def test_gate_lanes_do_not_accept_generic_local_fallback():
    assert not m._agent_accepts_local_fallback("Chrome_Operator")
    assert not m._agent_accepts_local_fallback("Quality_Validator")
    assert m._agent_accepts_local_fallback("General_Coder")


def test_task_content_includes_assigned_model():
    agent = m.AgentSpec(
        name="Xiaomi_MiMo_Code",
        description="Implementation lane",
        color="orange",
        model="xiaomi-mimo-code",
        mode="parallel",
        prompt="",
    )
    task = m.TrackTask(
        description="Task: Add docs command migration.",
        completed=False,
        track_name="Astro Documentation Standard",
        track_number=29,
    )
    track = m.Track(name="Astro Documentation Standard", number=29, tasks=[task])

    content = m._build_task_content(track, task, agent)

    assert "Xiaomi_MiMo_Code" in content
    assert "xiaomi-mimo-code" in content
    assert "Use Astro/Starlight" in content
