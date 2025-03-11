podman build -t tpcm-generator .
podman run -it --rm --name tpcm-generator -v output:/tpcm-generator/input tpcm-generator