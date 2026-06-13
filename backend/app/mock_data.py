from copy import deepcopy

from .models import (
    Activity,
    Alert,
    Artifact,
    DashboardData,
    DateRange,
    EvidenceSummary,
    FieldEvent,
    IrrigationMarker,
    Measurement,
    Plot,
    Sensor,
    Study,
    Vineyard,
)


TREND_POINTS = [
    ("2026-06-12T14:30:00+02:00", 22.4, 22.0, 24.1, 26.1, 26.5, 25.7),
    ("2026-06-12T16:30:00+02:00", 21.9, 21.1, 23.8, 27.0, 27.4, 26.3),
    ("2026-06-12T18:30:00+02:00", 21.3, 20.4, 23.5, 26.7, 27.2, 26.0),
    ("2026-06-12T20:30:00+02:00", 26.6, 20.0, 23.3, 24.5, 25.1, 24.0),
    ("2026-06-12T22:30:00+02:00", 33.8, 19.7, 23.2, 22.8, 23.4, 22.5),
    ("2026-06-13T00:30:00+02:00", 32.9, 19.2, 23.0, 21.6, 22.0, 21.4),
    ("2026-06-13T02:30:00+02:00", 32.1, 18.9, 22.8, 20.9, 21.4, 20.8),
    ("2026-06-13T04:30:00+02:00", 31.4, 18.6, 22.6, 20.5, 21.0, 20.4),
    ("2026-06-13T06:30:00+02:00", 31.1, 18.3, 23.1, 22.2, 22.8, 21.9),
    ("2026-06-13T08:30:00+02:00", 30.6, 18.1, 23.9, 24.8, 25.3, 24.4),
    ("2026-06-13T10:30:00+02:00", 30.2, 17.9, 24.4, 26.3, 26.9, 25.8),
    ("2026-06-13T12:30:00+02:00", 29.8, 17.7, 24.8, 27.0, 27.8, 26.6),
    ("2026-06-13T14:30:00+02:00", 31.0, 18.0, 25.0, 27.2, 28.1, 26.8),
]


def build_measurements() -> list[Measurement]:
    measurements: list[Measurement] = []
    for index, point in enumerate(TREND_POINTS, start=1):
        timestamp, plot_a, plot_b, plot_c, temp_a, temp_b, temp_c = point
        measurements.extend(
            [
                Measurement(
                    id=f"measurement-a-{index}",
                    plotId="plot-a",
                    timestamp=timestamp,
                    soilMoisture=plot_a,
                    airTemperature=temp_a,
                    airHumidity=56 - round((index - 1) / 3),
                    rainfall=0,
                ),
                Measurement(
                    id=f"measurement-b-{index}",
                    plotId="plot-b",
                    timestamp=timestamp,
                    soilMoisture=plot_b,
                    airTemperature=temp_b,
                    airHumidity=51 - round((index - 1) / 4),
                    rainfall=0,
                ),
                Measurement(
                    id=f"measurement-c-{index}",
                    plotId="plot-c",
                    timestamp=timestamp,
                    soilMoisture=plot_c,
                    airTemperature=temp_c,
                    airHumidity=60 - round((index - 1) / 5),
                    rainfall=0,
                ),
            ]
        )
    return measurements


BASE_DASHBOARD = DashboardData(
    vineyard=Vineyard(
        id="vineyard-tenuta-verde",
        name="Tenuta Verde",
        location="Lazio, Italy",
        tagline="From vineyard data to evidence-based decisions.",
        lastSensorUpdate="2026-06-13T14:35:00+02:00",
    ),
    plots=[
        Plot(id="plot-a", name="Plot A", fieldName="North Field", soilMoisture=31, airTemperature=27.2, airHumidity=56, status="Healthy", activeSensors=3, areaHectares=1.8, grapeVariety="Sangiovese"),
        Plot(id="plot-b", name="Plot B", fieldName="South Field", soilMoisture=18, airTemperature=28.1, airHumidity=49, status="Water stress risk", activeSensors=3, areaHectares=2.1, grapeVariety="Merlot"),
        Plot(id="plot-c", name="Plot C", fieldName="Experimental Field", soilMoisture=25, airTemperature=26.8, airHumidity=59, status="Monitoring", activeSensors=2, areaHectares=0.9, grapeVariety="Mixed research rows"),
    ],
    sensors=[
        Sensor(id="soil-01", label="Soil sensor 01", plotId="plot-a", type="Soil moisture", batteryLevel=82, status="Online", lastReading=31, unit="%"),
        Sensor(id="air-01", label="Canopy climate 01", plotId="plot-a", type="Air temperature", batteryLevel=77, status="Online", lastReading=27.2, unit="°C"),
        Sensor(id="humidity-01", label="Humidity probe 01", plotId="plot-a", type="Air humidity", batteryLevel=64, status="Online", lastReading=56, unit="%"),
        Sensor(id="soil-02", label="Soil sensor 02", plotId="plot-b", type="Soil moisture", batteryLevel=53, status="Online", lastReading=18, unit="%"),
        Sensor(id="soil-03", label="Soil sensor 03", plotId="plot-b", type="Soil moisture", batteryLevel=18, status="Low battery", lastReading=17.4, unit="%"),
        Sensor(id="air-02", label="Canopy climate 02", plotId="plot-b", type="Air temperature", batteryLevel=71, status="Online", lastReading=28.1, unit="°C"),
        Sensor(id="soil-04", label="Soil sensor 04", plotId="plot-c", type="Soil moisture", batteryLevel=69, status="Online", lastReading=25, unit="%"),
        Sensor(id="rain-01", label="Rain gauge 01", plotId="plot-c", type="Rain gauge", batteryLevel=88, status="Online", lastReading=0, unit="mm"),
    ],
    measurements=build_measurements(),
    fieldEvents=[
        FieldEvent(id="event-irrigation-a", plotId="plot-a", type="Irrigation", date="2026-06-12", time="20:10", durationMinutes=20, notes="Drip irrigation applied to North Field blocks near soil-01.", createdAt="2026-06-12T20:35:00+02:00"),
        FieldEvent(id="event-inspection-b", plotId="plot-b", type="Agronomist inspection", date="2026-06-13", time="09:20", durationMinutes=35, notes="Checked leaf posture and soil surface dryness in South Field.", createdAt="2026-06-13T10:02:00+02:00"),
        FieldEvent(id="event-sampling-c", plotId="plot-c", type="Sampling", date="2026-06-13", time="11:45", durationMinutes=45, notes="Collected berry samples for experimental row comparison.", createdAt="2026-06-13T12:20:00+02:00"),
    ],
    alerts=[
        Alert(id="alert-low-moisture-b", plotId="plot-b", title="Low soil moisture detected in Plot B", description="Average soil moisture has stayed below 20% for the last 8 hours.", severity="critical", timestamp="2026-06-13T14:10:00+02:00"),
        Alert(id="alert-battery-soil-03", plotId="plot-b", title="Soil sensor 03 battery below 20%", description="Battery is at 18%. Schedule replacement before the next sampling cycle.", severity="warning", timestamp="2026-06-13T11:55:00+02:00"),
        Alert(id="alert-irrigation-response-a", plotId="plot-a", title="Irrigation response successfully recorded in Plot A", description="Soil moisture increased after a 20-minute irrigation event.", severity="info", timestamp="2026-06-12T23:05:00+02:00"),
    ],
    activities=[
        Activity(id="activity-irrigation-a", type="irrigation", title="Irrigation recorded", description="20-minute irrigation added for Plot A - North Field.", timestamp="2026-06-12T20:35:00+02:00"),
        Activity(id="activity-import", type="import", title="Sensor data imported", description="144 new readings received from the vineyard gateway.", timestamp="2026-06-13T14:35:00+02:00"),
        Activity(id="activity-note", type="note", title="Agronomist note added", description="Leaf posture suggests water stress risk in Plot B.", timestamp="2026-06-13T10:02:00+02:00"),
        Activity(id="activity-study-sync", type="study", title="Study synchronized with Flywheel", description="Irrigation response package prepared for research review.", timestamp="2026-06-12T23:20:00+02:00"),
    ],
    studies=[
        Study(
            id="study-irrigation-a",
            title="Irrigation response in Plot A",
            researchQuestion="Did the 20-minute irrigation sufficiently increase soil moisture in Plot A?",
            plotId="plot-a",
            dateRange=DateRange(start="2026-06-12", end="2026-06-13"),
            metrics=["Soil moisture", "Air temperature", "Air humidity"],
            relatedFieldEventId="event-irrigation-a",
            notes="Initial evidence package for the hackathon demo.",
            status="Ready for review",
            observation="Soil moisture increased from 21.3% to 33.8% after the irrigation event.",
            evidence=EvidenceSummary(sensorReadings=144, fieldEvents=1, observationWindow="24-hour observation window", generatedArtifacts=2),
            interpretation="The irrigation produced a measurable increase in soil moisture near sensor soil-01.",
            limitations="Only one irrigation event was analyzed. The measurement represents the area surrounding one sensor and should not be generalized to the entire plot.",
            suggestedNextStep="Repeat the same observation for at least three irrigation events and compare measurements at different soil depths.",
            artifacts=[
                Artifact(id="artifact-measurements", name="measurements.csv", type="csv", size="18 KB"),
                Artifact(id="artifact-metadata", name="study-metadata.json", type="json", size="4 KB"),
                Artifact(id="artifact-chart", name="soil-moisture-chart.png", type="image", size="92 KB"),
            ],
            syncState="not_synchronized",
            createdAt="2026-06-13T13:40:00+02:00",
        )
    ],
    irrigationMarkers=[IrrigationMarker(timestamp="2026-06-12T20:30:00+02:00", plotId="plot-a", label="Irrigation event")],
)


def fresh_dashboard() -> DashboardData:
    return deepcopy(BASE_DASHBOARD)
