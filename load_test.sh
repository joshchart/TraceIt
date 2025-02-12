# Load environment variables
source .env

# Configuration
DURATION="30s"        # Duration of the test
RATE="200"           # Requests per second (QPS)
TIMEOUT="30s"         # Timeout for each request
TARGETS_FILE="targets.txt"
RESULTS_FILE="results.bin"
REPORT_FILE="report.txt"
PLOT_FILE="plot.html"

# UUID for the pre-registered user and device
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

# Function to run Vegeta attack with a specific rate
run_vegeta_attack() {
  local rate=$1
  local duration=$2
  local timeout=$3
  local targets_file=$4
  local results_file=$5
  local report_file=$6
  local plot_file=$7

  echo "Running Vegeta with $rate requests per second for $duration and timeout of $timeout..."
  vegeta attack -duration=$duration -rate=$rate -timeout=$timeout -targets=$targets_file | tee $results_file | vegeta report -type=text > $report_file

  # Generate a plot report
  cat $results_file | vegeta plot > $plot_file

  echo "Load test completed. Results:"
  cat $report_file
  echo "Plot report generated at $plot_file"
}

# Incremental load testing
for rate in 50 100 200; do
  echo "Testing with rate: $rate"
  run_vegeta_attack $rate $DURATION $TIMEOUT $TARGETS_FILE $RESULTS_FILE $REPORT_FILE $PLOT_FILE
done

