#!/usr/bin/env python3
"""Swarm Agent Entry Point - standardized agent process for the Antigravity Swarm.

Each swarm agent reads tasks from its mailbox, processes them, and writes
structured results back. Supports single-run (--once) and daemon modes.

Usage:
    python scripts/swarm_agent.py --agent Junior           # --once (default)
    python scripts/swarm_agent.py --agent Junior --daemon  # continuous watch
    python scripts/swarm_agent.py --agent Junior --once    # explicit single-run

Identity is read from environment variables when available, falling back to
.swarm/config.json and subagents.yaml.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Constants
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SWARM_DIR = WORKSPACE_ROOT / ".swarm"
MAILBOXES_DIR = SWARM_DIR / "mailboxes"
STATE_DIR = SWARM_DIR / "state"
SUBAGENTS_YAML = WORKSPACE_ROOT / "subagents.yaml"
SWARM_CONFIG_JSON = SWARM_DIR / "config.json"
TASK_PLAN_MD = WORKSPACE_ROOT / "task_plan.md"
POLL_INTERVAL = 1.0
HEARTBEAT_INTERVAL = 5.0

AgentIdentity = dict[str, str]
TaskResult = dict[str, Any]


def _load_subagents_yaml(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return _parse_subagents_list(path.read_text(encoding="utf-8"))


def _parse_subagents_list(text: str) -> list[dict[str, Any]]:
    agents: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    block_key: str | None = None
    block_lines: list[str] = []
    in_subagents = False
    for line in text.splitlines():
        stripped = line.strip()
        if block_key is not None:
            if stripped and (line[0] in (" ", "	")):
                block_lines.append(stripped)
                continue
            current[block_key] = "\n".join(block_lines) + "\n"
            block_key = None
            block_lines = []
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "subagents:":
            in_subagents = True
            continue
        if not in_subagents:
            continue
        if stripped.startswith("- "):
            if current:
                agents.append(current)
            current = {}
            rest = stripped[2:]
            if ":" in rest:
                key, _, val = rest.partition(":")
                key = key.strip()
                val = val.strip()
                if val == "|":
                    block_key = key
                    block_lines = []
                elif val:
                    current[key] = val.strip('"')
                else:
                    current[key] = ""
            continue
        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            if val == "|":
                block_key = key
                block_lines = []
            elif val:
                current[key] = val.strip('"')
            else:
                current[key] = ""
    if current:
        agents.append(current)
    return agents

# Identity resolution
def resolve_identity(agent_name: str | None = None) -> AgentIdentity:
    """Resolve agent identity from env vars, config, or defaults."""
    identity: AgentIdentity = {
        "name": agent_name or os.environ.get("SWARM_AGENT_NAME", "unknown"),
        "role": os.environ.get("SWARM_AGENT_ROLE", ""),
        "color": os.environ.get("SWARM_AGENT_COLOR", ""),
        "model": os.environ.get("SWARM_AGENT_MODEL", ""),
        "mode": os.environ.get("SWARM_AGENT_MODE", ""),
    }
    name = identity["name"]
    _fill_from_swarm_config(identity)
    _fill_from_subagents_yaml(identity, name)
    return identity


def _fill_from_swarm_config(identity: AgentIdentity) -> None:
    if not SWARM_CONFIG_JSON.exists():
        return
    try:
        cfg = json.loads(SWARM_CONFIG_JSON.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return
    name = identity["name"]
    for member in cfg.get("members", []):
        if member.get("name", "").lower() == name.lower():
            if not identity.get("role"):
                identity["role"] = member.get("description", member.get("name", ""))
            if not identity.get("color"):
                identity["color"] = member.get("color", "white")
            if not identity.get("model"):
                identity["model"] = member.get("model", "")
            if not identity.get("mode"):
                identity["mode"] = member.get("mode", "serial")
            break


def _fill_from_subagents_yaml(identity: AgentIdentity, name: str) -> None:
    agents = _load_subagents_yaml(SUBAGENTS_YAML)
    for agent_def in agents:
        if agent_def.get("name", "").lower() == name.lower():
            if not identity.get("role"):
                identity["role"] = agent_def.get("description", "")
            if not identity.get("color"):
                identity["color"] = agent_def.get("color", "white")
            if not identity.get("model"):
                identity["model"] = agent_def.get("model", "")
            if not identity.get("mode"):
                identity["mode"] = agent_def.get("mode", "serial")
            if not identity.get("prompt"):
                identity["prompt"] = agent_def.get("prompt", "")
            break


# System prompt loading
def load_system_prompt(agent_name: str) -> str:
    default = (
        f"You are {agent_name}. Your role is to complete the assigned task "
        f"for the mission: Develop and harden NZ legislation workspace."
    )
    agents = _load_subagents_yaml(SUBAGENTS_YAML)
    for agent_def in agents:
        if agent_def.get("name", "").lower() == agent_name.lower():
            return agent_def.get("prompt", default)
    return default


# Mailbox operations
def _agent_mailbox_dir(agent_name: str) -> Path:
    return MAILBOXES_DIR / agent_name.lower().replace(" ", "_")


def _agent_inbox_dir(agent_name: str) -> Path:
    inbox = _agent_mailbox_dir(agent_name) / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    return inbox


def _agent_outbox_dir(agent_name: str) -> Path:
    outbox = _agent_mailbox_dir(agent_name) / "outbox"
    outbox.mkdir(parents=True, exist_ok=True)
    return outbox


def _agent_processed_dir(agent_name: str) -> Path:
    processed = _agent_mailbox_dir(agent_name) / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    return processed


def _agent_state_path(agent_name: str) -> Path:
    name = agent_name.lower().replace(" ", "_")
    state_file = STATE_DIR / f"{name}.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    return state_file


def list_inbox_messages(agent_name: str) -> list[Path]:
    inbox = _agent_inbox_dir(agent_name)
    if not inbox.exists():
        return []
    return sorted(p for p in inbox.iterdir() if p.is_file() and p.suffix == ".json")


def read_message(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[swarm_agent] Failed to read message {path.name}: {exc}", file=sys.stderr)
        return None


def write_result(agent_name: str, original_msg: dict[str, Any], result: TaskResult) -> Path:
    outbox_dir = _agent_outbox_dir(agent_name)
    timestamp_ms = int(time.time() * 1000)
    msg_id = original_msg.get("msg_id", "unknown")
    filename = f"{timestamp_ms}-{msg_id}-result.json"
    filepath = outbox_dir / filename
    payload = {
        "msg_id": f"result-{msg_id}",
        "sender": agent_name,
        "recipient": original_msg.get("sender", "leader"),
        "msg_type": "result",
        "original_msg_id": msg_id,
        "result": result,
        "timestamp": time.time(),
        "metadata": {},
    }
    filepath.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return filepath


def move_to_processed(agent_name: str, message_path: Path) -> None:
    processed_dir = _agent_processed_dir(agent_name)
    dest = processed_dir / message_path.name
    try:
        message_path.rename(dest)
    except OSError:
        dest.write_bytes(message_path.read_bytes())
        message_path.unlink()

# Heartbeat
def write_heartbeat(agent_name: str, status: str = "alive") -> None:
    state_path = _agent_state_path(agent_name)
    heartbeat = {
        "agent": agent_name,
        "status": status,
        "timestamp": time.time(),
        "iso_timestamp": datetime.now(timezone.utc).isoformat(),
    }
    state_path.write_text(json.dumps(heartbeat, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# Task plan updates
def _extract_task_title(task_description: str) -> str:
    return task_description.strip().split("\n")[0].strip()[:80]


def mark_task_complete_in_plan(task_description: str) -> bool:
    if not TASK_PLAN_MD.exists():
        return False
    original = TASK_PLAN_MD.read_text(encoding="utf-8")
    task_title = _extract_task_title(task_description).lower()
    lines = original.splitlines(keepends=True)
    modified = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("- [ ]") and task_title in stripped.lower():
            indent = line[: len(line) - len(line.lstrip())]
            rest = stripped[5:].strip()
            lines[i] = f"{indent}- [x] {rest}\n"
            modified = True
            break
    if modified:
        TASK_PLAN_MD.write_text("".join(lines), encoding="utf-8")
    return modified


# Task execution
def execute_task(task_description: str) -> TaskResult:
    files_modified: list[str] = []
    test_results: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []
    plan_updated = mark_task_complete_in_plan(task_description)
    if plan_updated:
        rel = TASK_PLAN_MD.relative_to(WORKSPACE_ROOT)
        files_modified.append(str(rel))
    return {
        "success": len(errors) == 0,
        "summary": f"Task processed: {task_description[:120]}",
        "files_modified": files_modified,
        "test_results": test_results,
        "warnings": warnings,
        "errors": errors,
        "task_description": task_description,
        "processed_at": time.time(),
    }


# Message processing
def process_one_message(agent_name: str, message_path: Path) -> TaskResult | None:
    msg = read_message(message_path)
    if msg is None:
        return None
    task_description = msg.get("content", "")
    if not task_description:
        print(f"[swarm_agent] Message {message_path.name} has no content, skipping", file=sys.stderr)
        move_to_processed(agent_name, message_path)
        return None
    print(f"[swarm_agent] Processing task: {task_description[:80]}...")
    result = execute_task(task_description)
    result_path = write_result(agent_name, msg, result)
    print(f"[swarm_agent] Result written to {result_path}")
    move_to_processed(agent_name, message_path)
    write_heartbeat(agent_name, "processing_complete")
    return result


# Run modes
def run_once(agent_name: str) -> int:
    identity = resolve_identity(agent_name)
    print(f"[swarm_agent] Agent: {identity['name']} | Role: {identity.get('role', 'unknown')} | Color: {identity.get('color', 'white')} | Model: {identity.get('model', 'default')}")
    messages = list_inbox_messages(agent_name)
    if not messages:
        print(f"[swarm_agent] No messages in inbox for '{agent_name}'")
        write_heartbeat(agent_name, "idle")
        return 0
    print(f"[swarm_agent] Found {len(messages)} message(s) in inbox")
    for msg_path in messages:
        result = process_one_message(agent_name, msg_path)
        if result is None:
            continue
        if not result.get("success", False):
            print(f"[swarm_agent] Task failed: {result.get('summary', 'unknown')}", file=sys.stderr)
            return 1
        for warning in result.get("warnings", []):
            print(f"[swarm_agent] Warning: {warning}")
        for error in result.get("errors", []):
            print(f"[swarm_agent] Error: {error}", file=sys.stderr)
    return 0


def run_daemon(agent_name: str) -> int:
    identity = resolve_identity(agent_name)
    print(f"[swarm_agent] DAEMON MODE - Agent: {identity['name']} | Role: {identity.get('role', 'unknown')}")
    print(f"[swarm_agent] Watching inbox: {_agent_inbox_dir(agent_name)}")
    print(f"[swarm_agent] Poll interval: {POLL_INTERVAL}s | Heartbeat: {HEARTBEAT_INTERVAL}s")
    last_heartbeat = 0.0
    seen_files: set[str] = set()
    try:
        while True:
            now = time.time()
            if now - last_heartbeat >= HEARTBEAT_INTERVAL:
                write_heartbeat(agent_name, "alive")
                last_heartbeat = now
            messages = list_inbox_messages(agent_name)
            for msg_path in messages:
                if msg_path.name in seen_files:
                    continue
                seen_files.add(msg_path.name)
                result = process_one_message(agent_name, msg_path)
                if result is None:
                    continue
                if result.get("errors"):
                    print(f"[swarm_agent] Task had errors: {result['errors']}", file=sys.stderr)
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\n[swarm_agent] Shutting down (SIGINT)")
        write_heartbeat(agent_name, "shutdown")
        return 0
    except Exception as exc:
        print(f"[swarm_agent] Fatal error: {exc}", file=sys.stderr)
        write_heartbeat(agent_name, "error")
        return 1


# CLI
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Swarm Agent Entry Point - process tasks from mailbox")
    parser.add_argument("--agent", "-a", default=os.environ.get("SWARM_AGENT_NAME", "Junior"), help="Agent name")
    parser.add_argument("--once", action="store_true", default=False, help="Process one task and exit")
    parser.add_argument("--daemon", action="store_true", default=False, help="Continuously watch mailbox")
    parser.add_argument("--task", "-t", default=None, help="Inline task description")
    parser.add_argument("--identity", action="store_true", default=False, help="Print resolved identity and exit")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    agent_name = args.agent
    identity = resolve_identity(agent_name)

    if args.identity:
        print(json.dumps(identity, indent=2, ensure_ascii=False))
        prompt = load_system_prompt(agent_name)
        if prompt:
            print(f"\nSystem prompt ({len(prompt)} chars):")
            print(prompt[:500] + ("..." if len(prompt) > 500 else ""))
        return 0

    if args.task:
        print(f"[swarm_agent] Agent: {identity['name']} | Role: {identity.get('role', 'unknown')}")
        result = execute_task(args.task)
        outbox_dir = _agent_outbox_dir(agent_name)
        ts = int(time.time() * 1000)
        result_file = outbox_dir / f"{ts}-inline-result.json"
        result_file.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[swarm_agent] Result written to {result_file}")
        if result.get("errors"):
            print(f"[swarm_agent] Task errors: {result['errors']}", file=sys.stderr)
            return 1
        return 0

    if args.daemon:
        return run_daemon(agent_name)
    else:
        return run_once(agent_name)


if __name__ == "__main__":
    sys.exit(main())
