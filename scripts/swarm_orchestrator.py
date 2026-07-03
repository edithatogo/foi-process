#!/usr/bin/env python3
"""Swarm Orchestrator - Production-grade mission coordinator.

Reads swarm-config.yaml, subagents.yaml, .swarm/config.json, and task_plan.md
to discover pending work, dispatch tasks to agent mailboxes, monitor lifecycle
(heartbeats, timeouts), and track progress in .swarm/state.json.

Usage:
    python scripts/swarm_orchestrator.py              # run the full cycle
    python scripts/swarm_orchestrator.py --dry-run    # preview without dispatching
    python scripts/swarm_orchestrator.py --once       # single dispatch pass then exit
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# -------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SWARM_DIR = WORKSPACE_ROOT / ".swarm"
MAILBOXES_DIR = SWARM_DIR / "mailboxes"
STATE_PATH = SWARM_DIR / "state.json"
CONFIG_JSON_PATH = SWARM_DIR / "config.json"
MISSIONS_DIR = SWARM_DIR / "missions"
AUDIT_DIR = SWARM_DIR / "audit"

SUBAGENTS_YAML = WORKSPACE_ROOT / "subagents.yaml"
SWARM_CONFIG_YAML = WORKSPACE_ROOT / "swarm-config.yaml"
TASK_PLAN_MD = WORKSPACE_ROOT / "task_plan.md"

HEARTBEAT_STALE_SECONDS = 30.0
POLL_INTERVAL = 1.0
DEFAULT_TIMEOUT = 300.0

# -------------------------------------------------------------------------
# Data types
# -------------------------------------------------------------------------


@dataclass
class TrackTask:
    """A single task item parsed from the task plan."""
    description: str
    completed: bool
    track_name: str
    track_number: int
    assigned_agent: str | None = None
    blocked: bool = False
    block_reason: str = ""


@dataclass
class Track:
    """A named track (section) from the task plan."""
    name: str
    number: int
    tasks: list[TrackTask] = field(default_factory=list)
    completed: bool = False


@dataclass
class AgentSpec:
    """Agent specification from subagents.yaml."""
    name: str
    description: str
    color: str
    model: str
    mode: str
    prompt: str


@dataclass
class SwarmConfig:
    """Runtime swarm configuration."""
    version: int
    backend: str
    default_model: str
    engine: str
    max_parallel: int
    poll_interval_ms: int
    permission_mode: str
    audit_enabled: bool
    tui_refresh_rate: int
    compaction_threshold: int
    presets: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    """Runtime state of one agent."""
    name: str
    status: str
    current_task: str | None = None
    task_started_at: float | None = None
    last_heartbeat: float | None = None
    error_count: int = 0


@dataclass
class MissionState:
    """Full mission state persisted to state.json."""
    mission_id: str
    description: str
    started_at: float
    status: str
    agents: list[AgentState] = field(default_factory=list)
    completed_tasks: list[str] = field(default_factory=list)
    current_track_index: int = 0
    updated_at: float = 0.0
    ended_at: float | None = None
    failure_reason: str = ""


@dataclass
class MailboxMessage:
    """A message placed into an agent mailbox."""
    msg_id: str
    sender: str
    recipient: str
    msg_type: str
    content: str
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)

# -------------------------------------------------------------------------
# YAML Parser (no PyYAML dependency)
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# YAML Parser (no PyYAML dependency)
# -------------------------------------------------------------------------

def _parse_yaml_simple(text: str) -> list[dict[str, Any]]:
    """Parse a simple YAML list-of-mappings document."""
    items: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    block_key: str | None = None
    block_lines: list[str] = []
    in_top_list = False
    for line in text.splitlines():
        stripped = line.strip()
        if block_key is not None:
            if stripped and (line[0] == " " or line[0] == "\t"):
                block_lines.append(stripped)
                continue
            else:
                current[block_key] = "\n".join(block_lines) + "\n"
                block_key = None
                block_lines = []
        if not stripped or stripped.startswith("#"):
            continue
        if not stripped.startswith("- ") and ":" in stripped and not in_top_list:
            key, _, val = stripped.partition(":"); key = key.strip(); val = val.strip()
            if val == "|": block_key = key; block_lines = []
            continue
        if stripped.startswith("- "):
            if current: items.append(current)
            current = {}; in_top_list = True
            rest = stripped[2:]
            if ":" in rest:
                key, _, val = rest.partition(":"); key = key.strip(); val = val.strip()
                if val == "|": block_key = key; block_lines = []
                elif val: current[key] = val
                else: current[key] = ""
            continue
        if ":" in stripped:
            key, _, val = stripped.partition(":"); key = key.strip(); val = val.strip()
            if val == "|": block_key = key; block_lines = []
            elif val: current[key] = val
            else: current[key] = ""
    if current: items.append(current)
    return items


def _parse_yaml_top_mapping(text: str) -> dict[str, Any]:
    """Parse a simple YAML top-level mapping (swarm-config style)."""
    result: dict[str, Any] = {}
    block_key: str | None = None; block_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if block_key is not None:
            if stripped and (line[0] == " " or line[0] == "\t"):
                block_lines.append(stripped); continue
            else:
                result[block_key] = "\n".join(block_lines) + "\n"
                block_key = None; block_lines = []
        if not stripped or stripped.startswith("#"): continue
        if ":" in stripped:
            key, _, val = stripped.partition(":"); key = key.strip(); val = val.strip()
            if val == "|": block_key = key; block_lines = []
            elif val: result[key] = val
    return result

# -------------------------------------------------------------------------
# Config loaders
# -------------------------------------------------------------------------



def _unquote(s: str) -> str:
    """Strip matching single or double quotes from a string."""
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


def _load_subagents(path: Path) -> list[AgentSpec]:
    if not path.exists(): return []
    text = path.read_text(encoding="utf-8")
    items = _parse_yaml_simple(text)
    agents: list[AgentSpec] = []
    for item in items:
        agents.append(AgentSpec(name=_unquote(item.get("name","Unknown")),
            description=_unquote(item.get("description","")),
            color=_unquote(item.get("color","white")),
            model=_unquote(item.get("model","")),
            mode=_unquote(item.get("mode","parallel")),
            prompt=_unquote(item.get("prompt",""))))
    return agents


def _load_swarm_config(path: Path) -> SwarmConfig | None:
    if not path.exists(): return None
    text = path.read_text(encoding="utf-8")
    m = _parse_yaml_top_mapping(text)
    return SwarmConfig(version=int(m.get("version",1)),
        backend=str(m.get("backend","thread")),
        default_model=str(m.get("default_model","deepseek-v4-flash")),
        engine=str(m.get("engine","cline")),
        max_parallel=int(m.get("max_parallel",8)),
        poll_interval_ms=int(m.get("poll_interval_ms",1000)),
        permission_mode=str(m.get("permission_mode","auto")),
        audit_enabled=str(m.get("audit_enabled","true")).lower()=="true",
        tui_refresh_rate=int(m.get("tui_refresh_rate",10)),
        compaction_threshold=int(m.get("compaction_threshold",50)),
        presets=_parse_swarm_presets(text))


def _parse_swarm_presets(text: str) -> dict[str, Any]:
    """Parse the small swarm-config preset shape used by this repo."""
    presets: dict[str, Any] = {}
    current_preset: str | None = None
    in_presets = False
    in_agents = False
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()
        if stripped == "presets:":
            in_presets = True
            current_preset = None
            in_agents = False
            continue
        if not in_presets:
            continue
        if indent == 2 and stripped.endswith(":"):
            current_preset = stripped[:-1]
            presets[current_preset] = {"agents": []}
            in_agents = False
            continue
        if current_preset is None:
            continue
        if indent == 4 and stripped.startswith("description:"):
            _, _, val = stripped.partition(":")
            presets[current_preset]["description"] = _unquote(val.strip())
            continue
        if indent == 4 and stripped == "agents:":
            in_agents = True
            continue
        if in_agents and stripped.startswith("- {") and stripped.endswith("}"):
            body = stripped[3:-1]
            agent: dict[str, str] = {}
            for part in body.split(","):
                key, _, val = part.partition(":")
                if key and val:
                    agent[key.strip()] = _unquote(val.strip())
            if agent:
                presets[current_preset]["agents"].append(agent)
    return presets


def _load_config_json(path: Path) -> dict[str, Any] | None:
    if not path.exists(): return None
    return json.loads(path.read_text(encoding="utf-8"))

# -------------------------------------------------------------------------
# Task plan parser
# -------------------------------------------------------------------------

TRACK_HEADER_RE = re.compile(r"^##\s+Track\s+(\d+):\s+(.+?)(?:\s+\u2705\s*(\w+))?\s*$", re.IGNORECASE)
PHASE_HEADER_RE = re.compile(r"^##\s+Phase\s+(\d+):\s+(.+?)\s*$", re.IGNORECASE)
TASK_ITEM_RE = re.compile(r"^\s*-\s+(\[ \]|\[x])\s+(.+)$")
AGENT_TAG_RE = re.compile(r"\u2705\s*(\w+)")
BLOCKER_RE = re.compile(
    r"\b(blocked|gate|requires approval|requires user|chrome|external-write)\b",
    re.IGNORECASE,
)


def parse_task_plan(path: Path) -> list[Track]:
    """Parse task_plan.md into structured Tracks with tasks."""
    if not path.exists(): return []
    text = path.read_text(encoding="utf-8")
    return _parse_task_plan_text(text)


def _parse_task_plan_text(text: str) -> list[Track]:
    """Parse task plan markdown content into structured Tracks with tasks."""
    tracks: list[Track] = []
    current_track: Track | None = None
    last_task: TrackTask | None = None
    for line in text.splitlines():
        m = TRACK_HEADER_RE.match(line)
        phase_m = PHASE_HEADER_RE.match(line)
        if m or phase_m:
            if current_track is not None: tracks.append(current_track)
            last_task = None
            if m:
                track_num = int(m.group(1))
                track_name = m.group(2).strip()
                agent_tag = m.group(3) if m.lastindex >= 3 else None
            else:
                track_num = 10
                track_name = f"Phase {phase_m.group(1)}: {phase_m.group(2).strip()}"
                agent_tag = None
            current_track = Track(name=track_name, number=track_num,
                tasks=[], completed=agent_tag is not None)
            continue
        if current_track is None: continue
        tm = TASK_ITEM_RE.match(line)
        if tm:
            is_comp = tm.group(1) == "[x]"
            desc = tm.group(2).strip()
            task = TrackTask(description=desc, completed=is_comp,
                track_name=current_track.name, track_number=current_track.number)
            agent_m = AGENT_TAG_RE.search(desc)
            if agent_m:
                task.assigned_agent = agent_m.group(1)
                task.description = AGENT_TAG_RE.sub("", desc).strip()
            current_track.tasks.append(task)
            last_task = task
            continue
        if last_task is not None and BLOCKER_RE.search(line):
            reason = line.strip().lstrip("-").strip()
            last_task.blocked = True
            last_task.block_reason = reason
    if current_track is not None: tracks.append(current_track)
    return tracks
# -------------------------------------------------------------------------
# Mailbox operations
# -------------------------------------------------------------------------

def _ensure_mailbox(agent_name: str) -> None:
    for subdir in ("inbox", "outbox", "processed"):
        (MAILBOXES_DIR / agent_name / subdir).mkdir(parents=True, exist_ok=True)


def send_message(recipient: str, content: str, sender: str = "orchestrator",
                 msg_type: str = "task", metadata: dict[str, Any] | None = None) -> MailboxMessage:
    """Place a JSON message into an agent inbox (matches send_agent_task.py format)."""
    _ensure_mailbox(recipient)
    msg = MailboxMessage(msg_id=str(uuid.uuid4())[:8], sender=sender,
        recipient=recipient, msg_type=msg_type, content=content,
        timestamp=time.time(), metadata=metadata or {})
    filename = f"{int(time.time() * 1000)}-{msg.msg_id}.json"
    filepath = MAILBOXES_DIR / recipient / "inbox" / filename
    filepath.write_text(json.dumps(asdict(msg), ensure_ascii=False, indent=2), encoding="utf-8")
    return msg


def send_shutdown(recipient: str, reason: str = "Mission complete") -> MailboxMessage:
    return send_message(recipient=recipient,
        content=f"## Shutdown Notice\n\n**Reason:** {reason}\n\nPlease terminate gracefully.",
        sender="orchestrator", msg_type="shutdown")


def read_inbox(agent_name: str) -> list[MailboxMessage]:
    """Read all unprocessed messages from an agent inbox."""
    inbox_dir = MAILBOXES_DIR / agent_name / "inbox"
    if not inbox_dir.exists(): return []
    messages: list[MailboxMessage] = []
    for filename in sorted(inbox_dir.iterdir()):
        if filename.suffix == ".json" and filename.is_file():
            try:
                data = json.loads(filename.read_text(encoding="utf-8"))
                messages.append(MailboxMessage(**data))
            except (json.JSONDecodeError, TypeError): continue
    return messages


def move_to_processed(agent_name: str, msg_id: str) -> bool:
    """Move a message from inbox to processed."""
    inbox_dir = MAILBOXES_DIR / agent_name / "inbox"
    processed_dir = MAILBOXES_DIR / agent_name / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    for f in inbox_dir.iterdir():
        if f.suffix == ".json" and msg_id in f.name:
            try: f.rename(processed_dir / f.name); return True
            except OSError: return False
    return False


def read_heartbeat(agent_name: str) -> float | None:
    """Read the agent heartbeat timestamp file."""
    hb_file = MAILBOXES_DIR / agent_name / "heartbeat"
    if not hb_file.exists(): return None
    try: return float(hb_file.read_text(encoding="utf-8").strip())
    except (ValueError, OSError): return None


def write_heartbeat(agent_name: str, ts: float | None = None) -> None:
    """Write a heartbeat timestamp for an agent."""
    hb_file = MAILBOXES_DIR / agent_name / "heartbeat"
    hb_file.parent.mkdir(parents=True, exist_ok=True)
    hb_file.write_text(str(ts or time.time()), encoding="utf-8")

# -------------------------------------------------------------------------
# State persistence
# -------------------------------------------------------------------------

def _load_state() -> MissionState | None:
    """Load mission state from state.json."""
    if not STATE_PATH.exists(): return None
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        agents = [AgentState(**a) for a in data.get("agents", [])]
        return MissionState(mission_id=data["mission_id"],
            description=data.get("description",""), started_at=data.get("started_at",0.0),
            status=data.get("status","active"), agents=agents,
            completed_tasks=data.get("completed_tasks",[]),
            current_track_index=data.get("current_track_index",0),
            updated_at=data.get("updated_at",0.0), ended_at=data.get("ended_at"),
            failure_reason=data.get("failure_reason",""))
    except (json.JSONDecodeError, KeyError, TypeError): return None


def _save_state(state: MissionState) -> None:
    """Persist mission state to state.json."""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    state.updated_at = time.time()
    data = asdict(state)
    STATE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _init_state(agents: list[AgentSpec],
               description: str = "Develop and harden NZ legislation workspace") -> MissionState:
    """Create a fresh mission state."""
    return MissionState(mission_id=str(uuid.uuid4())[:8], description=description,
        started_at=time.time(), status="active",
        agents=[AgentState(name=a.name, status="pending") for a in agents],
        completed_tasks=[], current_track_index=0)

# -------------------------------------------------------------------------
# Audit logging
# -------------------------------------------------------------------------

def _audit_log(event: str, agent: str, detail: str, meta: dict[str, Any] | None = None) -> None:
    """Append an event to the mission audit JSONL file."""
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    audit_path = AUDIT_DIR / "mission-swarm-mission.jsonl"
    record = {"ts": time.time(), "agent": agent, "event": event,
             "detail": detail, "meta": meta or {}}
    with audit_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
# -------------------------------------------------------------------------
# Agent lifecycle helpers
# -------------------------------------------------------------------------

def _check_heartbeats(state: MissionState, stale_threshold: float = HEARTBEAT_STALE_SECONDS) -> None:
    """Mark agents with stale heartbeats as timeout."""
    now = time.time()
    for agent_state in state.agents:
        if agent_state.status not in ("running", "idle"): continue
        hb = read_heartbeat(agent_state.name)
        if hb is not None and (now - hb) > stale_threshold:
            _audit_log("timeout", agent_state.name, f"No heartbeat for {now - hb:.1f}s")
            agent_state.status = "timeout"; agent_state.error_count += 1


def _agent_is_available(agent_state: AgentState) -> bool:
    """Check if an agent is available for new work."""
    return agent_state.status in ("pending", "idle")


def _console_safe(text: str) -> str:
    """Return text that can be printed on legacy Windows console encodings."""
    return text.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
        sys.stdout.encoding or "utf-8"
    )


def _task_gate_lane(task: TrackTask, available_agents: list[str]) -> str | None:
    if task.blocked:
        return None
    task_lower = task.description.lower()
    if any(kw in task_lower for kw in ("chrome", "browser", "oauth", "web console", "screenshot")):
        return "Chrome_Operator" if "Chrome_Operator" in available_agents else None
    if any(kw in task_lower for kw in ("commit", "push", "upload", "hugging face", "zenodo", "account", ".env", "gh auth")):
        return "Quality_Validator" if "Quality_Validator" in available_agents else None
    return ""


def _task_prefers_mimo(track: Track, task: TrackTask) -> bool:
    """Return true for bounded local implementation work suitable for MiMo Code."""
    text = f"{track.name} {task.description}".lower()
    if any(kw in text for kw in (
        "cross-repo", "cross-workspace", "every workspace", "all outstanding",
        "reconcile", "architecture", "schema", "ontology", "compatibility",
        "validat", "quality", "test", "lint", "chrome", "browser", "oauth",
        "commit", "push", "upload", "hugging face", "zenodo", ".env",
    )):
        return False
    return any(kw in text for kw in (
        "cli", "astro", "docs", "documentation", "plugin", "style", "migration",
        "template", "refactor", "script", "package", "command",
    ))


def _assign_track_to_agent(track: Track, task: TrackTask, available_agents: list[str]) -> str | None:
    """Determine the best agent for a given track using heuristic rules."""
    name_lower = track.name.lower()
    task_lower = task.description.lower()
    gated_lane = _task_gate_lane(task, available_agents)
    if gated_lane != "":
        return gated_lane
    if any(kw in task_lower for kw in ("all outstanding", "cross-workspace", "every workspace", "reconcile")):
        if "Codex_GPT55_Engineer" in available_agents: return "Codex_GPT55_Engineer"
    if any(kw in name_lower or kw in task_lower for kw in ("architecture", "ontology", "schema", "dependency ordering", "compatibility")):
        if "Architect_Oracle" in available_agents: return "Architect_Oracle"
    if any(kw in name_lower or kw in task_lower for kw in ("validat", "evidence", "quality", "test", "lint")):
        if "Quality_Validator" in available_agents: return "Quality_Validator"
    if any(kw in name_lower or kw in task_lower for kw in ("report", "transcript", "briefing", "interface", "visual")):
        if "Frontend" in available_agents: return "Frontend"
    if _task_prefers_mimo(track, task):
        if "Xiaomi_MiMo_Code" in available_agents: return "Xiaomi_MiMo_Code"
    if "General_Coder" in available_agents: return "General_Coder"
    for name in ("Xiaomi_MiMo_Code", "Codex_GPT55_Engineer", "Junior", "Frontend", "Oracle", "Quality_Validator"):
        if name in available_agents: return name
    return None


def _agent_accepts_local_fallback(agent_name: str) -> bool:
    """Return true for lanes allowed to take generic local implementation work."""
    return agent_name not in {"Chrome_Operator", "Quality_Validator"}


def _build_task_content(track: Track, task: TrackTask, agent: AgentSpec | None = None) -> str:
    """Build the full task message content for an agent."""
    done = sum(1 for t in track.tasks if t.completed)
    lines = []
    lines.append(f"## Track {track.number}: {track.name} - Task")
    lines.append("")
    lines.append(f"**Description:** {task.description}")
    lines.append("")
    lines.append("### Context")
    lines.append(f"This is part of Track {track.number} ({track.name}) in the root")
    lines.append("legal-nz all-Conductor swarm mission. The track has")
    lines.append(f"{len(track.tasks)} task(s), of which {done} are completed.")
    if agent is not None:
        lines.append("")
        lines.append("### Assigned Lane")
        lines.append(f"- Agent: `{agent.name}`")
        lines.append(f"- Model: `{agent.model}`")
        lines.append(f"- Mode: `{agent.mode}`")
    lines.append("")
    lines.append("Use `swarm-workspaces.yaml` to map workspace IDs to paths, and")
    lines.append("treat each listed `conductor/tracks.md` plus active track plans")
    lines.append("as the source of truth for that workspace.")
    lines.append("")
    lines.append("### Expected Outcome")
    lines.append("Provide concrete deliverables and clear completion criteria.")
    lines.append("")
    lines.append("### Requirements")
    lines.append("- Use only the minimum necessary tools and report what was used.")
    lines.append("- Use registered CLIs/package scripts before writing custom code.")
    lines.append("- Use Astro/Starlight for documentation-site work.")
    lines.append("- Preserve existing behavior, validate outputs, and log key decisions.")
    lines.append("- No destructive actions, no fabricated results, no silent assumptions.")
    lines.append("- Do not commit, push, upload, edit/sync `.env`, access Chrome/browser profiles,")
    lines.append("  or mutate external services unless the user explicitly approves that gate.")
    lines.append("")
    lines.append("### Deliverables")
    lines.append("- Working code or configuration changes in the workspace.")
    lines.append("- Update progress.md with a log of what was done.")
    lines.append("- Mark the task as [x] in task_plan.md when complete.")
    return "\n".join(lines)

# -------------------------------------------------------------------------
# Git notes tracking
# -------------------------------------------------------------------------

def _git_commit_exists(ref: str = "HEAD") -> bool:
    try:
        subprocess.run(["git","rev-parse","--verify",ref],
            capture_output=True, cwd=WORKSPACE_ROOT, timeout=10)
        return True
    except (subprocess.SubprocessError, FileNotFoundError): return False


def _git_note_add(task_description: str, agent: str) -> bool:
    """Add a git note to HEAD recording task completion."""
    if not _git_commit_exists(): return False
    try:
        note = json.dumps({"type":"task_completion","agent":agent,
            "task":task_description,"timestamp":time.time()})
        subprocess.run(["git","notes","add","-m",note],
            capture_output=True, cwd=WORKSPACE_ROOT, timeout=10)
        return True
    except (subprocess.SubprocessError, FileNotFoundError): return False
# -------------------------------------------------------------------------
# Main orchestrator
# -------------------------------------------------------------------------

def run_orchestrator(dry_run: bool = False, once: bool = False) -> int:
    """Execute the full swarm orchestrator cycle. Returns exit code."""
    # Phase 1: Load configuration
    swarm_config = _load_swarm_config(SWARM_CONFIG_YAML)
    if swarm_config is None:
        print("[ORCHESTRATOR] ERROR: swarm-config.yaml not found", file=sys.stderr)
        return 1
    agents = _load_subagents(SUBAGENTS_YAML)
    if not agents:
        print("[ORCHESTRATOR] ERROR: subagents.yaml not found or empty", file=sys.stderr)
        return 1
    agent_names = {a.name for a in agents}
    agent_specs_by_name = {a.name: a for a in agents}
    print(f"[ORCHESTRATOR] Loaded {len(agents)} agents: {', '.join(sorted(agent_names))}")
    print(f"[ORCHESTRATOR] Backend: {swarm_config.backend}, Engine: {swarm_config.engine}")
    if swarm_config.presets:
        preset_names = ", ".join(sorted(swarm_config.presets))
        print(f"[ORCHESTRATOR] Presets: {preset_names}")

    # Phase 2: Load or initialise mission state
    state = _load_state()
    if state is None:
        state = _init_state(agents)
        _save_state(state)
        _audit_log("mission_started", "orchestrator", f"Mission {state.mission_id} started")
        print(f"[ORCHESTRATOR] Initialised new mission state: {state.mission_id}")
    else:
        print(f"[ORCHESTRATOR] Resuming mission {state.mission_id} (status={state.status})")
        current_names = {a.name for a in state.agents}
        for a in agents:
            if a.name not in current_names:
                state.agents.append(AgentState(name=a.name, status="pending"))

    if state.status == "completed":
        print("[ORCHESTRATOR] Mission already completed. Exiting.")
        return 0

    # Phase 3: Parse task plan
    tracks = parse_task_plan(TASK_PLAN_MD)
    print(f"[ORCHESTRATOR] Parsed {len(tracks)} tracks from task_plan.md")
    for t in tracks:
        total = len(t.tasks)
        done = sum(1 for task in t.tasks if task.completed)
        print(f"  Track {t.number}: {t.name} - {done}/{total} tasks complete")

    # Phase 4: Dispatch loop
    all_done = False; cycle_count = 0
    poll_seconds = swarm_config.poll_interval_ms / 1000.0

    while not all_done:
        cycle_count += 1
        if not once: print(f"\n[ORCHESTRATOR] --- Cycle {cycle_count} ---")
        _check_heartbeats(state)

        # Build pending task list
        pending: list[tuple[Track, TrackTask]] = []
        blocked_pending: list[tuple[Track, TrackTask]] = []
        for track in tracks:
            for task in track.tasks:
                if not task.completed and task.description not in state.completed_tasks:
                    if task.blocked:
                        blocked_pending.append((track, task))
                    else:
                        pending.append((track, task))
        if not pending:
            if blocked_pending:
                print("[ORCHESTRATOR] No dispatchable local tasks remain.")
                for track, task in blocked_pending:
                    reason = f" ({task.block_reason})" if task.block_reason else ""
                    line = f"  BLOCKED Track {track.number}: {task.description}{reason}"
                    print(_console_safe(line))
                break
            all_done = True; break

        available_names = [a.name for a in state.agents if _agent_is_available(a)]
        dispatched = 0

        for agent_state in state.agents:
            if not _agent_is_available(agent_state): continue
            task_for = None
            task_idx = -1
            # Find task for this agent (exact match)
            for idx, (track, task) in enumerate(pending):
                assigned = _assign_track_to_agent(track, task, available_names)
                if assigned == agent_state.name:
                    task_for = (track, task); task_idx = idx; break
            if task_for is None:
                # Fallback: first task for this agent
                for idx, (track, task) in enumerate(pending):
                    if track.number in (1,2,9): continue
                    assigned = _assign_track_to_agent(track, task, available_names)
                    if assigned == agent_state.name:
                        task_for = (track, task); task_idx = idx; break
            if task_for is None:
                # Last resort: first pending task
                if not _agent_accepts_local_fallback(agent_state.name):
                    continue
                for idx, (track, task) in enumerate(pending):
                    if track.number in (1,2,9): continue
                    if _task_gate_lane(task, available_names) != "":
                        continue
                    task_for = (track, task); task_idx = idx; break
            if task_for is None: continue
            if task_idx >= 0: pending.pop(task_idx)

            track, task = task_for
            if dry_run:
                spec = agent_specs_by_name.get(agent_state.name)
                model = f" [{spec.model}]" if spec and spec.model else ""
                print(f"[ORCHESTRATOR] [DRY-RUN] -> {agent_state.name}{model}: Track {track.number} - {task.description[:80]}")
                dispatched += 1
                continue

            spec = agent_specs_by_name.get(agent_state.name)
            msg = send_message(recipient=agent_state.name,
                content=_build_task_content(track, task, spec), sender="orchestrator",
                msg_type="task",
                metadata={"track_number":track.number,"track_name":track.name,
                         "task_description":task.description,
                         "agent_model": spec.model if spec else "",
                         "agent_mode": spec.mode if spec else ""})
            agent_state.status = "running"
            agent_state.current_task = task.description
            agent_state.task_started_at = time.time()
            write_heartbeat(agent_state.name)
            _audit_log("task_dispatched", agent_state.name,
                f"Track {track.number}: {task.description[:60]}", {"msg_id":msg.msg_id})
            print(f"[ORCHESTRATOR] Dispatched {agent_state.name}: Track {track.number} - {task.description[:60]}...")
            dispatched += 1

        if dry_run:
            if dispatched == 0 and pending:
                print(
                    "[ORCHESTRATOR] [DRY-RUN] No eligible idle lane is available "
                    f"for {len(pending)} pending task(s)."
                )
            else:
                print(
                    f"[ORCHESTRATOR] [DRY-RUN] Would dispatch {dispatched} task(s); "
                    f"{len(pending)} pending task(s) would remain."
                )
            break

        if dispatched == 0 and not once:
            running = [a for a in state.agents if a.status == "running"]
            if not running:
                state.status = "active"; _save_state(state)
                print(f"[ORCHESTRATOR] All idle, {len(pending)} tasks remain. Continuing monitor.")
                time.sleep(poll_seconds)
                continue
            for agent_state in running:
                for msg in read_inbox(agent_state.name):
                    if msg.sender == agent_state.name and msg.msg_type in ("task_result","status"):
                        if agent_state.current_task and agent_state.current_task not in state.completed_tasks:
                            state.completed_tasks.append(agent_state.current_task)
                            _git_note_add(agent_state.current_task, agent_state.name)
                            _audit_log("task_completed", agent_state.name, agent_state.current_task[:80])
                            print(f"[ORCHESTRATOR] Completed: {agent_state.name} - {agent_state.current_task[:60]}...")
                        agent_state.status = "idle"; agent_state.current_task = None; agent_state.task_started_at = None
                        move_to_processed(agent_state.name, msg.msg_id)
            now = time.time()
            for agent_state in running:
                if agent_state.task_started_at and (now - agent_state.task_started_at) > DEFAULT_TIMEOUT:
                    _audit_log("timeout", agent_state.name, f"Task exceeded {DEFAULT_TIMEOUT}s");
                    agent_state.status = "timeout"; agent_state.error_count += 1
                    print(f"[ORCHESTRATOR] TIMEOUT: {agent_state.name}")
            _save_state(state)
            if once: break
            time.sleep(poll_seconds); continue
        if once: break
        _save_state(state); time.sleep(poll_seconds)

    # Phase 5: Finalisation
    if all_done:
        state.status = "completed"; state.ended_at = time.time(); _save_state(state)
        _audit_log("mission_completed", "orchestrator", "All tasks completed")
        for agent_state in state.agents:
            if agent_state.status in ("running","idle") and not dry_run:
                send_shutdown(agent_state.name, "All tasks completed")
                _audit_log("shutdown_sent", agent_state.name, "Mission complete")
        print(f"\n[ORCHESTRATOR] Mission complete! {len(state.completed_tasks)} tasks.")
        return 0
    if not dry_run:
        _save_state(state)
    print(f"\n[ORCHESTRATOR] Paused. {len(state.completed_tasks)} tasks completed.")
    return 0

# -------------------------------------------------------------------------
# CLI entry point
# -------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Swarm Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--once", action="store_true", help="Single dispatch pass")
    parser.add_argument("--reset", action="store_true", help="Reset mission state")
    args = parser.parse_args()
    if args.reset:
        if STATE_PATH.exists(): STATE_PATH.unlink()
        state = _init_state(_load_subagents(SUBAGENTS_YAML))
        _save_state(state)
        print(f"[ORCHESTRATOR] Reset - new mission: {state.mission_id}")
        return 0
    return run_orchestrator(dry_run=args.dry_run, once=args.once)


if __name__ == "__main__":
    sys.exit(main())
