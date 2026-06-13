import { Bell, Droplets, Radio, Thermometer } from "lucide-react";
import { ActivityItem } from "../components/ActivityItem";
import { AlertItem } from "../components/AlertItem";
import { EmptyState } from "../components/EmptyState";
import { MetricCard } from "../components/MetricCard";
import { PlotCard } from "../components/PlotCard";
import { TimeSeriesChart } from "../components/TimeSeriesChart";
import type {
  Activity,
  Alert,
  IrrigationMarker,
  Measurement,
  Plot,
} from "../types/vineyard";
import { buildSoilMoistureComparisonData } from "../utils/chartData";
import { formatPercent, formatTemperature } from "../utils/formatters";

type OverviewViewProps = {
  plots: Plot[];
  measurements: Measurement[];
  alerts: Alert[];
  activities: Activity[];
  irrigationMarkers: IrrigationMarker[];
  onSelectPlot: (plotId: string) => void;
};

export function OverviewView({
  plots,
  measurements,
  alerts,
  activities,
  irrigationMarkers,
  onSelectPlot,
}: OverviewViewProps) {
  const averageSoilMoisture =
    plots.reduce((total, plot) => total + plot.soilMoisture, 0) / Math.max(plots.length, 1);
  const averageTemperature =
    plots.reduce((total, plot) => total + plot.airTemperature, 0) / Math.max(plots.length, 1);
  const activeSensors = plots.reduce((total, plot) => total + plot.activeSensors, 0);
  const openAlerts = alerts.length;
  const chartData = buildSoilMoistureComparisonData(measurements, ["plot-a", "plot-b"]);
  const overviewMarkers = irrigationMarkers
    .filter((marker) => marker.plotId === "plot-a")
    .map((marker) => ({ timestamp: marker.timestamp, label: marker.label }));

  function getPlotLabel(plotId?: string): string | undefined {
    const plot = plots.find((item) => item.id === plotId);
    return plot ? `${plot.name} - ${plot.fieldName}` : undefined;
  }

  return (
    <div className="stack">
      <section className="metric-grid" aria-label="Vineyard summary">
        <MetricCard
          comparison="Up 5.1 points after yesterday evening irrigation"
          icon={Droplets}
          title="Average soil moisture"
          value={formatPercent(averageSoilMoisture)}
        />
        <MetricCard
          comparison="Within expected range for the canopy"
          icon={Thermometer}
          title="Air temperature"
          value={formatTemperature(averageTemperature)}
        />
        <MetricCard
          comparison="All gateway imports completed"
          icon={Radio}
          title="Active sensors"
          value={String(activeSensors)}
        />
        <MetricCard
          comparison="1 critical, 1 warning, 1 informational"
          icon={Bell}
          title="Open alerts"
          value={String(openAlerts)}
        />
      </section>

      <section className="chart-card" aria-labelledby="moisture-chart-title">
        <div className="section-heading">
          <div>
            <h2 id="moisture-chart-title">Soil moisture during the last 24 hours</h2>
            <p>Comparison between Plot A and Plot B with the irrigation event highlighted.</p>
          </div>
        </div>
        <TimeSeriesChart
          data={chartData}
          lines={[
            { dataKey: "plotA", name: "Plot A", color: "#1f6b46" },
            { dataKey: "plotB", name: "Plot B", color: "#a5673f" },
          ]}
          markers={overviewMarkers}
        />
      </section>

      <section className="view-card" aria-labelledby="plot-status-title">
        <div className="section-heading">
          <div>
            <h2 id="plot-status-title">Plot status</h2>
            <p>Open a plot to inspect sensors, recent field events, and irrigation response.</p>
          </div>
        </div>
        <div className="plot-grid">
          {plots.map((plot) => (
            <PlotCard key={plot.id} plot={plot} onSelect={onSelectPlot} />
          ))}
        </div>
      </section>

      <div className="dashboard-grid">
        <section className="view-card" aria-labelledby="alerts-title">
          <div className="section-heading">
            <div>
              <h2 id="alerts-title">Alerts and observations</h2>
              <p>Current agronomic signals requiring attention or review.</p>
            </div>
          </div>
          <div className="panel-list">
            {alerts.length > 0 ? (
              alerts.map((alert) => (
                <AlertItem alert={alert} key={alert.id} plotLabel={getPlotLabel(alert.plotId)} />
              ))
            ) : (
              <EmptyState
                title="No open alerts"
                description="Alert cards will appear here when thresholds or observations need attention."
              />
            )}
          </div>
        </section>

        <section className="view-card" aria-labelledby="activity-title">
          <div className="section-heading">
            <div>
              <h2 id="activity-title">Recent activity</h2>
              <p>Field work, imports, notes, and research synchronization history.</p>
            </div>
          </div>
          <div className="panel-list">
            {activities.length > 0 ? (
              activities.map((activity) => <ActivityItem activity={activity} key={activity.id} />)
            ) : (
              <EmptyState
                title="No recent activity"
                description="Saved field events and imports will appear here."
              />
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
