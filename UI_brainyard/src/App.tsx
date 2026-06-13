import { useEffect, useMemo, useState } from "react";
import { EventForm } from "./components/EventForm";
import { Header } from "./components/Header";
import { LoadingState } from "./components/LoadingState";
import { Sidebar, type NavigationKey } from "./components/Sidebar";
import { StudyForm } from "./components/StudyForm";
import { StudyResult } from "./components/StudyResult";
import { flywheelService } from "./services/flywheelService";
import { vineyardService } from "./services/vineyardService";
import type {
  Activity,
  DashboardData,
  FieldEventDraft,
  FlywheelSyncState,
  StudyDraft,
} from "./types/vineyard";
import { buildPlotHistoryData, getMarkersForPlot } from "./utils/chartData";
import { generateId } from "./utils/formatters";
import { FieldLogView } from "./views/FieldLogView";
import { OverviewView } from "./views/OverviewView";
import { PlotDetailView } from "./views/PlotDetailView";
import { PlotsView } from "./views/PlotsView";
import { SettingsView } from "./views/SettingsView";
import { StudiesView } from "./views/StudiesView";

type AppView =
  | NavigationKey
  | "plot-detail"
  | "create-study"
  | "study-result";

function getSidebarView(activeView: AppView): NavigationKey {
  if (activeView === "plot-detail") {
    return "plots";
  }

  if (activeView === "create-study" || activeView === "study-result") {
    return "studies";
  }

  return activeView;
}

function App() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [activeView, setActiveView] = useState<AppView>("overview");
  const [selectedPlotId, setSelectedPlotId] = useState("plot-a");
  const [selectedStudyId, setSelectedStudyId] = useState("study-irrigation-a");
  const [isEventFormOpen, setIsEventFormOpen] = useState(false);
  const [isSavingEvent, setIsSavingEvent] = useState(false);
  const [isCreatingStudy, setIsCreatingStudy] = useState(false);
  const [synchronizingStudyId, setSynchronizingStudyId] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    vineyardService
      .getDashboardData()
      .then((data) => {
        if (!isMounted) {
          return;
        }

        setDashboardData(data);
        setSelectedPlotId(data.plots[0]?.id ?? "plot-a");
        setSelectedStudyId(data.studies[0]?.id ?? "");
      })
      .catch(() => {
        if (isMounted) {
          setError("Brainyard could not load local vineyard data.");
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const selectedPlot = useMemo(
    () => dashboardData?.plots.find((plot) => plot.id === selectedPlotId),
    [dashboardData?.plots, selectedPlotId],
  );

  const selectedStudy = useMemo(
    () => dashboardData?.studies.find((study) => study.id === selectedStudyId),
    [dashboardData?.studies, selectedStudyId],
  );

  const pageTitle = useMemo(() => {
    if (activeView === "overview") {
      return "Vineyard Overview";
    }

    if (activeView === "plots") {
      return "Plots";
    }

    if (activeView === "field-log") {
      return "Field Log";
    }

    if (activeView === "studies") {
      return "Studies";
    }

    if (activeView === "settings") {
      return "Settings";
    }

    if (activeView === "plot-detail" && selectedPlot) {
      return `${selectedPlot.name} Detail`;
    }

    if (activeView === "create-study") {
      return "Create Study";
    }

    if (activeView === "study-result") {
      return "Study Result";
    }

    return "Brainyard";
  }, [activeView, selectedPlot]);

  useEffect(() => {
    document.title = `Brainyard | ${pageTitle}`;
  }, [pageTitle]);

  useEffect(() => {
    if (!toastMessage) {
      return;
    }

    const timeout = window.setTimeout(() => setToastMessage(""), 4200);
    return () => window.clearTimeout(timeout);
  }, [toastMessage]);

  function handleNavigate(view: NavigationKey) {
    setActiveView(view);
  }

  function handleSelectPlot(plotId: string) {
    setSelectedPlotId(plotId);
    setActiveView("plot-detail");
  }

  async function handleCreateFieldEvent(draft: FieldEventDraft) {
    if (!dashboardData) {
      return;
    }

    setIsSavingEvent(true);

    try {
      const fieldEvent = await vineyardService.createFieldEvent(draft);
      const plot = dashboardData.plots.find((item) => item.id === fieldEvent.plotId);
      const plotLabel = plot ? `${plot.name} - ${plot.fieldName}` : "selected plot";
      const activity: Activity = {
        id: generateId("activity"),
        type: fieldEvent.type === "Irrigation" ? "irrigation" : "event",
        title: `${fieldEvent.type} recorded`,
        description: `${fieldEvent.durationMinutes}-minute ${fieldEvent.type.toLowerCase()} added for ${plotLabel}.`,
        timestamp: fieldEvent.createdAt,
      };

      setDashboardData((current) =>
        current
          ? {
              ...current,
              fieldEvents: [fieldEvent, ...current.fieldEvents],
              activities: [activity, ...current.activities],
            }
          : current,
      );
      setIsEventFormOpen(false);
      setToastMessage("Field event recorded successfully.");
    } finally {
      setIsSavingEvent(false);
    }
  }

  async function handleCreateStudy(draft: StudyDraft) {
    setIsCreatingStudy(true);

    try {
      const study = await vineyardService.createStudy(draft);
      setDashboardData((current) =>
        current
          ? {
              ...current,
              studies: [study, ...current.studies],
            }
          : current,
      );
      setSelectedStudyId(study.id);
      setActiveView("study-result");
      setToastMessage("Study created and evidence package prepared.");
    } finally {
      setIsCreatingStudy(false);
    }
  }

  function updateStudySyncState(studyId: string, syncState: FlywheelSyncState) {
    setDashboardData((current) =>
      current
        ? {
            ...current,
            studies: current.studies.map((study) =>
              study.id === studyId
                ? {
                    ...study,
                    syncState,
                    status: syncState === "synchronized" ? "Synchronized" : study.status,
                  }
                : study,
            ),
          }
        : current,
    );
  }

  async function handleSynchronizeStudy() {
    if (!selectedStudy) {
      return;
    }

    setSynchronizingStudyId(selectedStudy.id);

    try {
      await flywheelService.synchronizeStudy(selectedStudy.id, (state) => {
        updateStudySyncState(selectedStudy.id, state);
      });
      setToastMessage("Evidence package synchronized with Flywheel.");
    } finally {
      setSynchronizingStudyId(null);
    }
  }

  if (isLoading) {
    return (
      <main className="standalone-state">
        <LoadingState />
      </main>
    );
  }

  if (error || !dashboardData) {
    return (
      <main className="standalone-state">
        <section className="state-card state-card--error">
          <h1>Brainyard</h1>
          <p>{error || "Local vineyard data is unavailable."}</p>
        </section>
      </main>
    );
  }

  const selectedStudyPlot = selectedStudy
    ? dashboardData.plots.find((plot) => plot.id === selectedStudy.plotId)
    : undefined;

  return (
    <div className="app-shell">
      <Sidebar activeView={getSidebarView(activeView)} onNavigate={handleNavigate} />

      <div className="app-content">
        <Header
          pageTitle={pageTitle}
          vineyard={dashboardData.vineyard}
          onCreateStudy={() => setActiveView("create-study")}
          onRecordEvent={() => setIsEventFormOpen(true)}
        />

        {toastMessage ? (
          <div className="toast" role="status" aria-live="polite">
            {toastMessage}
          </div>
        ) : null}

        <main>
          {activeView === "overview" ? (
            <OverviewView
              activities={dashboardData.activities}
              alerts={dashboardData.alerts}
              irrigationMarkers={dashboardData.irrigationMarkers}
              measurements={dashboardData.measurements}
              plots={dashboardData.plots}
              onSelectPlot={handleSelectPlot}
            />
          ) : null}

          {activeView === "plots" ? (
            <PlotsView plots={dashboardData.plots} onSelectPlot={handleSelectPlot} />
          ) : null}

          {activeView === "plot-detail" && selectedPlot ? (
            <PlotDetailView
              fieldEvents={dashboardData.fieldEvents}
              irrigationMarkers={dashboardData.irrigationMarkers}
              measurements={dashboardData.measurements}
              plot={selectedPlot}
              sensors={dashboardData.sensors}
              onAnalyzeIrrigationResponse={() => setActiveView("create-study")}
              onBack={() => setActiveView("overview")}
            />
          ) : null}

          {activeView === "field-log" ? (
            <FieldLogView
              fieldEvents={dashboardData.fieldEvents}
              plots={dashboardData.plots}
              onRecordEvent={() => setIsEventFormOpen(true)}
            />
          ) : null}

          {activeView === "studies" ? (
            <StudiesView
              plots={dashboardData.plots}
              studies={dashboardData.studies}
              onCreateStudy={() => setActiveView("create-study")}
              onOpenStudy={(studyId) => {
                setSelectedStudyId(studyId);
                setActiveView("study-result");
              }}
            />
          ) : null}

          {activeView === "create-study" ? (
            <StudyForm
              fieldEvents={dashboardData.fieldEvents}
              isSubmitting={isCreatingStudy}
              plots={dashboardData.plots}
              onCancel={() => setActiveView("studies")}
              onSubmit={handleCreateStudy}
            />
          ) : null}

          {activeView === "study-result" && selectedStudy && selectedStudyPlot ? (
            <StudyResult
              chartData={buildPlotHistoryData(dashboardData.measurements, selectedStudy.plotId)}
              isSynchronizing={synchronizingStudyId === selectedStudy.id}
              markers={getMarkersForPlot(dashboardData.irrigationMarkers, selectedStudy.plotId)}
              plot={selectedStudyPlot}
              study={selectedStudy}
              syncState={selectedStudy.syncState}
              onBack={() => setActiveView("studies")}
              onSynchronize={handleSynchronizeStudy}
            />
          ) : null}

          {activeView === "settings" ? <SettingsView /> : null}
        </main>
      </div>

      {isEventFormOpen ? (
        <EventForm
          isSubmitting={isSavingEvent}
          plots={dashboardData.plots}
          onClose={() => setIsEventFormOpen(false)}
          onSubmit={handleCreateFieldEvent}
        />
      ) : null}
    </div>
  );
}

export default App;
