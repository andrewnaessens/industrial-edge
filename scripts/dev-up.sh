#!/bin/bash

# Industrial Edge: Inner Loop Launcher
# This script runs the containerised vitals service with local code mounted

# Move to the directory where the script lives, then go up one level to the root
PARENT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P)
cd "$PARENT_PATH/.."

echo "Launching Industrial Edge Development Sandbox..."

# Ensure we are running from the project root
if [ ! -f "Containerfile.dev" ]; then
    echo "Error: Please run this script from the project root directory."
    exit 1
fi

# Run the container:
# --rm: Deletes container after exit
# -it: Interactive terminal for logs
# --env-file: Inject HiveMQ secrets
# -v: Mount local code (z flag handles SELinux/Podman permissions)
podman run --rm -it \
    --name industrial-edge-vitals-dev \
    --env-file .env \
    -e RPI_LGPIO_REVISION=c03111 \
    -e GPIOZERO_PIN_FACTORY=lgpio \
    --device /dev/gpiomem:/dev/gpiomem \
    --device /dev/gpiochip0:/dev/gpiochip0 \
    --device /dev/i2c-1:/dev/i2c-1 \
    -v "$(pwd):/app:z" \
    industrial-edge-dev
