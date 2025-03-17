#!/bin/bash

# Create input and output directories if they don't exist
mkdir -p input output

# Generate unique container names using a timestamp
TIMESTAMP=$(date +%Y%m%d%H%M%S)
TPCM_GENERATOR_NAME="tpcm-generator-$TIMESTAMP"
TPCM2PCM_NAME="tpcm2pcm-$TIMESTAMP"

# Step 1: Run the tpcm-generator container
echo "Starting tpcm-generator container ($TPCM_GENERATOR_NAME)..."
docker run -v ./input:/tpcm-generator/input --name $TPCM_GENERATOR_NAME registry.dumusstbereitsein.de/tpcm-generator > tpcm-generator.log 2>&1

# Check if the tpcm-generator container completed successfully
if [ $? -eq 0 ]; then
  echo "tpcm-generator container ($TPCM_GENERATOR_NAME) finished successfully."

  # Step 2: Run the tpcm2pcm container in the background
  echo "Starting tpcm2pcm container ($TPCM2PCM_NAME)..."
  docker run -v ./input:/usr/eclipse/shared -v ./output:/usr/eclipse/workspace --name $TPCM2PCM_NAME registry.dumusstbereitsein.de/tpcm2pcm > tpcm2pcm.log 2>&1 &
  CONTAINER_PID=$!

  # Timeout period (in seconds) to wait for no output
  TIMEOUT=30
  LAST_LOG_SIZE=$(stat -c%s tpcm2pcm.log)

  # Monitor the log file for changes
  echo "Monitoring tpcm2pcm container ($TPCM2PCM_NAME) for inactivity..."
  while true; do
    sleep 5

    # Check if the container process is still running
    if ! ps -p $CONTAINER_PID > /dev/null; then
      echo "tpcm2pcm container ($TPCM2PCM_NAME) process has stopped."
      break
    fi

    # Check if the log file has grown
    CURRENT_LOG_SIZE=$(stat -c%s tpcm2pcm.log)
    if [ $CURRENT_LOG_SIZE -gt $LAST_LOG_SIZE ]; then
      # Log file has grown, reset the timeout
      LAST_LOG_SIZE=$CURRENT_LOG_SIZE
    else
      # Log file has not grown, decrement the timeout
      TIMEOUT=$((TIMEOUT - 5))
      if [ $TIMEOUT -le 0 ]; then
        echo "No output detected for 30 seconds. Stopping tpcm2pcm container ($TPCM2PCM_NAME)..."
        docker stop $TPCM2PCM_NAME > /dev/null
        break
      fi
    fi
  done

  # Check if the tpcm2pcm container completed successfully
  if docker inspect -f '{{.State.ExitCode}}' $TPCM2PCM_NAME | grep -q '0'; then
    echo "tpcm2pcm container ($TPCM2PCM_NAME) finished successfully."
  else
    echo "Error: tpcm2pcm container ($TPCM2PCM_NAME) failed or was stopped."
    exit 1
  fi
else
  echo "Error: tpcm-generator container ($TPCM_GENERATOR_NAME) failed."
  exit 1
fi

# Cleanup: Remove containers
docker rm $TPCM_GENERATOR_NAME $TPCM2PCM_NAME > /dev/null
