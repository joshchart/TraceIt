# TraceIt

## Overview
TraceIt is a location tracking application built with FastAPI. It allows users to register devices, update their locations, and retrieve the current location of a device. The application is deployed on Google Cloud using Cloud Run, and it includes capabilities for load testing using Locust.

## Features
- Register devices
- Update device locations
- Retrieve current location of a device
- List all registered devices

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/joshchart/TraceIt.git
   cd traceit
   ```

2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Set up the environment variables (create a `.env` file):
   ```sh
   touch .env
   ```

## Usage
1. Run the FastAPI application:
   ```sh
   uvicorn src.main:app --reload
   ```

2. Access the API documentation at `http://127.0.0.1:8000/docs`.

## Running Tests
To run the tests, use the following command:
```sh
pytest
```

## Load Testing with Locust
The application includes load testing capabilities using Locust. You can deploy the Locust tests to Google Cloud Run and run them against the deployed application.

### Deploying to Google Cloud Run

We use Docker Buildx for building and pushing the Docker images because of architecture mismatches. When Docker images are built on a machine with a different architecture (e.g., an Apple M1 Mac which uses ARM architecture) and then run on Google Cloud Run, which typically uses x86_64 (amd64) architecture, it can cause issues such as the "exec format error." This error occurs because the binaries compiled for ARM architecture are not compatible with x86_64 architecture.

#### Building and Pushing Main App Image
1. **Create and use a new Buildx builder:**
   ```sh
   docker buildx create --use
   ```

2. **Build and push the main app Docker image:**
   ```sh
   docker buildx build --platform linux/amd64 -t LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY/IMAGE --push -f Dockerfile .
   ```

3. **Deploy the main app to Cloud Run:**
   ```sh
   gcloud run deploy main-app --image LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY/IMAGE --platform managed --region us-central1 --allow-unauthenticated
   ```

#### Building and Pushing Locust Image
1. **Create and use a new Buildx builder (if not already done):**
   ```sh
   docker buildx create --use
   ```

2. **Build and push the Locust Docker image (make sure tags are different):**
   ```sh
   docker buildx build --platform linux/amd64 -t LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY/IMAGE --push -f Dockerfile.locust .
   ```

3. **Deploy the Locust tests to Cloud Run:**
   ```sh
   gcloud run deploy locust-test --image gcr.io/<YOUR_PROJECT_ID>/traceit-test --platform managed --region us-central1 --allow-unauthenticated
   ```

### Running Load Tests Locally
If you want to run the load tests locally, you need to modify the `Dockerfile.locust` file:

1. **Uncomment the local host command:**
   ```Dockerfile
   CMD ["-f", "locustfile.py", "--host=http://app:8080"]
   ```

2. **Comment the Cloud Run host command:**
   ```Dockerfile
   CMD ["-f", "locustfile.py"]
   ```

3. **Run the load tests using Docker Compose:**
   ```sh
   docker compose up
   ```

### Accessing Locust Web Interface
After deploying the Locust service to Cloud Run, you can access the Locust web interface to configure and run load tests. Use the URL provided by Cloud Run for the `locust-test` service.