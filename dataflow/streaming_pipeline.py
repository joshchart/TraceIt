import argparse
import json
import logging
import os
from datetime import datetime
from typing import Dict

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions, StandardOptions
import psycopg2


def parse_event(message: bytes) -> Dict:
    data = json.loads(message.decode("utf-8"))
    # Basic validation
    for key in ("device_id", "latitude", "longitude", "timestamp"):
        if key not in data:
            raise ValueError(f"Missing field: {key}")
    return data


def upsert_location_to_postgres(row: Dict) -> None:
    dsn = os.getenv("DATABASE_URL_SYNC")
    if not dsn:
        raise RuntimeError("DATABASE_URL_SYNC must be set for Dataflow pipeline")

    # psycopg2 does not support async, so use a separate DSN for sync driver.
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            # Ensure geometry creation using PostGIS
            cur.execute(
                """
                UPDATE devices
                SET coordinates = ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    timestamp = %s
                WHERE id = %s::uuid
                """,
                (
                    float(row["longitude"]),
                    float(row["latitude"]),
                    datetime.fromisoformat(row["timestamp"]),
                    row["device_id"],
                ),
            )
            if cur.rowcount == 0:
                logging.warning("Device not found in DB for id=%s", row["device_id"])
        conn.commit()
    finally:
        conn.close()


class ParseAndWrite(beam.DoFn):
    def process(self, element: Dict):
        try:
            payload = parse_event(element)
            upsert_location_to_postgres(payload)
            yield payload
        except Exception as exc:
            logging.exception("Failed processing message: %s", exc)
            # Drop or route to DLQ in future
            return


def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_topic", required=True)
    known_args, pipeline_args = parser.parse_known_args(argv)

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    pipeline_options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            | "ReadFromPubSub" >> beam.io.ReadFromPubSub(topic=known_args.input_topic)
            | "ToDict" >> beam.Map(parse_event)
            | "UpsertToPostgres" >> beam.Map(upsert_location_to_postgres)
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
