#!/usr/bin/env python3
"""Unit tests for scripts/swarm_agent.py - Swarm Agent Entry Point."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = WORKSPACE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def _patch_env(monkeypatch):
    for k in ("SWARM_AGENT_NAME","SWARM_AGENT_ROLE","SWARM_AGENT_COLOR","SWARM_AGENT_MODEL","SWARM_AGENT_MODE"):
        monkeypatch.delenv(k, raising=False)


class TestResolveIdentity:
    def test_default(self, monkeypatch):
        _patch_env(monkeypatch)
        from scripts import swarm_agent as m
        assert m.resolve_identity()["name"] == "unknown"

    def test_env_vars(self, monkeypatch):
        _patch_env(monkeypatch)
        monkeypatch.setenv("SWARM_AGENT_NAME","Bot")
        monkeypatch.setenv("SWARM_AGENT_ROLE","tester")
        monkeypatch.setenv("SWARM_AGENT_COLOR","blue")
        from scripts import swarm_agent as m
        i = m.resolve_identity("Bot")
        assert i["name"] == "Bot"
        assert i["role"] == "tester"
        assert i["color"] == "blue"

    def test_subagents_yaml(self, monkeypatch):
        _patch_env(monkeypatch)
        from scripts import swarm_agent as m
        i = m.resolve_identity("Xiaomi_MiMo_Code")
        assert i["name"] == "Xiaomi_MiMo_Code"
        assert i["color"] == "orange"
        assert i["model"] == "xiaomi-mimo-code"
        assert i["mode"] == "parallel"

    def test_junior_subagents_yaml(self, monkeypatch):
        _patch_env(monkeypatch)
        from scripts import swarm_agent as m
        i = m.resolve_identity("Junior")
        assert i["model"] == "deepseek-v4-flash"
        assert i["mode"] == "parallel"
        assert "do the work" in i.get("prompt","")


class TestSystemPrompt:
    def test_junior(self):
        from scripts import swarm_agent as m
        p = m.load_system_prompt("Junior")
        assert "do the work" in p

    def test_oracle(self):
        from scripts import swarm_agent as m
        p = m.load_system_prompt("Oracle")
        assert "deep architectural insights" in p

    def test_unknown(self):
        from scripts import swarm_agent as m
        p = m.load_system_prompt("X")
        assert "X" in p


class TestMailbox:
    def test_inbox_created(self, tmp_path):
        from scripts import swarm_agent as m
        o = m.MAILBOXES_DIR; m.MAILBOXES_DIR = tmp_path / "mb"
        try:
            assert m._agent_inbox_dir("A").exists()
        finally:
            m.MAILBOXES_DIR = o

    def test_list_empty(self, tmp_path):
        from scripts import swarm_agent as m
        o = m.MAILBOXES_DIR; m.MAILBOXES_DIR = tmp_path / "mb"
        try:
            assert m.list_inbox_messages("A") == []
        finally:
            m.MAILBOXES_DIR = o

    def test_list_with_files(self, tmp_path):
        from scripts import swarm_agent as m
        o = m.MAILBOXES_DIR; m.MAILBOXES_DIR = tmp_path / "mb"
        try:
            (m._agent_inbox_dir("A") / "b.json").write_text("{}")
            (m._agent_inbox_dir("A") / "a.json").write_text("{}")
            msgs = m.list_inbox_messages("A")
            assert len(msgs) == 2
            assert msgs[0].name == "a.json"
        finally:
            m.MAILBOXES_DIR = o

    def test_read_valid(self, tmp_path):
        from scripts import swarm_agent as m
        f = tmp_path / "m.json"
        f.write_text(json.dumps({"msg_id":"abc","content":"do"}))
        assert m.read_message(f)["msg_id"] == "abc"

    def test_read_invalid(self, tmp_path):
        from scripts import swarm_agent as m
        f = tmp_path / "b.json"
        f.write_text("bad")
        assert m.read_message(f) is None

    def test_write_result(self, tmp_path):
        from scripts import swarm_agent as m
        o = m.MAILBOXES_DIR; m.MAILBOXES_DIR = tmp_path / "mb"
        try:
            p = m.write_result("A", {"msg_id":"t1","sender":"L"}, {"ok":True})
            assert p.exists()
            d = json.loads(p.read_text())
            assert d["msg_type"] == "result"
            assert d["original_msg_id"] == "t1"
        finally:
            m.MAILBOXES_DIR = o

    def test_move_processed(self, tmp_path):
        from scripts import swarm_agent as m
        o = m.MAILBOXES_DIR; m.MAILBOXES_DIR = tmp_path / "mb"
        try:
            f = m._agent_inbox_dir("A") / "m.json"
            f.write_text("{}")
            m.move_to_processed("A", f)
            assert (m._agent_processed_dir("A") / "m.json").exists()
            assert not f.exists()
        finally:
            m.MAILBOXES_DIR = o


class TestHeartbeat:
    def test_writes(self, tmp_path):
        from scripts import swarm_agent as m
        o = m.STATE_DIR; m.STATE_DIR = tmp_path / "st"
        try:
            m.write_heartbeat("B", "alive")
            d = json.loads((tmp_path / "st" / "b.json").read_text())
            assert d["agent"] == "B"
            assert d["status"] == "alive"
        finally:
            m.STATE_DIR = o


class TestTaskPlan:
    def test_marks(self, tmp_path):
        from scripts import swarm_agent as m
        o = m.TASK_PLAN_MD; pf = tmp_path / "p.md"
        pf.write_text("- [ ] Do it" + chr(10) + "- [ ] Other" + chr(10))
        m.TASK_PLAN_MD = pf
        try:
            assert m.mark_task_complete_in_plan("Do it")
            txt = pf.read_text()
            assert "- [x] Do it" in txt
            assert "- [ ] Other" in txt
        finally:
            m.TASK_PLAN_MD = o

    def test_no_match(self, tmp_path):
        from scripts import swarm_agent as m
        o = m.TASK_PLAN_MD; pf = tmp_path / "p.md"
        pf.write_text("- [ ] X" + chr(10))
        m.TASK_PLAN_MD = pf
        try:
            assert not m.mark_task_complete_in_plan("Y")
        finally:
            m.TASK_PLAN_MD = o

    def test_no_file(self):
        from scripts import swarm_agent as m
        assert not m.mark_task_complete_in_plan("Any")


class TestExecuteTask:
    def test_structure(self):
        from scripts import swarm_agent as m
        r = m.execute_task("Test")
        assert r["success"]
        for k in ("summary","files_modified","test_results","warnings","errors","task_description","processed_at"):
            assert k in r


class TestCLI:
    def test_default(self):
        from scripts import swarm_agent as m
        assert m.build_parser().parse_args([]).agent == "Junior"

    def test_custom(self):
        from scripts import swarm_agent as m
        assert m.build_parser().parse_args(["--agent","O"]).agent == "O"

    def test_once(self):
        from scripts import swarm_agent as m
        assert m.build_parser().parse_args(["--once"]).once

    def test_daemon(self):
        from scripts import swarm_agent as m
        assert m.build_parser().parse_args(["--daemon"]).daemon

    def test_task(self):
        from scripts import swarm_agent as m
        assert m.build_parser().parse_args(["--task","Do"]).task == "Do"

    def test_identity(self):
        from scripts import swarm_agent as m
        assert m.build_parser().parse_args(["--identity"]).identity


class TestProcessMsg:
    def test_skip_empty(self, tmp_path):
        from scripts import swarm_agent as m
        o = m.MAILBOXES_DIR; m.MAILBOXES_DIR = tmp_path / "mb"
        try:
            f = m._agent_inbox_dir("A") / "e.json"
            f.write_text(json.dumps({"msg_id":"e1","content":""}))
            assert m.process_one_message("A", f) is None
            assert (m._agent_processed_dir("A") / "e.json").exists()
        finally:
            m.MAILBOXES_DIR = o

    def test_valid(self, tmp_path):
        from scripts import swarm_agent as m
        o = m.MAILBOXES_DIR; m.MAILBOXES_DIR = tmp_path / "mb"
        try:
            f = m._agent_inbox_dir("A") / "t.json"
            f.write_text(json.dumps({"msg_id":"t1","sender":"L","content":"Do"}))
            r = m.process_one_message("A", f)
            assert r is not None
            assert r["success"]
            assert len(list(m._agent_outbox_dir("A").glob("*t1*result*"))) == 1
        finally:
            m.MAILBOXES_DIR = o


class TestYAML:
    def test_parses(self):
        from scripts import swarm_agent as m
        agents = m._load_subagents_yaml(m.SUBAGENTS_YAML)
        assert len(agents) >= 4
        names = [a["name"] for a in agents]
        for n in ("Oracle","Frontend","Junior","Quality_Validator","Xiaomi_MiMo_Code"):
            assert n in names

    def test_attributes(self):
        from scripts import swarm_agent as m
        agents = m._load_subagents_yaml(m.SUBAGENTS_YAML)
        jr = next(a for a in agents if a["name"] == "Junior")
        assert jr["color"] == "yellow"
        assert jr["model"] == "deepseek-v4-flash"
        assert jr["mode"] == "parallel"
        assert "You are Junior" in jr["prompt"]
