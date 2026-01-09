# TraceIt

Real-time item location tracking application built with FastAPI and Google Cloud Platform.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Devices   │────▶│  Cloud Run  │────▶│   Pub/Sub   │────▶│  Dataflow   │
│  (Clients)  │     │   (API)     │     │   (Queue)   │     │  (Stream)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                                       │
                           ▼                                       ▼
                    ┌─────────────┐                         ┌─────────────┐
                    │   Cloud     │                         │ PostgreSQL  │
                    │ Monitoring  │                         │  + PostGIS  │
                    └─────────────┘                         └─────────────┘
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API** | Cloud Run + FastAPI | Serverless API with auto-scaling |
| **Queue** | Pub/Sub | Async message buffering for reliability |
| **Stream Processor** | Dataflow (Apache Beam) | Real-time location processing |
| **Database** | PostgreSQL + PostGIS | Geospatial data storage |
| **IaC** | Terraform | Infrastructure as Code |
| **CI/CD** | GitHub Actions | Automated testing and deployment |
| **Monitoring** | Cloud Monitoring | Uptime checks and alerting |

## Features

- Register users and devices
- Update device locations in real-time
- Query current device locations
- Geospatial queries (PostGIS)
- Highly available ingestion pipeline
- Auto-scaling from 0 to thousands of requests

## Quick Start

### Prerequisites

- Python 3.11+
- Docker
- Google Cloud SDK (`gcloud`)
- Terraform (for infrastructure)
- Vegeta (for load testing)

### Local Development

1. **Clone and setup:**
   ```bash
   git clone https://github.com/joshchart/TraceIt.git
   cd TraceIt
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your DATABASE_URL
   ```

3. **Run locally:**
   ```bash
   uvicorn src.main:app --reload
   ```

4. **Access API docs:** http://127.0.0.1:8000/docs

### Docker

```bash
# Build
docker build -t traceit .

# Run
docker run --name traceit -p 8080:8080 --env-file .env traceit
```

## API Reference

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/users` | Create a user |
| `GET` | `/api/v1/users` | List all users |
| `GET` | `/api/v1/users/{id}` | Get a specific user |
| `DELETE` | `/api/v1/users/{id}` | Delete a user |

### Devices

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/users/{user_id}/devices` | Register a device |
| `GET` | `/api/v1/devices` | List all devices |
| `GET` | `/api/v1/devices/{id}` | Get device info |
| `GET` | `/api/v1/devices/{id}/location` | Get device location |
| `POST` | `/api/v1/devices/{id}/locations` | Update device location |
| `DELETE` | `/api/v1/devices/{id}` | Delete a device |

### Example Requests

```bash
# Create a user
curl -X POST https://traceit-dev-nqmvtusa7q-uc.a.run.app/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Register a device
curl -X POST https://traceit-dev-nqmvtusa7q-uc.a.run.app/api/v1/users/{user_id}/devices \
  -H "Content-Type: application/json" \
  -d '{"device_name": "Phone", "latitude": 37.7749, "longitude": -122.4194, "timestamp": "2026-01-09T12:00:00Z"}'

# Update location
curl -X POST https://traceit-dev-nqmvtusa7q-uc.a.run.app/api/v1/devices/{device_id}/locations \
  -H "Content-Type: application/json" \
  -d '{"latitude": 40.7128, "longitude": -74.0060, "timestamp": "2026-01-09T12:30:00Z"}'
```

## Testing

### Unit Tests

```bash
pip install -r requirements-test.txt
pytest
```

### Load Testing

Uses [Vegeta](https://github.com/tsenart/vegeta) for HTTP load testing.

```bash
# Install Vegeta (macOS)
brew install vegeta

# Run load tests (50, 100, 200 req/s)
./load_test.sh

# View results
cat report.txt
open plot.html
```

## Infrastructure

### Terraform

Infrastructure is managed with Terraform in the `terraform/` directory.

```bash
cd terraform

# Initialize
terraform init

# Preview changes
terraform plan

# Apply changes
terraform apply
```

**Managed Resources:**
- Cloud Run service
- Pub/Sub topic and subscription
- Uptime monitoring check
- Alert policy

### Dataflow Pipeline

The streaming pipeline processes location updates from Pub/Sub.

```bash
# Start the pipeline
python dataflow/streaming_pipeline.py

# Check status
gcloud dataflow jobs list --region=us-central1

# Stop the pipeline (to save costs)
gcloud dataflow jobs cancel $(gcloud dataflow jobs list --region=us-central1 --status=active --format="value(id)") --region=us-central1
```

## CI/CD

### Continuous Integration

Runs on every push to any branch:
- Builds Docker image
- Runs pytest against PostgreSQL + PostGIS container
- 12 tests covering users, devices, and locations

### Deployment

Manual deployment via GitHub Actions workflow dispatch:

1. Go to **Actions** > **Deploy**
2. Click **Run workflow**
3. Select environment (`dev`)
4. Click **Run workflow**

Deployment uses OIDC authentication (no stored credentials).

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL async connection string |
| `DATABASE_URL_SYNC` | PostgreSQL sync connection string (for Dataflow) |
| `BASE_URL` | API base URL for load testing |
| `PUBSUB_ENABLED` | Enable Pub/Sub publishing (`true`/`false`) |
| `GCP_PROJECT` | GCP project ID |
| `PUBSUB_TOPIC_ID` | Pub/Sub topic name |
| `ECHO_SQL` | Log SQL queries (`True`/`False`) |

## Cost Management

### Pause All Services

To stop incurring costs, cancel the Dataflow job:

```bash
gcloud dataflow jobs cancel $(gcloud dataflow jobs list --region=us-central1 --status=active --format="value(id)") --region=us-central1
```

Cloud Run automatically scales to zero when not in use.

### Resume Services

```bash
python dataflow/streaming_pipeline.py
```

## Project Structure

```
TraceIt/
├── src/
│   ├── app/
│   │   ├── models.py      # SQLAlchemy models
│   │   ├── router.py      # API endpoints
│   │   ├── schemas.py     # Pydantic schemas
│   │   └── service.py     # Business logic
│   ├── database.py        # Database connection
│   ├── config.py          # Configuration
│   └── main.py            # FastAPI app
├── tests/
│   ├── conftest.py        # Pytest fixtures
│   └── test_app.py        # API tests
├── dataflow/
│   ├── streaming_pipeline.py  # Beam pipeline
│   └── setup.py           # Worker dependencies
├── terraform/
│   └── main.tf            # Infrastructure
├── .github/workflows/
│   ├── ci.yml             # CI pipeline
│   └── deploy.yml         # Deploy pipeline
├── Dockerfile
├── requirements.txt
├── requirements-test.txt
└── load_test.sh
```

## License

MIT
