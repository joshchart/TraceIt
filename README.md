# TraceIt

## Overview
TraceIt is a location tracking application built with FastAPI. It allows users to register devices, update their locations, and retrieve the current location of a device.

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