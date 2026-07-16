import { useEffect, useMemo, useState } from "react";
import ReactECharts from "./EChart";
import {
  Activity,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  CircleAlert,
  Clock3,
  Database,
  FileCheck2,
  Filter,
  FlaskConical,
  GitBranch,
  LayoutDashboard,
  ListTree,
  Search,
  ShieldCheck,
} from "lucide-react";

type EventRow = {
  event_id: string;
  case_id: string;
  activity: string;
  timestamp: string;
  source_sequence: number;
  authority_id: string | null;
  jurisdiction: string;
  evidence_count: number;
};

type CaseRow = {
  case_id: string;
  authority_id: string | null;
  jurisdiction: string;
  started_at: string;
  ended_at: string;
  duration_seconds: number;
  event_ids: string[];
  activities: string[];
};

type EdgeRow = {
  source: string;
  target: string;
  count: number;
  mean_wait_seconds: number | null;
};

type VariantRow = { variant_id: number; activities: string[]; count: number };
type FindingRow = {
  rule_id: string;
  case_id: string;
  layer: string;
  severity: string;
  message: string;
  requires_human_review: boolean;
};

type ScenarioSummary = {
  scenario_id: string;
  label: string;
  description: string;
  case_count: number;
  event_count: number;
  revision_count: number;
  corrected_case_count: number;
  correction_rate: number;
  median_cycle_days: number;
  p90_cycle_days: number;
  peak_backlog: number;
  variant_count: number;
  dominant_variant: string[];
};

type ScenarioDaily = {
  scenario_id: string;
  date: string;
  arrivals: number;
  closures: number;
  backlog: number;
  mean_closed_cycle_days: number | null;
  correction_events: number;
};

type ScenarioProcessModel = {
  scenario_id: string;
  activities: { activity: string; count: number }[];
  edges: { source: string; target: string; count: number; mean_wait_days: number }[];
  variants: { rank: number; activities: string[]; count: number; share: number }[];
};

type DashboardData = {
  meta: {
    dataset_id: string;
    classification: string;
    source_release: string;
    generated_at: string;
    manifest_sha256: string;
  };
  metrics: Record<string, number>;
  quality: {
    manifest_file_count: number;
    checksums_verified: boolean;
    timestamp_coverage: number;
    evidence_coverage: number;
    reviewed_revision_count: number;
    revision_count: number;
    delta_count: number;
    ocel_object_count: number;
    ocel_link_count: number;
  };
  activities: { activity: string; count: number }[];
  events: EventRow[];
  edges: EdgeRow[];
  variants: VariantRow[];
  cases: CaseRow[];
  findings: FindingRow[];
  simulation: { summaries: ScenarioSummary[]; daily_metrics: ScenarioDaily[]; process_models: ScenarioProcessModel[] };
};

type Tab = "overview" | "process" | "variants" | "scenarios" | "cases" | "quality";

const palette = {
  ink: "#24312b",
  green: "#2f6f54",
  teal: "#297a78",
  gold: "#bd8b32",
  coral: "#c45d4a",
  blue: "#4b72a8",
  grid: "#dfe5e1",
};

const tabs: { id: Tab; label: string; icon: typeof Activity }[] = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "process", label: "Process", icon: GitBranch },
  { id: "variants", label: "Variants", icon: ListTree },
  { id: "scenarios", label: "Scenarios", icon: FlaskConical },
  { id: "cases", label: "Cases", icon: Clock3 },
  { id: "quality", label: "Quality", icon: ShieldCheck },
];

function shortActivity(value: string) {
  return value.replace(/^foio:/, "").replace(/([a-z])([A-Z])/g, "$1 $2");
}

function compactId(value: string) {
  const parts = value.split(":");
  const tail = parts[parts.length - 1] ?? value;
  return tail.length > 16 ? `${tail.slice(0, 8)}...${tail.slice(-5)}` : tail;
}

function duration(seconds: number | null) {
  if (seconds === null) return "No observation";
  if (seconds < 3600) return `${Math.round(seconds / 60)} min`;
  if (seconds < 86400) return `${(seconds / 3600).toFixed(1)} hr`;
  return `${(seconds / 86400).toFixed(1)} days`;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-NZ", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function quantile(values: number[], percentile: number) {
  if (!values.length) return 0;
  const ordered = [...values].sort((a, b) => a - b);
  const index = Math.min(ordered.length - 1, Math.ceil(percentile * ordered.length) - 1);
  return ordered[index];
}

function Metric({ label, value, detail, icon: Icon }: { label: string; value: string; detail: string; icon: typeof Activity }) {
  return (
    <article className="metric">
      <span className="metric-icon"><Icon size={18} /></span>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
        <small>{detail}</small>
      </div>
    </article>
  );
}

function Panel({ title, subtitle, children, action }: { title: string; subtitle?: string; children: React.ReactNode; action?: React.ReactNode }) {
  return (
    <section className="panel">
      <header className="panel-heading">
        <div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>
        {action}
      </header>
      {children}
    </section>
  );
}

function ChartLegend({ items }: { items: { label: string; color: string }[] }) {
  return <div className="scenario-chart-legend">{items.map((item) => <span key={item.label}><i style={{ background: item.color }} />{item.label}</span>)}</div>;
}

function Overview({ data, events, cases }: { data: DashboardData; events: EventRow[]; cases: CaseRow[] }) {
  const durations = cases.map((item) => item.duration_seconds);
  const activityCounts = Object.entries(events.reduce<Record<string, number>>((acc, event) => {
    acc[event.activity] = (acc[event.activity] ?? 0) + 1;
    return acc;
  }, {})).sort((a, b) => b[1] - a[1]);
  const chart = {
    color: [palette.green],
    tooltip: { trigger: "axis", renderMode: "richText" },
    grid: { left: 8, right: 22, top: 10, bottom: 10, containLabel: true },
    xAxis: { type: "value", minInterval: 1, splitLine: { lineStyle: { color: palette.grid } } },
    yAxis: { type: "category", data: activityCounts.map(([name]) => shortActivity(name)), axisLine: { show: false }, axisTick: { show: false } },
    series: [{ type: "bar", data: activityCounts.map(([, count]) => count), barMaxWidth: 24, itemStyle: { borderRadius: [0, 3, 3, 0] } }],
  };
  return (
    <>
      <div className="metrics-grid">
        <Metric label="Cases" value={String(cases.length)} detail={`${events.length} active events`} icon={Database} />
        <Metric label="Median cycle" value={duration(quantile(durations, 0.5))} detail="Request to last observation" icon={Clock3} />
        <Metric label="P90 cycle" value={duration(quantile(durations, 0.9))} detail="Observed cases" icon={BarChart3} />
        <Metric label="Evidence coverage" value={`${Math.round(data.quality.evidence_coverage * 100)}%`} detail="Events with linked evidence" icon={FileCheck2} />
      </div>
      <div className="overview-grid">
        <Panel title="Activity frequency" subtitle="Latest active revision per logical event">
          <ReactECharts option={chart} style={{ height: 310 }} />
        </Panel>
        <Panel title="Dataset posture" subtitle="Publication and provenance controls">
          <div className="posture-list">
            <div><CheckCircle2 /><span><strong>Checksums verified</strong><small>{data.quality.manifest_file_count} files matched the manifest</small></span></div>
            <div><ShieldCheck /><span><strong>Synthetic fixture</strong><small>Human-reviewed publication classification</small></span></div>
            <div><GitBranch /><span><strong>Revision aware</strong><small>{data.quality.revision_count} revisions, {data.quality.delta_count} evidence deltas</small></span></div>
            <div><Database /><span><strong>OCEL linked</strong><small>{data.quality.ocel_object_count} objects, {data.quality.ocel_link_count} event-object links</small></span></div>
          </div>
        </Panel>
      </div>
    </>
  );
}

function ProcessView({ edges, events }: { edges: EdgeRow[]; events: EventRow[] }) {
  const names = Array.from(new Set(events.map((event) => event.activity)));
  const counts = events.reduce<Record<string, number>>((acc, event) => ({ ...acc, [event.activity]: (acc[event.activity] ?? 0) + 1 }), {});
  const graph = {
    tooltip: { renderMode: "richText", formatter: (item: { dataType: string; data: { fullName?: string; count?: number; wait?: number | null } }) => item.dataType === "node"
      ? `${shortActivity(item.data.fullName ?? "")}\n${item.data.count} events`
      : `Mean wait: ${duration(item.data.wait ?? null)}` },
    series: [{
      type: "graph", layout: "none", roam: true, symbol: "roundRect", symbolSize: [135, 56],
      edgeSymbol: ["none", "arrow"], edgeSymbolSize: 9,
      label: { show: true, width: 116, overflow: "break", lineHeight: 15, color: "#fff", fontSize: 11 },
      lineStyle: { color: palette.teal, width: 3, curveness: 0.06, opacity: 0.75 },
      emphasis: { focus: "adjacency" },
      data: names.map((name, index) => ({
        name: shortActivity(name), fullName: name, count: counts[name],
        x: 110 + index * 185, y: index % 2 ? 210 : 130,
        itemStyle: { color: [palette.green, palette.blue, palette.gold, palette.coral][index % 4], borderColor: "#fff", borderWidth: 3 },
      })),
      links: edges.map((edge) => ({ source: shortActivity(edge.source), target: shortActivity(edge.target), wait: edge.mean_wait_seconds, value: edge.count })),
    }],
  };
  return (
    <div className="process-layout">
      <Panel title="Directly-follows map" subtitle="Drag to reposition; scroll to zoom" action={<span className="legend-line"><i /> Mean waiting time on hover</span>}>
        <ReactECharts option={graph} style={{ height: 470 }} />
      </Panel>
      <Panel title="Transitions" subtitle="Observed frequency and elapsed time">
        <div className="edge-list">
          {edges.map((edge) => <div className="edge-row" key={`${edge.source}-${edge.target}`}>
            <span>{shortActivity(edge.source)}</span><ArrowRight size={15} /><span>{shortActivity(edge.target)}</span>
            <strong>{edge.count}x</strong><small>{duration(edge.mean_wait_seconds)}</small>
          </div>)}
        </div>
      </Panel>
    </div>
  );
}

function VariantsView({ variants }: { variants: VariantRow[] }) {
  const nodes = new Map<string, { name: string }>();
  const links: { source: string; target: string; value: number }[] = [];
  variants.forEach((variant) => variant.activities.forEach((activity, index) => {
    const nodeName = `${index + 1}. ${shortActivity(activity)}`;
    nodes.set(nodeName, { name: nodeName });
    if (index) links.push({ source: `${index}. ${shortActivity(variant.activities[index - 1])}`, target: nodeName, value: variant.count });
  }));
  const option = {
    color: [palette.green, palette.blue, palette.gold, palette.coral, palette.teal],
    tooltip: { trigger: "item", renderMode: "richText" },
    series: [{ type: "sankey", data: [...nodes.values()], links, left: 25, right: 25, top: 25, bottom: 20, nodeWidth: 18, nodeGap: 20,
      label: { color: palette.ink, fontSize: 12 }, lineStyle: { color: "gradient", opacity: 0.4 }, emphasis: { focus: "adjacency" } }],
  };
  return (
    <div className="variants-layout">
      <Panel title="Variant flow" subtitle="Activity paths weighted by case frequency">
        <ReactECharts option={option} style={{ height: 430 }} />
      </Panel>
      <Panel title="Variant catalogue" subtitle={`${variants.length} observed path${variants.length === 1 ? "" : "s"}`}>
        <div className="variant-list">
          {variants.map((variant) => <article key={variant.variant_id}>
            <header><strong>Variant {variant.variant_id}</strong><span>{variant.count} case{variant.count === 1 ? "" : "s"}</span></header>
            <div className="variant-path">{variant.activities.map((activity, index) => <span key={`${activity}-${index}`}>{index > 0 && <ChevronRight size={14} />}{shortActivity(activity)}</span>)}</div>
          </article>)}
        </div>
      </Panel>
    </div>
  );
}

function CasesView({ cases, events, selectedCase, onSelect }: { cases: CaseRow[]; events: EventRow[]; selectedCase: string; onSelect: (value: string) => void }) {
  const current = cases.find((item) => item.case_id === selectedCase) ?? cases[0];
  const timeline = events.filter((event) => event.case_id === current?.case_id).sort((a, b) => a.timestamp.localeCompare(b.timestamp) || a.source_sequence - b.source_sequence || a.event_id.localeCompare(b.event_id));
  return (
    <div className="cases-layout">
      <Panel title="Case queue" subtitle="Select a request to inspect its trace">
        <div className="case-list">{cases.map((item) => <button className={item.case_id === current?.case_id ? "active" : ""} onClick={() => onSelect(item.case_id)} key={item.case_id}>
          <span><strong>{compactId(item.case_id)}</strong><small>{item.authority_id ?? "Unknown authority"}</small></span>
          <span><b>{duration(item.duration_seconds)}</b><ChevronRight size={16} /></span>
        </button>)}</div>
      </Panel>
      <Panel title="Request timeline" subtitle={current ? `${compactId(current.case_id)} · ${duration(current.duration_seconds)} total` : "No matching case"}>
        <div className="timeline">
          {timeline.map((event, index) => <article key={event.event_id}>
            <div className="timeline-marker"><i className={index === timeline.length - 1 ? "last" : ""} />{index < timeline.length - 1 && <span />}</div>
            <div><time>{formatDate(event.timestamp)}</time><h3>{shortActivity(event.activity)}</h3><p>{event.evidence_count} evidence link{event.evidence_count === 1 ? "" : "s"} · {event.jurisdiction}</p><code>{compactId(event.event_id)}</code></div>
          </article>)}
        </div>
      </Panel>
    </div>
  );
}

function ScenariosView({ data }: { data: DashboardData }) {
  const summaries = data.simulation.summaries;
  const [selected, setSelected] = useState(summaries[0]?.scenario_id ?? "baseline");
  const current = summaries.find((item) => item.scenario_id === selected) ?? summaries[0];
  const daily = data.simulation.daily_metrics.filter((item) => item.scenario_id === current?.scenario_id);
  const process = data.simulation.process_models.find((item) => item.scenario_id === current?.scenario_id);
  const comparison = {
    color: [palette.coral, palette.blue], tooltip: { trigger: "axis", renderMode: "richText" },
    grid: { left: 16, right: 18, top: 20, bottom: 16, containLabel: true },
    xAxis: { type: "category", data: summaries.map((item) => item.label), axisLabel: { interval: 0 } },
    yAxis: [{ type: "value", name: "Cases", splitLine: { lineStyle: { color: palette.grid } } }, { type: "value", name: "Days", splitLine: { show: false } }],
    series: [
      { name: "Peak backlog", type: "bar", data: summaries.map((item) => item.peak_backlog), barMaxWidth: 34, itemStyle: { borderRadius: [3, 3, 0, 0] } },
      { name: "P90 cycle", type: "line", yAxisIndex: 1, smooth: true, symbolSize: 8, data: summaries.map((item) => item.p90_cycle_days) },
    ],
  };
  const trajectory = {
    color: [palette.green, palette.blue, palette.gold, palette.coral], tooltip: { trigger: "axis", renderMode: "richText" },
    grid: { left: 15, right: 16, top: 20, bottom: 20, containLabel: true },
    xAxis: { type: "category", data: daily.map((item) => item.date.slice(5)), axisLabel: { interval: Math.max(0, Math.floor(daily.length / 8) - 1) } },
    yAxis: { type: "value", minInterval: 1, splitLine: { lineStyle: { color: palette.grid } } },
    series: [
      { name: "Backlog", type: "line", smooth: true, showSymbol: false, areaStyle: { opacity: 0.12 }, data: daily.map((item) => item.backlog) },
      { name: "Arrivals", type: "bar", stack: "flow", barMaxWidth: 9, data: daily.map((item) => item.arrivals) },
      { name: "Closures", type: "bar", stack: "flow", barMaxWidth: 9, data: daily.map((item) => -item.closures) },
      { name: "Corrections", type: "line", showSymbol: true, symbol: "diamond", symbolSize: 7, lineStyle: { width: 0 }, data: daily.map((item) => item.correction_events) },
    ],
  };
  const activityRows = [...(process?.activities ?? [])].reverse();
  const activityMix = {
    color: [palette.teal], tooltip: { trigger: "axis", renderMode: "richText" },
    grid: { left: 10, right: 20, top: 16, bottom: 16, containLabel: true },
    xAxis: { type: "value", minInterval: 1, splitLine: { lineStyle: { color: palette.grid } } },
    yAxis: { type: "category", data: activityRows.map((item) => shortActivity(item.activity)), axisLine: { show: false }, axisTick: { show: false } },
    series: [{ type: "bar", data: activityRows.map((item) => item.count), barMaxWidth: 25, itemStyle: { borderRadius: [0, 3, 3, 0] } }],
  };
  const processFlow = {
    tooltip: { renderMode: "richText", formatter: (item: { dataType: string; data: { name?: string; count?: number; source?: string; target?: string; mean_wait_days?: number } }) => item.dataType === "node"
      ? `${item.data.name}\n${item.data.count} events`
      : `${item.data.source} to ${item.data.target}\n${item.data.count} transitions · ${item.data.mean_wait_days?.toFixed(1)} days mean` },
    series: [{
      type: "sankey", left: 18, right: 112, top: 18, bottom: 18, nodeWidth: 20, nodeGap: 18,
      emphasis: { focus: "adjacency" }, draggable: false,
      label: { color: palette.ink, fontSize: 10, width: 94, overflow: "break", lineHeight: 13 },
      lineStyle: { color: "gradient", opacity: 0.45, curveness: 0.5 },
      data: (process?.activities ?? []).map((item, index) => ({
        name: shortActivity(item.activity), count: item.count,
        itemStyle: { color: [palette.green, palette.blue, palette.gold, palette.coral, palette.teal][index % 5] },
      })),
      links: (process?.edges ?? []).map((edge) => ({
        source: shortActivity(edge.source), target: shortActivity(edge.target), value: edge.count,
        count: edge.count, mean_wait_days: edge.mean_wait_days,
      })),
    }],
  };
  if (!current) return <Panel title="Simulation scenarios"><div className="empty-state">No scenario projection deposited.</div></Panel>;
  return (
    <>
      <div className="scenario-switcher" role="group" aria-label="Simulation scenario">
        {summaries.map((item) => <button key={item.scenario_id} className={item.scenario_id === current.scenario_id ? "active" : ""} onClick={() => setSelected(item.scenario_id)}>{item.label}</button>)}
      </div>
      <div className="metrics-grid">
        <Metric label="Peak backlog" value={String(current.peak_backlog)} detail="Open cases at maximum pressure" icon={Database} />
        <Metric label="Median cycle" value={current.median_cycle_days.toFixed(1) + " days"} detail="Request to closure" icon={Clock3} />
        <Metric label="P90 cycle" value={current.p90_cycle_days.toFixed(1) + " days"} detail="Tail processing time" icon={BarChart3} />
        <Metric label="Correction rate" value={Math.round(current.correction_rate * 100) + "%"} detail={current.corrected_case_count + " corrected cases"} icon={FileCheck2} />
      </div>
      <div className="scenario-grid">
        <Panel title="Comparative pressure" subtitle="Peak open cases and tail cycle time across scenarios"><ReactECharts option={comparison} style={{ height: 315 }} /><ChartLegend items={[{ label: "Peak backlog", color: palette.coral }, { label: "P90 cycle", color: palette.blue }]} /></Panel>
        <Panel title={current.label + " trajectory"} subtitle={current.description}><ReactECharts option={trajectory} style={{ height: 315 }} /><ChartLegend items={[{ label: "Backlog", color: palette.green }, { label: "Arrivals", color: palette.blue }, { label: "Closures", color: palette.gold }, { label: "Corrections", color: palette.coral }]} /></Panel>
      </div>
      <div className="scenario-mining-grid">
        <Panel title="Activity mix" subtitle={`${current.event_count} active events`}><ReactECharts option={activityMix} style={{ height: 330 }} /></Panel>
        <Panel title="Directly-follows flow" subtitle={`${process?.edges.length ?? 0} observed transitions`}><ReactECharts option={processFlow} style={{ height: 330 }} /></Panel>
        <Panel title="Trace variants" subtitle={`${process?.variants.length ?? 0} observed path${process?.variants.length === 1 ? "" : "s"}`}>
          <div className="scenario-variant-list">{(process?.variants ?? []).map((variant) => <article key={variant.rank}>
            <header><strong>Variant {variant.rank}</strong><span>{Math.round(variant.share * 100)}% · {variant.count} cases</span></header>
            <div className="variant-path">{variant.activities.map((activity, index) => <span key={`${activity}-${index}`}>{shortActivity(activity)}{index < variant.activities.length - 1 && <ChevronRight size={12} />}</span>)}</div>
            <div className="variant-share"><i style={{ width: `${Math.max(3, variant.share * 100)}%` }} /></div>
          </article>)}</div>
        </Panel>
      </div>
      <Panel title="Scenario catalogue" subtitle="Deterministic workload and revision stress profiles">
        <div className="scenario-catalogue">{summaries.map((item) => <article key={item.scenario_id} className={item.scenario_id === current.scenario_id ? "active" : ""}>
          <header><strong>{item.label}</strong><span>{item.case_count} cases</span></header><p>{item.description}</p>
          <dl><div><dt>Events</dt><dd>{item.event_count}</dd></div><div><dt>Revisions</dt><dd>{item.revision_count}</dd></div><div><dt>Variants</dt><dd>{item.variant_count}</dd></div></dl>
        </article>)}</div>
      </Panel>
    </>
  );
}

function QualityView({ data, findings }: { data: DashboardData; findings: FindingRow[] }) {
  const gauges = [
    { name: "Timestamp coverage", value: data.quality.timestamp_coverage, color: palette.green },
    { name: "Evidence coverage", value: data.quality.evidence_coverage, color: palette.gold },
    { name: "Reviewed revisions", value: data.quality.reviewed_revision_count / Math.max(data.quality.revision_count, 1), color: palette.blue },
  ];
  const option = {
    tooltip: { trigger: "item", formatter: "{b}: {d}%", renderMode: "richText" },
    series: gauges.map((gauge, index) => ({
      name: gauge.name, type: "pie", radius: [`${29 + index * 18}%`, `${39 + index * 18}%`], center: ["50%", "50%"], silent: false,
      label: { show: false }, data: [{ value: gauge.value, name: gauge.name, itemStyle: { color: gauge.color } }, { value: 1 - gauge.value, name: "Gap", itemStyle: { color: "#e8ece9" }, tooltip: { show: false } }],
    })),
  };
  return (
    <div className="quality-layout">
      <Panel title="Coverage profile" subtitle="Completeness of deposited analytical fields">
        <ReactECharts option={option} style={{ height: 330 }} />
        <div className="quality-legend">{gauges.map((item) => <span key={item.name}><i style={{ background: item.color }} />{item.name}<strong>{Math.round(item.value * 100)}%</strong></span>)}</div>
      </Panel>
      <Panel title="Conformance findings" subtitle="Evidence-linked outputs; not certified legal conclusions">
        <div className="finding-list">{findings.map((finding) => <article key={`${finding.case_id}-${finding.rule_id}`}>
          <span className={`severity ${finding.severity}`}><CircleAlert size={15} />{finding.severity}</span>
          <div><h3>{finding.rule_id}</h3><p>{finding.message}</p><small>{finding.layer} · {compactId(finding.case_id)}</small></div>
        </article>)}</div>
      </Panel>
      <Panel title="Publication provenance" subtitle="Reproducibility identifiers">
        <dl className="provenance">
          <div><dt>Dataset</dt><dd>{data.meta.dataset_id}</dd></div>
          <div><dt>Source release</dt><dd>{data.meta.source_release}</dd></div>
          <div><dt>Classification</dt><dd>{data.meta.classification}</dd></div>
          <div><dt>Manifest SHA-256</dt><dd><code>{data.meta.manifest_sha256}</code></dd></div>
        </dl>
      </Panel>
    </div>
  );
}

export default function App() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("overview");
  const [authority, setAuthority] = useState("all");
  const [query, setQuery] = useState("");
  const [selectedCase, setSelectedCase] = useState("");

  useEffect(() => {
    fetch("./data/dashboard-data.json")
      .then((response) => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json(); })
      .then((value: DashboardData) => { setData(value); setSelectedCase(value.cases[0]?.case_id ?? ""); })
      .catch((reason: Error) => setError(reason.message));
  }, []);

  const authorities = useMemo(() => data ? Array.from(new Set(data.cases.map((item) => item.authority_id).filter(Boolean))) as string[] : [], [data]);
  const filteredCases = useMemo(() => data?.cases.filter((item) => {
    const authorityMatch = authority === "all" || item.authority_id === authority;
    const text = `${item.case_id} ${item.authority_id ?? ""}`.toLowerCase();
    return authorityMatch && text.includes(query.toLowerCase());
  }) ?? [], [data, authority, query]);
  const caseIds = useMemo(() => new Set(filteredCases.map((item) => item.case_id)), [filteredCases]);
  const filteredEvents = data?.events.filter((event) => caseIds.has(event.case_id)) ?? [];

  useEffect(() => {
    if (filteredCases.length && !caseIds.has(selectedCase)) setSelectedCase(filteredCases[0].case_id);
  }, [caseIds, filteredCases, selectedCase]);

  if (error) return <main className="load-state"><CircleAlert /><h1>Dashboard data unavailable</h1><p>{error}</p></main>;
  if (!data) return <main className="load-state"><Activity className="pulse" /><h1>Loading process evidence</h1></main>;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand"><span><GitBranch size={21} /></span><div><h1>FOI Process Explorer</h1><p>Evidence-led process mining</p></div></div>
        <div className="dataset-state"><span><i /> Verified fixture</span><small>{data.meta.source_release} · {new Date(data.meta.generated_at).toLocaleDateString("en-NZ")}</small></div>
      </header>
      <nav className="tabs" aria-label="Dashboard views">{tabs.map((item) => { const Icon = item.icon; return <button className={tab === item.id ? "active" : ""} onClick={() => setTab(item.id)} key={item.id}><Icon size={17} />{item.label}</button>; })}</nav>
      <div className="filterbar">
        <div className="filter-label"><Filter size={16} /><span>Scope</span></div>
        <label><span>Authority</span><select value={authority} onChange={(event) => setAuthority(event.target.value)}><option value="all">All authorities</option>{authorities.map((item) => <option key={item}>{item}</option>)}</select></label>
        <label className="search"><span>Case search</span><div><Search size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Request or authority" /></div></label>
        <div className="scope-count"><strong>{filteredCases.length}</strong><span>cases in scope</span></div>
      </div>
      <main className="workspace">
        {tab === "overview" && <Overview data={data} events={filteredEvents} cases={filteredCases} />}
        {tab === "process" && <ProcessView edges={data.edges} events={filteredEvents} />}
        {tab === "variants" && <VariantsView variants={data.variants} />}
        {tab === "scenarios" && <ScenariosView data={data} />}
        {tab === "cases" && <CasesView cases={filteredCases} events={filteredEvents} selectedCase={selectedCase} onSelect={setSelectedCase} />}
        {tab === "quality" && <QualityView data={data} findings={data.findings.filter((finding) => caseIds.has(finding.case_id))} />}
      </main>
      <footer><span>Read-only analytical projection</span><span>{data.meta.classification}</span><span>{data.quality.checksums_verified ? "Manifest verified" : "Manifest unverified"}</span></footer>
    </div>
  );
}
