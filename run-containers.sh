#!/bin/bash

# Step 1: Run the tpcm-generator container
echo "Starting tpcm-generator container..."
docker run -v ./input:/tpcm-generator/input --name tpcm-generator tpcm-generator

# Check if the tpcm-generator container completed successfully
if [ $? -eq 0 ]; then
  echo "tpcm-generator container finished successfully."

  # Step 2: Run the tpcm2pcm container
  echo "Starting tpcm2pcm container..."
  docker run -v ./input:/usr/eclipse/shared -v ./output:/usr/eclipse/workspace --name tpcm2pcm registry.dumusstbereitsein.de/tpcm2pcm

  # Check if the tpcm2pcm container completed successfully
  if [ $? -eq 0 ]; then
    echo "tpcm2pcm container finished successfully."
  else
    echo "Error: tpcm2pcm container failed."
    exit 1
  fi
else
  echo "Error: tpcm-generator container failed."
  exit 1
fi
