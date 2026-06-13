import json
import os
from typing import Optional
from urllib import error, request

from .models import FieldEvent, Measurement, Plot, StudyDraft


def openai_enabled() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def fallback_study_insight(
    draft: StudyDraft,
    plot: Plot,
    measurements: list[Measurement],
    related_event: Optional[FieldEvent],
) -> dict[str, str]:
    if measurements:
        start_moisture = measurements[0].soilMoisture
        end_moisture = measurements[-1].soilMoisture
        min_moisture = min(item.soilMoisture for item in measurements)
        max_temp = max(item.airTemperature for item in measurements)
    else:
        start_moisture = end_moisture = min_moisture = plot.soilMoisture
        max_temp = plot.airTemperature

    moisture_delta = round(end_moisture - start_moisture, 1)
    event_text = f" after the {related_event.type.lower()} event" if related_event else " during the selected window"

    if plot.soilMoisture < 20:
        interpretation = (
            f"{plot.name} is showing a credible water stress pattern: current soil moisture is "
            f"{plot.soilMoisture:.1f}%, the lowest observed value is {min_moisture:.1f}%, "
            f"and canopy temperature reached {max_temp:.1f}°C. Irrigation should be prioritized unless rain is imminent."
        )
        next_step = "Schedule irrigation within 24 hours and re-check soil moisture two hours after completion."
    elif moisture_delta > 4:
        interpretation = (
            f"The measurements suggest a positive irrigation response{event_text}. "
            f"Soil moisture changed by {moisture_delta:+.1f} percentage points across the observation window."
        )
        next_step = "Keep monitoring the decay curve and compare the response with the next irrigation cycle."
    else:
        interpretation = (
            f"{plot.name} appears stable, but the signal should remain under observation. "
            f"The moisture change was {moisture_delta:+.1f} percentage points with current moisture at {plot.soilMoisture:.1f}%."
        )
        next_step = "Schedule a field inspection tomorrow morning and continue routine sensor checks."

    return {
        "observation": (
            f"For {plot.name} - {plot.fieldName}, {len(measurements)} sensor readings were reviewed. "
            f"Soil moisture moved from {start_moisture:.1f}% to {end_moisture:.1f}%{event_text}."
        ),
        "interpretation": interpretation,
        "limitations": (
            "This hackathon analysis combines one real soil moisture signal with simulated vineyard context. "
            "It is useful for operational triage, but it should not be treated as a scientific agronomy model."
        ),
        "suggestedNextStep": next_step,
    }


def generate_study_insight(
    draft: StudyDraft,
    plot: Plot,
    measurements: list[Measurement],
    related_event: Optional[FieldEvent],
) -> dict[str, str]:
    if not openai_enabled():
        return fallback_study_insight(draft, plot, measurements, related_event)

    fallback = fallback_study_insight(draft, plot, measurements, related_event)
    api_key = os.environ["OPENAI_API_KEY"]
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    prompt = {
        "task": "Generate concise, believable vineyard decision-support study fields for a hackathon dashboard.",
        "output_schema": {
            "observation": "string",
            "interpretation": "string",
            "limitations": "string",
            "suggestedNextStep": "string",
        },
        "research_question": draft.researchQuestion,
        "plot": plot.dict(),
        "date_range": draft.dateRange.dict(),
        "metrics": draft.metrics,
        "notes": draft.notes,
        "related_event": related_event.dict() if related_event else None,
        "measurements": [item.dict() for item in measurements[-24:]],
        "style": "clear, operational, under 70 words per field, no scientific overclaiming",
    }
    body = json.dumps(
        {
            "model": model,
            "input": [
                {
                    "role": "system",
                    "content": "You are an agronomy decision-support assistant. Return only valid JSON.",
                },
                {"role": "user", "content": json.dumps(prompt)},
            ],
            "text": {"format": {"type": "json_object"}},
            "temperature": 0.4,
        }
    ).encode("utf-8")
    req = request.Request(
        "https://api.openai.com/v1/responses",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=20) as response:
            raw = json.loads(response.read().decode("utf-8"))
        text = raw.get("output_text")
        if not text:
            for item in raw.get("output", []):
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        text = content.get("text")
                        break
        parsed = json.loads(text or "{}")
        return {
            "observation": parsed.get("observation") or fallback["observation"],
            "interpretation": parsed.get("interpretation") or fallback["interpretation"],
            "limitations": parsed.get("limitations") or fallback["limitations"],
            "suggestedNextStep": parsed.get("suggestedNextStep") or fallback["suggestedNextStep"],
        }
    except (error.URLError, TimeoutError, json.JSONDecodeError, KeyError):
        return fallback
