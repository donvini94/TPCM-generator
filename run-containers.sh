#!/bin/bash
set -euo pipefail

# Create input and output directories if they don't exist
mkdir -p input output

# Get number of available CPU cores
NUM_CORES=$(nproc)
echo "Detected $NUM_CORES CPU cores, will launch $NUM_CORES parallel containers"

# Create temporary directory for task distribution
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Step 1: Run the tpcm-generator container once to generate all TPCM files
TIMESTAMP=$(date +%Y%m%d%H%M%S)
TPCM_GENERATOR_NAME="tpcm-generator-$TIMESTAMP"

echo "Starting tpcm-generator container ($TPCM_GENERATOR_NAME)..."
docker run -v ./input:/tpcm-generator/input --name $TPCM_GENERATOR_NAME registry.dumusstbereitsein.de/tpcm-generator > tpcm-generator.log 2>&1

# Check if the tpcm-generator container completed successfully
if [ $? -ne 0 ]; then
  echo "Error: tpcm-generator container ($TPCM_GENERATOR_NAME) failed."
  docker rm $TPCM_GENERATOR_NAME > /dev/null 2>&1 || true
  exit 1
fi

echo "tpcm-generator container ($TPCM_GENERATOR_NAME) finished successfully."
docker rm $TPCM_GENERATOR_NAME > /dev/null 2>&1 || true

# Find all TPCM files in input directory
TPCM_FILES=()
while IFS= read -r file; do
  TPCM_FILES+=("$file")
done < <(find ./input -name "*.tpcm" -type f | sort)

TOTAL_FILES=${#TPCM_FILES[@]}
echo "Found $TOTAL_FILES TPCM files to convert"

if [ $TOTAL_FILES -eq 0 ]; then
  echo "No TPCM files found in input directory. Exiting."
  exit 0
fi

# Calculate files per core (at least 1)
FILES_PER_CORE=$(( (TOTAL_FILES + NUM_CORES - 1) / NUM_CORES ))
if [ $FILES_PER_CORE -lt 1 ]; then
  FILES_PER_CORE=1
fi

echo "Each core will process approximately $FILES_PER_CORE files"

# Create task lists for each core
for ((i=0; i<NUM_CORES; i++)); do
  START_INDEX=$((i * FILES_PER_CORE))
  if [ $START_INDEX -ge $TOTAL_FILES ]; then
    break  # No more files to process
  fi
  
  # Calculate end index (exclusive)
  END_INDEX=$((START_INDEX + FILES_PER_CORE))
  if [ $END_INDEX -gt $TOTAL_FILES ]; then
    END_INDEX=$TOTAL_FILES
  fi
  
  # Create task file for this core
  TASK_FILE="$TEMP_DIR/tpcm_task_$i.txt"
  for ((j=START_INDEX; j<END_INDEX; j++)); do
    echo "${TPCM_FILES[$j]}" >> "$TASK_FILE"
  done
  
  echo "Core $i will process $((END_INDEX - START_INDEX)) TPCM files"
done

# Function to process a batch of TPCM files
process_tpcm_files() {
  local task_file=$1
  local core_id=$2
  
  echo "[$core_id] Starting tpcm2pcm container to process $(wc -l < "$task_file") files"
  
  # Create core-specific output directory
  CORE_OUTPUT_DIR="./output/core_$core_id"
  mkdir -p "$CORE_OUTPUT_DIR"
  
  # Create a temporary working directory for this core
  CORE_INPUT_DIR="$TEMP_DIR/input_$core_id"
  mkdir -p "$CORE_INPUT_DIR"
  
  # Copy all TPCM files from the task list to core's input directory
  while IFS= read -r tpcm_file; do
    cp "$tpcm_file" "$CORE_INPUT_DIR/"
  done < "$task_file"
  
  # Generate a unique container name for this core
  TPCM2PCM_NAME="tpcm2pcm-core$core_id-$TIMESTAMP"
  
  # Run the tpcm2pcm container
  echo "[$core_id] Starting tpcm2pcm container ($TPCM2PCM_NAME)..."
  docker run -v "$CORE_INPUT_DIR":/usr/eclipse/shared \
             -v "$CORE_OUTPUT_DIR":/usr/eclipse/workspace \
             --name "$TPCM2PCM_NAME" \
             registry.dumusstbereitsein.de/tpcm2pcm > "$TEMP_DIR/tpcm2pcm_$core_id.log" 2>&1
  
  CONTAINER_EXIT_CODE=$?
  
  # Check if the container completed successfully
  if [ $CONTAINER_EXIT_CODE -eq 0 ]; then
    echo "[$core_id] tpcm2pcm container ($TPCM2PCM_NAME) finished successfully."
    
    # Move files from core-specific output to main output
    find "$CORE_OUTPUT_DIR" -type f -name "*.repository" -o -name "*.system" -o -name "*.resourceenvironment" -o -name "*.allocation" -o -name "*.usagemodel" -o -name "*.xmi" | while read -r file; do
      mv "$file" "./output/"
    done
    
  else
    echo "[$core_id] Error: tpcm2pcm container ($TPCM2PCM_NAME) failed with exit code $CONTAINER_EXIT_CODE."
  fi
  
  # Cleanup container
  docker rm "$TPCM2PCM_NAME" > /dev/null 2>&1 || true
  
  echo "[$core_id] Completed processing assigned TPCM files"
}

# Launch tpcm2pcm containers in parallel
echo "Launching $NUM_CORES parallel tpcm2pcm containers..."
PIDS=()
for ((i=0; i<NUM_CORES; i++)); do
  TASK_FILE="$TEMP_DIR/tpcm_task_$i.txt"
  if [ -f "$TASK_FILE" ]; then
    # Process each task file in a background subprocess
    process_tpcm_files "$TASK_FILE" "$i" &
    PIDS[$i]=$!
  fi
done

# Wait for all containers to complete
echo "Waiting for all tpcm2pcm containers to complete..."
for pid in "${PIDS[@]}"; do
  wait $pid
done

echo "All TPCM files have been processed and converted to PCM files"
echo "Results are available in the output directory"