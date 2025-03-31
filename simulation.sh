#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="PCMs/"
DOCKER_IMAGE="registry.dumusstbereitsein.de/palladio_runtime:latest"

for exp_dir in "$BASE_DIR"/*; do
        if [ -d "$exp_dir/model-gen" ]; then
                echo "Processing experiment in $exp_dir"

                mkdir -p "$exp_dir/results"

                ABS_MODEL_DIR=$(realpath "$exp_dir/model-gen")
                ABS_RESULTS_DIR=$(realpath "$exp_dir/results")

                # Run the container in the background (detached).
                container_id=$(
                        docker run -d \
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

              echo "Updated Generated.experiments:"
              cat "$GENERATED"
              echo "------------------------------------"
              echo "Updated measuring2.measuringpoint:"
              cat "$MEASURINGPOINT"
              echo "------------------------------------"

              # Run the simulation
              /usr/RunExperimentAutomation.sh

              echo "Simulation complete. Results available in /result"
            '
                )

                echo "Launched container: $container_id"

                # Wait for the container to finish, but wrap in a timeout.
                # If it doesn't exit within, say, 1 minutes (60 seconds), we kill it.
                if ! timeout 60s docker wait "$container_id"; then
                        echo "Container $container_id took too long. Killing..."
                        docker kill "$container_id" || true
                fi

                # Clean up container
                docker rm "$container_id" >/dev/null 2>&1 || true
        fi
done
