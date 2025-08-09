import json
import os
from datetime import datetime
from typing import Optional

try:
    from google.cloud import pubsub_v1  # type: ignore
except Exception:  # pragma: no cover - optional dependency at runtime
    pubsub_v1 = None  # type: ignore


def _get_topic_path() -> Optional[str]:
    """
    Resolve the Pub/Sub topic path from environment variables.
    Prefer a fully-qualified path in PUBSUB_TOPIC (projects/<id>/topics/<name>).
    Otherwise, build it from GCP_PROJECT and PUBSUB_TOPIC_ID.
    Returns None if publishing is disabled or misconfigured.
    """
    if os.getenv("PUBSUB_ENABLED", "false").lower() != "true":
        return None

    explicit_topic = os.getenv("PUBSUB_TOPIC")
    if explicit_topic and explicit_topic.startswith("projects/"):
        return explicit_topic

    project_id = os.getenv("GCP_PROJECT")
    topic_id = os.getenv("PUBSUB_TOPIC_ID", "device-locations")
    if not project_id:
        return None

    return f"projects/{project_id}/topics/{topic_id}"


def publish_location_update(
    *,
    device_id: str,
    latitude: float,
    longitude: float,
    timestamp: datetime,
) -> None:
    """
    Publish a location update event to Pub/Sub if configured.
    Failures are swallowed so app requests are not impacted.
    """
    topic_path = _get_topic_path()
    if not topic_path or pubsub_v1 is None:
        return

    try:
        publisher = pubsub_v1.PublisherClient()
        payload = {
            "device_id": device_id,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp.isoformat(),
            "event_type": "location_update",
            "source": "traceit-api",
            "version": "v1",
        }
        future = publisher.publish(topic_path, json.dumps(payload).encode("utf-8"))
        future.add_done_callback(lambda _f: None)
    except Exception:
        # Intentionally ignore to keep the API resilient if Pub/Sub is unreachable.
        return
