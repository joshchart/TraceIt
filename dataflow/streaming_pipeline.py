import argparse
import json
import logging
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


class WriteToPostgres(beam.DoFn):
    """DoFn that writes location updates to PostgreSQL."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._conn = None
    
    def setup(self):
        """Called once per worker to establish connection."""
        self._conn = psycopg2.connect(self.database_url)
    
    def teardown(self):
        """Called when worker is shutting down."""
        if self._conn:
            self._conn.close()
    
    def process(self, row: Dict):
        try:
            with self._conn.cursor() as cur:
                # Parse timestamp - handle both formats
                ts = row["timestamp"]
                if isinstance(ts, str):
                    # Remove timezone suffix if present for fromisoformat compatibility
                    ts = ts.replace("Z", "+00:00")
                    ts = datetime.fromisoformat(ts)
                
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
                        ts,
                        row["device_id"],
                    ),
                )
                if cur.rowcount == 0:
                    logging.warning("Device not found in DB for id=%s", row["device_id"])
                else:
                    logging.info("Updated location for device %s", row["device_id"])
            self._conn.commit()
            yield row
        except Exception as exc:
            logging.exception("Failed processing message: %s", exc)
            self._conn.rollback()
            # Don't yield - effectively drops the message


def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_topic", required=True)
    parser.add_argument("--database_url", required=True, help="PostgreSQL connection string")
    known_args, pipeline_args = parser.parse_known_args(argv)

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    pipeline_options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            | "ReadFromPubSub" >> beam.io.ReadFromPubSub(topic=known_args.input_topic)
            | "ParseJSON" >> beam.Map(parse_event)
            | "WriteToPostgres" >> beam.ParDo(WriteToPostgres(known_args.database_url))
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
