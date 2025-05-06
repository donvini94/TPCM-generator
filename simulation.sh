#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="PCMs/"
DOCKER_IMAGE="registry.dumusstbereitsein.de/palladio_runtime:latest"

# Get number of available CPU cores
NUM_CORES=$(nproc)
echo "Detected $NUM_CORES CPU cores, will launch $NUM_CORES parallel containers"

# Create a temporary directory for splitting tasks
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Find all experiment directories
ALL_DIRS=()
for exp_dir in "$BASE_DIR"/*; do
  if [ -d "$exp_dir/model-gen" ]; then
    ALL_DIRS+=("$exp_dir")
  fi
done

TOTAL_DIRS=${#ALL_DIRS[@]}
echo "Found $TOTAL_DIRS experiment directories to process"

if [ $TOTAL_DIRS -eq 0 ]; then
  echo "No experiment directories found in $BASE_DIR. Exiting."
  exit 0
fi

# Calculate directories per core (at least 1)
DIRS_PER_CORE=$(((TOTAL_DIRS + NUM_CORES - 1) / NUM_CORES))
if [ $DIRS_PER_CORE -lt 1 ]; then
  DIRS_PER_CORE=1
fi

echo "Each core will process approximately $DIRS_PER_CORE directories"

# Create task lists for each core
for ((i = 0; i < NUM_CORES; i++)); do
  START_INDEX=$((i * DIRS_PER_CORE))
  if [ $START_INDEX -ge $TOTAL_DIRS ]; then
    break # No more directories to process
  fi

  # Calculate end index (exclusive)
  END_INDEX=$((START_INDEX + DIRS_PER_CORE))
  if [ $END_INDEX -gt $TOTAL_DIRS ]; then
    END_INDEX=$TOTAL_DIRS
  fi

  # Create task file for this core
  TASK_FILE="$TEMP_DIR/task_$i.txt"
  for ((j = START_INDEX; j < END_INDEX; j++)); do
    echo "${ALL_DIRS[$j]}" >>"$TASK_FILE"
  done

  echo "Core $i will process $((END_INDEX - START_INDEX)) directories"
done

# Function to process a task file in a container
process_task_file() {
  local task_file=$1
  local core_id=$2

  echo "Starting container for core $core_id to process $(wc -l <"$task_file") directories"

  # Process each directory in the task file
  while IFS= read -r exp_dir; do
    echo "[$core_id] Processing experiment in $exp_dir"

    mkdir -p "$exp_dir/results"

    ABS_MODEL_DIR=$(realpath "$exp_dir/model-gen")
    ABS_RESULTS_DIR=$(realpath "$exp_dir/results")

    # Generate a unique container name based on directory and core ID
    CONTAINER_NAME="palladio-simulation-$(basename "$exp_dir")-core$core_id"

    # Run the container
    container_id=$(
      docker run -d \
        --name "$CONTAINER_NAME" \
        -v "$ABS_MODEL_DIR":/tmp/modeldata \
        -v "$ABS_RESULTS_DIR":/result \
        "$DOCKER_IMAGE" \
        bash -c '
              # Copy all files from the mounted modeldata folder.
              cp -r /tmp/modeldata/* /usr/ExperimentData/model/

              allocation_file=$(ls /usr/ExperimentData/model | grep "^allocation_.*\.allocation$")
              usage_file=$(ls /usr/ExperimentData/model | grep "^usage_.*\.usagemodel$")
              env_file=$(ls /usr/ExperimentData/model | grep "^Environment_.*\.resourceenvironment$")

              echo "Found allocation file: $allocation_file"
              echo "Found usage file: $usage_file"
              echo "Found resource environment file: $env_file"

              new_allocation_id=$(sed -n "2s/.*id=\"\\([^\"]*\\)\".*/\\1/p" /usr/ExperimentData/model/"$allocation_file")
              echo "New allocation ID: $new_allocation_id"

              new_resource_id=$(sed -n "4s/.*id=\"\\([^\"]*\\)\".*/\\1/p" /usr/ExperimentData/model/"$env_file")
              echo "New resource ID: $new_resource_id"

              new_usage_id=$(sed -n "3s/.*id=\"\\([^\"]*\\)\".*/\\1/p" /usr/ExperimentData/model/"$usage_file")
              echo "New usage ID: $new_usage_id"

              GENERATED="/usr/ExperimentData/model/Experiments/Generated.experiments"
              MEASURINGPOINT="/usr/ExperimentData/model/measuring2.measuringpoint"

              # Update references in Generated.experiments
              sed -i "s|\(<usageModel href=\"\)[^\"]*\(\"\s*/>\)|\1../$usage_file#/\2|g" "$GENERATED"
              sed -i "s|\(<allocation href=\"\)[^\"]*\(\"\s*/>\)|\1../$allocation_file#$new_allocation_id\2|g" "$GENERATED"

              # Update measuring2.measuringpoint
              sed -i "3s|resourceURIRepresentation=\"[^\"]*\"|resourceURIRepresentation=\"$env_file#$new_resource_id\"|" "$MEASURINGPOINT"
              sed -i "4s|href=\"[^\"]*\"|href=\"$env_file#$new_resource_id\"|" "$MEASURINGPOINT"
              sed -i "6s|resourceURIRepresentation=\"[^\"]*\"|resourceURIRepresentation=\"$usage_file#$new_usage_id\"|" "$MEASURINGPOINT"
              sed -i "7s|href=\"[^\"]*\"|href=\"$usage_file#$new_usage_id\"|" "$MEASURINGPOINT"

              # Run the simulation
              /usr/RunExperimentAutomation.sh

              echo "Simulation complete. Results available in /result"
            '
    )

    echo "[$core_id] Launched container: $container_id"

    # Wait for the container to finish with timeout
    if ! timeout 60s docker wait "$container_id"; then
      echo "[$core_id] Container $container_id took too long. Killing..."
      docker kill "$container_id" || true
    fi

    # Clean up container
    docker rm "$container_id" >/dev/null 2>&1 || true

  done <"$task_file"

  echo "Core $core_id finished processing all assigned directories"
}

# Launch containers in parallel
echo "Launching $NUM_CORES parallel container groups..."
for ((i = 0; i < NUM_CORES; i++)); do
  TASK_FILE="$TEMP_DIR/task_$i.txt"
  if [ -f "$TASK_FILE" ]; then
    # Process each task file in a background subprocess
    process_task_file "$TASK_FILE" "$i" &
    PIDS[$i]=$!
  fi
done

# Wait for all processes to complete
echo "Waiting for all container groups to complete..."
for pid in "${PIDS[@]}"; do
  wait $pid
done

echo "All simulations completed"
