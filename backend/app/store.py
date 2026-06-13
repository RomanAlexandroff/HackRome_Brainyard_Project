from typing import Optional

from .models import (
    Activity,
    Alert,
    Artifact,
    DashboardData,
    EvidenceSummary,
    FieldEvent,
    FieldEventDraft,
    IrrigationMarker,
    Measurement,
    SensorReading,
    Study,
    StudyDraft,
    now_iso,
)
from .openai_service import generate_study_insight


class VineyardStore:
    def __init__(self, dashboard: DashboardData):
        self.dashboard = dashboard
        self.latest_sensor_reading: Optional[SensorReading] = None
        self._field_event_counter = 1
        self._study_counter = 1

    def get_dashboard(self) -> DashboardData:
        return self.dashboard

    def get_latest_sensor_reading(self) -> Optional[SensorReading]:
        return self.latest_sensor_reading

    def ingest_sensor_reading(self, reading: SensorReading) -> SensorReading:
        timestamp = reading.timestamp or now_iso()
        reading.timestamp = timestamp
        self.latest_sensor_reading = reading
        self.dashboard.vineyard.lastSensorUpdate = timestamp

        plot = next((item for item in self.dashboard.plots if item.id == reading.plotId), None)
        if plot:
            plot.soilMoisture = reading.soilMoisture
            plot.status = "Water stress risk" if reading.soilMoisture < 20 else "Healthy"

        sensor = next((item for item in self.dashboard.sensors if item.id == reading.sensorId), None)
        if sensor:
            sensor.lastReading = reading.soilMoisture
            sensor.batteryLevel = reading.batteryLevel
            sensor.status = reading.status

        self.dashboard.measurements.append(
            Measurement(
                id=f"measurement-live-{len(self.dashboard.measurements) + 1}",
                plotId=reading.plotId,
                timestamp=timestamp,
                soilMoisture=reading.soilMoisture,
                airTemperature=plot.airTemperature if plot else 27.0,
                airHumidity=plot.airHumidity if plot else 55,
                rainfall=0,
            )
        )
        self._upsert_sensor_alert(reading)
        return reading

    def create_field_event(self, draft: FieldEventDraft) -> FieldEvent:
        created_at = now_iso()
        event = FieldEvent(
            id=f"field-event-{self._field_event_counter}",
            plotId=draft.plotId,
            type=draft.type,
            date=draft.date,
            time=draft.time,
            durationMinutes=draft.durationMinutes,
            notes=draft.notes,
            createdAt=created_at,
        )
        self._field_event_counter += 1
        self.dashboard.fieldEvents.insert(0, event)
        self.dashboard.activities.insert(
            0,
            Activity(
                id=f"activity-event-{self._field_event_counter}",
                type="irrigation" if event.type == "Irrigation" else "event",
                title=f"{event.type} recorded",
                description=f"{event.durationMinutes}-minute {event.type.lower()} added for {self._plot_label(event.plotId)}.",
                timestamp=created_at,
            ),
        )
        if event.type == "Irrigation":
            self.dashboard.irrigationMarkers.append(
                IrrigationMarker(timestamp=f"{event.date}T{event.time}:00+02:00", plotId=event.plotId, label="Irrigation event")
            )
        return event

    def create_study(self, draft: StudyDraft) -> Study:
        plot = next((item for item in self.dashboard.plots if item.id == draft.plotId), self.dashboard.plots[0])
        measurements = [item for item in self.dashboard.measurements if item.plotId == draft.plotId]
        related_event = None
        if draft.relatedFieldEventId:
            related_event = next((item for item in self.dashboard.fieldEvents if item.id == draft.relatedFieldEventId), None)

        insight = generate_study_insight(draft, plot, measurements, related_event)
        created_at = now_iso()
        field_events_count = len([item for item in self.dashboard.fieldEvents if item.plotId == draft.plotId])
        title_topic = "Irrigation response" if "irrig" in draft.researchQuestion.lower() else "AI vineyard assessment"
        study = Study(
            id=f"study-{self._study_counter}",
            title=f"{title_topic} in {plot.name}",
            researchQuestion=draft.researchQuestion,
            plotId=draft.plotId,
            dateRange=draft.dateRange,
            metrics=draft.metrics,
            relatedFieldEventId=draft.relatedFieldEventId,
            notes=draft.notes,
            status="Ready for review",
            observation=insight["observation"],
            evidence=EvidenceSummary(
                sensorReadings=len(measurements),
                fieldEvents=field_events_count,
                observationWindow="Selected observation window",
                generatedArtifacts=3,
            ),
            interpretation=insight["interpretation"],
            limitations=insight["limitations"],
            suggestedNextStep=insight["suggestedNextStep"],
            artifacts=[
                Artifact(id="artifact-measurements", name="measurements.csv", type="csv", size="18 KB"),
                Artifact(id="artifact-metadata", name="study-metadata.json", type="json", size="4 KB"),
                Artifact(id="artifact-ai-summary", name="openai-study-summary.json", type="json", size="6 KB"),
            ],
            syncState="not_synchronized",
            createdAt=created_at,
        )
        self._study_counter += 1
        self.dashboard.studies.insert(0, study)
        self.dashboard.activities.insert(
            0,
            Activity(
                id=f"activity-study-{self._study_counter}",
                type="study",
                title="OpenAI study generated",
                description=f"AI evidence package prepared for {plot.name} using sensor readings and field context.",
                timestamp=created_at,
            ),
        )
        return study

    def _plot_label(self, plot_id: str) -> str:
        plot = next((item for item in self.dashboard.plots if item.id == plot_id), None)
        return f"{plot.name} - {plot.fieldName}" if plot else "selected plot"

    def _upsert_sensor_alert(self, reading: SensorReading) -> None:
        self.dashboard.alerts = [
            alert for alert in self.dashboard.alerts if alert.id not in {"alert-live-low-moisture", "alert-live-low-battery"}
        ]
        if reading.soilMoisture < 20:
            self.dashboard.alerts.insert(
                0,
                Alert(
                    id="alert-live-low-moisture",
                    plotId=reading.plotId,
                    title="Low soil moisture detected from live sensor",
                    description=f"{reading.sensorId} reports {reading.soilMoisture:.1f}% soil moisture. Review irrigation priority within 24 hours.",
                    severity="critical",
                    timestamp=reading.timestamp or now_iso(),
                ),
            )
        if reading.batteryLevel < 25:
            self.dashboard.alerts.insert(
                0,
                Alert(
                    id="alert-live-low-battery",
                    plotId=reading.plotId,
                    title="Sensor battery below threshold",
                    description=f"{reading.sensorId} battery is at {reading.batteryLevel}%. Schedule replacement before the next monitoring cycle.",
                    severity="warning",
                    timestamp=reading.timestamp or now_iso(),
                ),
            )
