# TraceIt

## Overview
TraceIt is a location tracking application built with FastAPI. It allows users to register devices, update their locations, and retrieve the current location of a device. The application is deployed on Google Cloud using Cloud Run, and it is unit tested with pytest and load testing with Vegeta.

## Features
- Register Users
- Register devices
- Update device locations
- Retrieve current location of a device
- List specific/all registered users/devices

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
### Running locally
1. Run the FastAPI application:
   ```sh
   uvicorn src.main:app --reload
   ```

2. Access the API documentation at `http://127.0.0.1:8000/docs`.

### Running locally with docker
1. Build image:
   ```sh
   docker build -t traceit_image .
   ```
2. Run container:
   ```sh
   docker run --name traceit -p 8080:8080 --env-file .env traceit_image
   ```

## Deploying to Google Cloud Run

We use Docker Buildx for building and pushing the Docker images because of architecture mismatches. When Docker images are built on a machine with a different architecture (e.g., an Apple M1 Mac which uses ARM architecture) and then run on Google Cloud Run, which typically uses x86_64 (amd64) architecture, it can cause issues such as the "exec format error." This error occurs because the binaries compiled for ARM architecture are not compatible with x86_64 architecture.

### Building and Pushing Main App Image
1. **Create and use a new Buildx builder:**
   ```sh
   docker buildx create --use
   ```

2. **Build and push the main app Docker image:**
   ```sh
   docker buildx build --platform linux/amd64 -t gcr.io/<PROJECT-ID>/<IMAGE-NAME> --push -f <DOCKERFILE-PATH> .
   ```

3. **Deploy the main app to Cloud Run:**
   ```sh
   gcloud run deploy <SERVICE-NAME> \
       --image gcr.io/<PROJECT-ID>/<IMAGE-NAME> \
       --platform managed \
       --region <REGION> \
       --allow-unauthenticated \
       --set-env-vars DATABASE_URL=postgresql+asyncpg://<DB-USER>:<DB-PASSWORD>@<DB-HOST>/<DB-NAME>,ECHO_SQL=True
   ```

## Running Tests
### Unit testing with pytest
Make sure to `DATABASE_URL` in `src/database.py` and uncomment `NullPool` related code. To run the tests, use the following command:

1. Install the dependencies:
   ```sh
   pip install -r requirements-text.txt
   ```
2. Might need to activate venv again
   ```sh
   source venv/bin/activate
   ```

3. Run unit tests
   ```sh
   pytest
   ```

### Load Testing with Vegeta
Currently when load testing using local environment and running script. In the future planning on create a Google Batch Job to run the tests.

1. Make sure  `.env` file has `BASE_URL` and `DATABASE_URL` setup.

2. To change duration or QPS update `DURATION` and `RATE` respectively in `load_test.sh`

3. Make the script executable:
   ```sh
   chmod +x load_test.sh
   ```
4. Run `load_test.sh`
   ```sh
   ./load_test.sh
   ```
5. Results will print in terminal and be added to `report.txt`

6. Acess diagram in `plot.html`:
   ```sh
   open plot.html
   ```

## Design Decision and Additional Considerations:
- Used pooled connection to help increase concurrent limit increasing QPS
- Using Google Cloud Run since it is fully managed and autoscales container
