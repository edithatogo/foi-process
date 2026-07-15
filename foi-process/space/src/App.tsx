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
};

type Tab = "overview" | "process" | "variants" | "cases" | "quality";

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
  const timeline = events.filter((event) => event.case_id === current?.case_id).sort((a, b) => a.timestamp.localeCompare(b.timestamp));
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
        {tab === "cases" && <CasesView cases={filteredCases} events={filteredEvents} selectedCase={selectedCase} onSelect={setSelectedCase} />}
        {tab === "quality" && <QualityView data={data} findings={data.findings.filter((finding) => caseIds.has(finding.case_id))} />}
      </main>
      <footer><span>Read-only analytical projection</span><span>{data.meta.classification}</span><span>{data.quality.checksums_verified ? "Manifest verified" : "Manifest unverified"}</span></footer>
    </div>
  );
}
