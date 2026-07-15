import { useEffect, useRef } from "react";
import type { CSSProperties } from "react";
import * as echarts from "echarts/core";
import type { EChartsCoreOption } from "echarts/core";
import { BarChart, GraphChart, PieChart, SankeyChart } from "echarts/charts";
import { GridComponent, TooltipComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
  BarChart,
  GraphChart,
  PieChart,
  SankeyChart,
  GridComponent,
  TooltipComponent,
  CanvasRenderer,
]);

export default function EChart({ option, style }: { option: Record<string, unknown>; style?: CSSProperties }) {
  const element = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!element.current) return;
    const chart = echarts.init(element.current, undefined, { renderer: "canvas" });
    chart.setOption(option as EChartsCoreOption);
    const observer = new ResizeObserver(() => chart.resize());
    observer.observe(element.current);
    return () => {
      observer.disconnect();
      chart.dispose();
    };
  }, [option]);

  return <div ref={element} style={style} />;
}
