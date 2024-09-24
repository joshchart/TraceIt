# Load environment variables
source .env

# Configuration
DURATION="30s"        # Duration of the test
RATE="200"           # Requests per second (QPS)
TARGETS_FILE="targets.txt"
RESULTS_FILE="results.bin"
REPORT_FILE="report.txt"
PLOT_FILE="plot.html"

# UUID for the pre-registered device and user
USER_UUID="f6e47d7e-a802-4a81-9106-b67e969a7003"
DEVICE_UUID="0361ab50-54f0-4a64-b5f1-bae2305bc8da"

# Prepare the targets file with the necessary endpoints and payloads
cat <<EOF > $TARGETS_FILE
GET $BASE_URL/api/v1/users

GET $BASE_URL/api/v1/users/$USER_UUID

GET $BASE_URL/api/v1/devices

POST $BASE_URL/api/v1/devices/$DEVICE_UUID/locations
Content-Type: application/json
@update_location.json

GET $BASE_URL/api/v1/devices/$DEVICE_UUID/location

GET $BASE_URL/api/v1/devices/$DEVICE_UUID
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

