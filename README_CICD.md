# CI/CD and Infrastructure

## Overview

TraceIt uses GitHub Actions for CI/CD and Terraform for infrastructure management.

## CI Pipeline (`.github/workflows/ci.yml`)

**Triggers:** Every push to any branch

**Steps:**
1. Build Docker image
2. Spin up PostgreSQL + PostGIS container
3. Run pytest (12 tests)

**Test Coverage:**
- User CRUD operations
- Device registration
- Location updates and queries
- Cascade delete behavior
- 404 handling for non-existent resources

## Deploy Pipeline (`.github/workflows/deploy.yml`)

**Triggers:** Manual (`workflow_dispatch`)

**Steps:**
1. Authenticate to GCP via OIDC (Workload Identity Federation)
2. Build and push Docker image to Container Registry
3. Deploy new revision to Cloud Run

**Why manual deploy?**
- Human-in-the-loop for production safety
- Review changes before deploying
- Control deployment timing

### Running a Deploy

1. Go to **Actions** tab in GitHub
2. Select **Deploy** workflow
3. Click **Run workflow**
4. Choose environment (`dev`)
5. Click **Run workflow**

## GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `GCP_PROJECT_ID` | GCP project ID (`traceit-2026`) |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Full provider path |
| `GCP_SERVICE_ACCOUNT_EMAIL` | Deploy service account email |
| `DATABASE_URL` | PostgreSQL connection string |

## OIDC Authentication

We use Workload Identity Federation instead of service account keys:

- **No stored credentials** - More secure than JSON keys
- **Short-lived tokens** - GitHub proves identity to GCP
- **Auditable** - All authentications logged

### Setup Components

1. **Workload Identity Pool:** `github-actions`
2. **OIDC Provider:** Configured for `joshchart/TraceIt` repo
3. **Service Account:** `github-actions-deploy@traceit-2026.iam.gserviceaccount.com`

### Service Account Roles

- `roles/run.admin` - Deploy to Cloud Run
- `roles/iam.serviceAccountUser` - Act as service account
- `roles/storage.admin` - Push to Container Registry
- `roles/artifactregistry.writer` - Write to Artifact Registry
- `roles/artifactregistry.createOnPushWriter` - Create repos on push

## Terraform Infrastructure

Location: `terraform/`

### Backend

State stored in GCS bucket: `gs://traceit-2026-tfstate`

### Managed Resources

```hcl
google_cloud_run_service.traceit           # Cloud Run service
google_cloud_run_service_iam_member.invoker # Public access
google_pubsub_topic.device_locations        # Pub/Sub topic
google_pubsub_subscription.device_locations_sub # Subscription
google_monitoring_uptime_check_config.api_uptime # Health check
google_monitoring_alert_policy.uptime_alert # Alerting
```

### Commands

```bash
cd terraform

# Initialize (first time or after backend changes)
terraform init

# Preview changes
terraform plan

# Apply changes
terraform apply

# View current state
terraform show

# Destroy everything (careful!)
terraform destroy
```

### Variables

Create `terraform/terraform.tfvars`:

```hcl
project_id   = "traceit-2026"
region       = "us-central1"
database_url = "postgresql+asyncpg://..."
```

## Dataflow Pipeline

The streaming pipeline is deployed separately from Terraform.

### Start Pipeline

```bash
python dataflow/streaming_pipeline.py
```

### Stop Pipeline (Save Costs)

```bash
gcloud dataflow jobs cancel \
  $(gcloud dataflow jobs list --region=us-central1 --status=active --format="value(id)") \
  --region=us-central1
```

### Check Status

```bash
gcloud dataflow jobs list --region=us-central1
```

## Monitoring

### Uptime Check

- **Target:** `https://traceit-dev-nqmvtusa7q-uc.a.run.app/api/v1/devices`
- **Frequency:** Every 5 minutes
- **Locations:** Global

### Alert Policy

- **Condition:** Uptime check fails
- **Notification:** Configure in Cloud Console (email, Slack, PagerDuty, etc.)

### Cloud Logging

All Cloud Run requests are logged automatically. View logs:

```bash
gcloud logging read "resource.type=cloud_run_revision" --limit=50
```

Or in Cloud Console: **Logging** > **Logs Explorer**

## Local Testing

### Run CI Locally

```bash
# Start PostgreSQL with PostGIS
docker run -d --name postgres-test \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=traceit \
  -p 5432:5432 \
  postgis/postgis:15-3.3

# Set test database URL
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/traceit"

# Run tests
pip install -r requirements-test.txt
pytest
```

### Build Docker Image Locally

```bash
docker build -t traceit .
docker run -p 8080:8080 --env-file .env traceit
```
