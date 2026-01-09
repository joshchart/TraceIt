# CI/CD and Infra Overview

This repository now includes:

- GitHub Actions CI that runs unit tests against a PostGIS-enabled Postgres container and builds the Docker image.
- GitHub Actions Deploy workflow using Workload Identity Federation for manual, human-in-the-loop deploys to Cloud Run.
- Optional Pub/Sub publishing for location updates (enable by setting PUBSUB_ENABLED=true and providing GCP project/topic).
- Terraform for Pub/Sub topic/subscription and Cloud Run service with env vars plus a basic uptime check. You can continue to use Pulumi or switch to Terraform.
- A Dataflow (Apache Beam) streaming job (`dataflow/streaming_pipeline.py`) that reads location updates from Pub/Sub and updates Postgres.

## Inputs and secrets

- GCP_PROJECT_ID, GCP_WORKLOAD_IDENTITY_PROVIDER, GCP_SERVICE_ACCOUNT_EMAIL must be provided as repo secrets for deploy workflow.
- DATABASE_URL (for Cloud Run) and DATABASE_URL_SYNC (for Dataflow psycopg2) need to be configured appropriately.
