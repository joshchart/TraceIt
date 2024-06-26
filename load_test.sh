# Configuration
DURATION="60s"        # Duration of the test
RATE="1000"             # Requests per second (QPS)
TARGETS_FILE="targets.txt"
RESULTS_FILE="results.bin"
REPORT_FILE="report.txt"
PLOT_FILE="plot.html"

# UUID for the pre-registered device
DEVICE_UUID="00000000-0000-0000-0000-000000000000"

# Prepare the targets file with the necessary endpoints and payloads
cat <<EOF > $TARGETS_FILE
POST https://main-app-drdetwm72a-uc.a.run.app/api/v1/devices
Content-Type: application/json
@create_device.json

POST https://main-app-drdetwm72a-uc.a.run.app/api/v1/devices/$DEVICE_UUID/locations
Content-Type: application/json
@update_location.json

GET https://main-app-drdetwm72a-uc.a.run.app/api/v1/devices/$DEVICE_UUID/location

GET https://main-app-drdetwm72a-uc.a.run.app/api/v1/devices/$DEVICE_UUID

GET https://main-app-drdetwm72a-uc.a.run.app/api/v1/devices
EOF

# Check the targets file for correctness
echo "Contents of $TARGETS_FILE:"
cat $TARGETS_FILE

# Run the Vegeta attack
echo "Running Vegeta with $RATE requests per second for $DURATION..."
vegeta attack -duration=$DURATION -rate=$RATE -targets=$TARGETS_FILE | tee $RESULTS_FILE | vegeta report -type=text > $REPORT_FILE

# Generate a plot report
cat $RESULTS_FILE | vegeta plot > $PLOT_FILE

echo "Load test completed. Results:"
cat $REPORT_FILE
echo "Plot report generated at $PLOT_FILE"

