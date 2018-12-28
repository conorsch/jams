#!/bin/bash
# Container entrypoint script for running the Jams REPL.
# Dynamically generates assets if not found; assumes container will be run
# with local asset dir volume-mounted into container.
set -e
set -u
set -o pipefail

# Generate WAV files for use in script
if [[ "$(find /code/assets -type f -iname '*.wav' | wc -l )" = "0" ]]; then
    mkdir -p /code/assets
    cd /code
    python jams.py --generate
fi

# Run REPL
ipython3 --no-banner --no-confirm-exit -i jams.py
